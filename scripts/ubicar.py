"""Ubica cada ataque en el mapa → data/processed/ataques_ubicados.csv y distritos_lima.geojson.

Dos niveles de precisión (D-12):
  "lugar"     se encontró una vía o lugar (avenida, jirón, paradero, óvalo…) en el titular o en el
              texto archivado de la nota, Nominatim (OpenStreetMap) lo ubicó y el punto cae DENTRO del
              distrito del ataque. Si el ataque tiene rutas candidatas, además debe quedar a ≤1 km de una
              de ellas. Sin distrito, se acepta solo a ≤500 m de una ruta candidata. Para una avenida, el
              punto es un tramo de ella dentro del distrito: aproximado (error de hasta ~1-2 km).
  "distrito"  solo se sabe el distrito: el punto es el centro del distrito (en el mapa va como círculo
              agregado, nunca como punto exacto).
  ""          sin distrito ni lugar: no se dibuja.

Nominatim: gratis, máximo 1 consulta por segundo (se usa 1.1 s), sin datos personales (solo el lugar y
el distrito). Las respuestas se guardan en data/processed/geocache.json: cada consulta se hace una sola
vez y las corridas siguientes solo preguntan lo nuevo. --sin-red usa solo la caché.

Límites distritales: data/raw/limites/peru_distrital_simple.geojson (github.com/juaneladio/peru-geojson,
MPL-2.0). Solo Python estándar + curl: python3 -I scripts/ubicar.py
"""
import csv
import json
import math
import pathlib
import re
import subprocess
import sys
import time
import unicodedata
import urllib.parse

RAIZ = pathlib.Path(__file__).resolve().parent.parent
P = RAIZ / "data" / "processed"
LIMITES = RAIZ / "data" / "raw" / "limites" / "peru_distrital_simple.geojson"
CACHE = P / "geocache.json"
UA = "mapa-crimen/0.1 (proyecto de datos abiertos; uso bajo)"
PAUSA = 1.1
MAX_CONSULTAS = 400
MAX_DIST_RUTA = 1000  # m: un lugar más lejos de todas sus rutas candidatas se descarta  # tope por corrida, por cortesía con el servicio
LIMA_VIEWBOX = "-77.25,-11.55,-76.60,-12.55"  # lon1,lat1,lon2,lat2
ALIAS = {"CERCADO DE LIMA": "LIMA", "LURIGANCHO-CHOSICA": "LURIGANCHO", "PUEBLO LIBRE": "MAGDALENA VIEJA",
         "BRENA": "BRENA"}
NOMBRE_MAPA = {"MAGDALENA VIEJA": "Pueblo Libre", "LIMA": "Cercado de Lima", "LURIGANCHO": "Lurigancho-Chosica"}

TIPO = (r"(?i:avenida|av\.|jir[oó]n|jr\.|calle|carretera|autopista|v[ií]a expresa|[oó]valo|puente|paradero|"
        r"pasaje|prolongaci[oó]n|alameda|malec[oó]n|plaza|mercado|urbanizaci[oó]n|urb\.|"
        r"asentamiento humano|aa\.?\s?hh\.?|cooperativa|parque|panamericana(?: norte| sur)?|"
        r"carretera central|ramiro pr[ií]al[eé])")
# el nombre empieza con mayúscula o número (sin re.I: así no se cuela "en medio de…")
NOMBRE = r"((?:(?:de|del|la|las|los|el|y)\s+)*(?:[A-ZÁÉÍÓÚÑ0-9][\wÁÉÍÓÚÑáéíóúñ'’-]*\.?\s*){1,5})"
LUGAR = re.compile(rf"\b({TIPO})\s+{NOMBRE}")
# vías de muchos km: decir solo "en la Panamericana" no ubica el ataque
SIN_NOMBRE = {"panamericana", "panamericana norte", "panamericana sur", "carretera central", "ramiro prialé",
              "ramiro priale", "vía expresa", "via expresa"}
NO_LUGAR = {"PUENTE PIEDRA", "SJL", "VES", "SMP", "LIMA", "CALLAO"}


def norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper().strip()


# ---------- geometría ----------
def anillos(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    return geom["coordinates"]  # MultiPolygon


def dentro(lon, lat, geom):
    for poly in anillos(geom):
        ext, *huecos = poly
        if _en_anillo(lon, lat, ext) and not any(_en_anillo(lon, lat, h) for h in huecos):
            return True
    return False


def _en_anillo(x, y, r):
    c = False
    for (x1, y1), (x2, y2) in zip(r, r[1:] + r[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def centro(geom):
    """Centroide del polígono más grande; si cae fuera (forma rara), el vértice medio."""
    mejor, area_max = None, 0
    for poly in anillos(geom):
        r = poly[0]
        a = cx = cy = 0
        for (x1, y1), (x2, y2) in zip(r, r[1:] + r[:1]):
            k = x1 * y2 - x2 * y1
            a += k
            cx += (x1 + x2) * k
            cy += (y1 + y2) * k
        if abs(a) > area_max:
            area_max, mejor = abs(a), (cx / (3 * a), cy / (3 * a), r)
    x, y, r = mejor
    if not dentro(x, y, geom):
        x, y = r[len(r) // 2]
    return round(x, 5), round(y, 5)


def dist_m(lon1, lat1, lon2, lat2):
    kx = 111320 * math.cos(math.radians((lat1 + lat2) / 2))
    return math.hypot((lon1 - lon2) * kx, (lat1 - lat2) * 110540)


def dist_a_ruta(lon, lat, lineas):
    mejor = float("inf")
    kx = 111320 * math.cos(math.radians(lat))
    for l in lineas:
        for (x1, y1), (x2, y2) in zip(l, l[1:]):
            ax, ay = (x1 - lon) * kx, (y1 - lat) * 110540
            bx, by = (x2 - lon) * kx, (y2 - lat) * 110540
            dx, dy = bx - ax, by - ay
            t = 0 if dx == dy == 0 else max(0, min(1, -(ax * dx + ay * dy) / (dx * dx + dy * dy)))
            mejor = min(mejor, math.hypot(ax + t * dx, ay + t * dy))
    return mejor


# ---------- textos ----------
def lugares(texto):
    """Vías o lugares nombrados en el texto, en orden de aparición, sin repetir."""
    vistos, out = set(), []
    for m in LUGAR.finditer(texto):
        tipo, nombre = m.group(1).strip(), m.group(2)
        nombre = re.split(r"\.\s", nombre)[0].strip(" .,'’")  # corta en el punto seguido
        nombre = re.sub(r"\s+(?:de|del|la|las|los|el|y)$", "", nombre)
        tipo_l = tipo.lower()
        if tipo_l in SIN_NOMBRE or norm(f"{tipo} {nombre}") in {norm(x) for x in SIN_NOMBRE} | NO_LUGAR or norm(nombre) in NO_LUGAR:
            continue
        if len(nombre) < 3 or nombre.isdigit():
            continue
        if any(norm(nombre).startswith(x) for x in ("SAN JUAN DE", "VILLA EL", "VILLA MARIA")):
            continue  # es un distrito, no un lugar
        tipo_n = {"av.": "Avenida", "jr.": "Jirón", "urb.": "Urbanización"}.get(tipo_l, tipo.capitalize())
        lugar = f"{tipo_n} {nombre}"
        clave = norm(lugar)
        if clave not in vistos:
            vistos.add(clave)
            out.append(lugar)
    return out


def textos_por_ataque():
    """Para cada URL de Google Noticias: título + inicio del texto archivado (si lo hay)."""
    guid_de_url, titulo = {}, {}
    for l in (RAIZ / "data" / "raw" / "noticias.jsonl").open(encoding="utf-8"):
        n = json.loads(l)
        guid_de_url[n["url"]] = n["guid"]
        titulo[n["url"]] = n["titulo"]
    id_de_guid = {}
    archivo = RAIZ / "data" / "raw" / "archivo.jsonl"
    if archivo.exists():
        for l in archivo.open(encoding="utf-8"):
            e = json.loads(l)
            if e.get("texto") == "ok":
                id_de_guid[e["guid"]] = e["id"]

    def textos(urls):
        out, con_texto = [], 0
        for u in urls:
            out.append(titulo.get(u, ""))
            nid = id_de_guid.get(guid_de_url.get(u))
            f = RAIZ / "data" / "raw" / "articulos" / f"{nid}.json"
            if nid and f.exists():
                out.append(json.loads(f.read_text(encoding="utf-8"))["texto"][:1500])  # el lugar suele ir al inicio
                con_texto += 1
        return out, con_texto
    return textos


# ---------- Nominatim ----------
def geocodificar(consulta, cache, estado):
    if consulta in cache:
        return cache[consulta]
    if estado["sin_red"] or estado["consultas"] >= MAX_CONSULTAS:
        return None
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": consulta, "format": "jsonv2", "limit": 3, "countrycodes": "pe",
         "viewbox": LIMA_VIEWBOX, "bounded": 1})
    time.sleep(PAUSA)
    estado["consultas"] += 1
    r = subprocess.run(["curl", "-s", "-m", "20", "-A", UA, url], capture_output=True, text=True)
    try:
        res = [{"lat": float(x["lat"]), "lon": float(x["lon"]), "nombre": x.get("display_name", "")[:120]}
               for x in json.loads(r.stdout)]
    except (ValueError, KeyError):
        return None  # error de red o límite: no se guarda, se reintenta otra vez
    cache[consulta] = res
    return res


def main():
    estado = {"sin_red": "--sin-red" in sys.argv, "consultas": 0}
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    geo = json.loads(LIMITES.read_text(encoding="utf-8"))
    distritos = {norm(f["properties"]["NOMBDIST"]): f for f in geo["features"]
                 if f["properties"]["NOMBPROV"] in ("LIMA", "CALLAO")}
    centros = {}
    for k, f in distritos.items():
        if f["geometry"]:
            centros[k] = centro(f["geometry"])
        else:  # La Punta y Santa Anita vienen sin polígono en la fuente (P-11)
            res = geocodificar(f"Distrito de {f['properties']['NOMBDIST'].title()}, Lima, Perú", cache, estado) or []
            if res:
                centros[k] = (round(res[0]["lon"], 5), round(res[0]["lat"], 5))

    def en_distrito(lon, lat, k):
        g = distritos[k]["geometry"]
        if g:
            return dentro(lon, lat, g)
        return k in centros and dist_m(lon, lat, *centros[k]) <= 3000
    rutas = {}
    for f in json.loads((P / "rutas_trazados.geojson").read_text(encoding="utf-8"))["features"]:
        rutas.setdefault(f["properties"]["ruta"], []).extend(f["geometry"]["coordinates"])
    textos = textos_por_ataque()

    filas, n_texto = [], 0
    for a in csv.DictReader((P / "ataques.csv").open(encoding="utf-8")):
        d = norm(a["distrito"])
        d = ALIAS.get(d, d)
        fila = {"id": a["id"], "fecha": a["fecha"], "distrito": a["distrito"], "lat": "", "lon": "",
                "precision": "", "lugar": "", "dist_ruta_m": "", "codigos_ruta": a["codigos_ruta"],
                "empresa": a["empresa"], "roles": a["roles"], "hubo_muerte": a["hubo_muerte"],
                "n_notas": a["n_notas"], "urls": a["urls"]}
        ts, con_texto = textos(a["urls"].split())
        n_texto += con_texto > 0
        if d in centros:
            fila["lon"], fila["lat"] = centros[d]
            fila["precision"] = "distrito"
            nom_d = NOMBRE_MAPA.get(d, a["distrito"])
            for lugar in lugares(" \n".join(ts))[:4]:
                res = geocodificar(f"{lugar}, {nom_d}, Lima, Perú", cache, estado) or []
                ok = [r for r in res if en_distrito(r["lon"], r["lat"], d)]
                cods = [c for c in a["codigos_ruta"].split() if c in rutas]
                elegido = None
                for r in ok:
                    dm = min(dist_a_ruta(r["lon"], r["lat"], rutas[c]) for c in cods) if cods else None
                    if dm is None or dm <= MAX_DIST_RUTA:  # con ruta: el lugar debe quedar cerca de ella
                        elegido = (r, dm)
                        break
                if elegido:
                    r, dm = elegido
                    fila.update(lat=round(r["lat"], 5), lon=round(r["lon"], 5), precision="lugar", lugar=lugar,
                                dist_ruta_m="" if dm is None else round(dm))
                    break
        elif a["codigos_ruta"].strip():
            # sin distrito: se acepta el lugar solo si cae a ≤500 m de una de sus rutas candidatas
            cods = [c for c in a["codigos_ruta"].split() if c in rutas]
            for lugar in lugares(" \n".join(ts))[:4] if cods else []:
                res = geocodificar(f"{lugar}, Lima, Perú", cache, estado) or []
                for r in res:
                    dm = min(dist_a_ruta(r["lon"], r["lat"], rutas[c]) for c in cods)
                    if dm <= 500:  # más estricto: sin distrito no hay otro control
                        fila.update(lat=round(r["lat"], 5), lon=round(r["lon"], 5), precision="lugar",
                                    lugar=lugar, dist_ruta_m=round(dm))
                        break
                if fila["precision"]:
                    break
        filas.append(fila)

    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
    with (P / "ataques_ubicados.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    feats = [{"type": "Feature", "properties": {"distrito": NOMBRE_MAPA.get(k, f["properties"]["NOMBDIST"].title()),
                                                "clave": k, "centro": centros[k]},
              "geometry": f["geometry"]} for k, f in sorted(distritos.items()) if k in centros]
    (P / "distritos_lima.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": feats},
                                                         ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    prec = {k: sum(f["precision"] == k for f in filas) for k in ("lugar", "distrito", "")}
    cerca = sum(1 for f in filas if f["dist_ruta_m"] != "" and f["dist_ruta_m"] <= 500)
    con_ruta = sum(1 for f in filas if f["dist_ruta_m"] != "")
    print(f"{len(filas)} ataques: {prec['lugar']} con lugar, {prec['distrito']} solo distrito, "
          f"{prec['']} sin ubicar; {n_texto} con texto archivado; {estado['consultas']} consultas nuevas a "
          f"Nominatim; lugar a ≤500 m de su ruta: {cerca} de {con_ruta}")


if __name__ == "__main__":
    main()
