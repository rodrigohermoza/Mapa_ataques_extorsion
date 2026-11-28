"""Trazados oficiales de la ATU (respuesta SAIP del 24-nov-2026) → GeoJSON + tabla de rutas.

Entradas (data/raw/atu/):
  rutas_autorizadas_2026-11-05_shp.zip  shapefile de polilíneas, 890 registros (445 rutas × ida/vuelta).
      El .prj dice UTM 18N, pero los northing son negativos: en realidad es UTM 18S sin el
      falso norte de 10 000 km. Se suma y se convierte a lat/lon WGS84 aquí mismo (sin pyproj).
  relacion_rutas_2026.csv               hoja del Excel de la ATU (ruta, RUC, operador, flota).
      Si está el .xlsx (fuera de git porque sus metadatos traen nombres de funcionarios), se
      vuelve a exportar a este CSV.

Salidas:
  data/processed/rutas_trazados.geojson  una línea por ruta y sentido, simplificada (~5 m).
  data/processed/rutas_oficiales.csv     una fila por ruta con los atributos y el RUC.

Solo Python estándar: python3 -I scripts/trazados_atu.py
"""
import csv
import io
import json
import math
import pathlib
import re
import struct
import zipfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ATU = RAIZ / "data" / "raw" / "atu"
SHP_ZIP = ATU / "rutas_autorizadas_2026-11-05_shp.zip"
XLSX = ATU / "relacion_rutas_2026.xlsx"
XCSV = ATU / "relacion_rutas_2026.csv"
GEOJSON = RAIZ / "data" / "processed" / "rutas_trazados.geojson"
SALIDA = RAIZ / "data" / "processed" / "rutas_oficiales.csv"
TOLERANCIA_M = 5.0   # simplificación Douglas-Peucker
DECIMALES = 5        # ~1 m en lat/lon


# ---------- lectura del shapefile ----------
CORRECCIONES = str.maketrans({"Ð": "Ñ", "ð": "Ñ", "Ë": "Ó"})  # MARAÐON, JIRËN (cp850 mal leído)


def arreglar(texto):
    """Corrige la codificación mezclada del DBF: UTF-8 leído como latin-1 ("NÂ°" → "N°")
    y algunas letras de otra página de códigos."""
    texto = texto.replace("\u00e2\u0080\u0093", "–")
    if re.search("[ÂÃ]", texto):
        try:
            texto = texto.encode("latin-1").decode("utf-8")
        except UnicodeError:
            pass
    return texto.translate(CORRECCIONES)


def leer_dbf(datos):
    n, largo_cab, largo_reg = struct.unpack("<IHH", datos[4:12])
    campos, p = [], 32
    while datos[p] != 0x0D:
        campos.append((datos[p:p + 11].split(b"\0")[0].decode(), datos[p + 16]))
        p += 32
    filas = []
    for i in range(n):
        r = datos[largo_cab + i * largo_reg: largo_cab + (i + 1) * largo_reg]
        q, fila = 1, {}
        for nombre, largo in campos:
            fila[nombre] = arreglar(r[q:q + largo].decode("latin-1").strip())
            q += largo
        filas.append(fila)
    return filas


def leer_shp(datos):
    """Polilíneas (tipo 3) → lista de registros, cada uno lista de partes [(x, y), ...]."""
    assert struct.unpack("<i", datos[32:36])[0] == 3, "se esperaba polilínea"
    p, regs = 100, []
    while p < len(datos):
        largo = struct.unpack(">i", datos[p + 4:p + 8])[0] * 2
        c = datos[p + 8:p + 8 + largo]
        p += 8 + largo
        if struct.unpack("<i", c[:4])[0] == 0:  # nulo
            regs.append([])
            continue
        npartes, npuntos = struct.unpack("<ii", c[36:44])
        ini = list(struct.unpack(f"<{npartes}i", c[44:44 + 4 * npartes])) + [npuntos]
        pts = struct.unpack(f"<{2 * npuntos}d", c[44 + 4 * npartes:44 + 4 * npartes + 16 * npuntos])
        xy = list(zip(pts[0::2], pts[1::2]))
        regs.append([xy[ini[k]:ini[k + 1]] for k in range(npartes)])
    return regs


# ---------- geometría ----------
def utm_a_latlon(x, y, zona=18):
    """UTM WGS84 zona 18 sur, con northing negativo → (lat, lon) en grados (fórmulas de Snyder, error < 1 m)."""
    a, f, k0 = 6378137.0, 1 / 298.257223563, 0.9996
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)
    x -= 500000.0  # y ya viene con el falso norte de 10 000 km restado (northing negativo)
    m = y / k0
    mu = m / (a * (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    phi1 = (mu + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu)
            + (21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32) * math.sin(4 * mu)
            + (151 * e1 ** 3 / 96) * math.sin(6 * mu) + (1097 * e1 ** 4 / 512) * math.sin(8 * mu))
    s, c, t = math.sin(phi1), math.cos(phi1), math.tan(phi1)
    n1 = a / math.sqrt(1 - e2 * s * s)
    t1, c1 = t * t, ep2 * c * c
    r1 = a * (1 - e2) / (1 - e2 * s * s) ** 1.5
    d = x / (n1 * k0)
    lat = phi1 - (n1 * t / r1) * (d ** 2 / 2 - (5 + 3 * t1 + 10 * c1 - 4 * c1 ** 2 - 9 * ep2) * d ** 4 / 24
                                  + (61 + 90 * t1 + 298 * c1 + 45 * t1 ** 2 - 252 * ep2 - 3 * c1 ** 2) * d ** 6 / 720)
    lon = (d - (1 + 2 * t1 + c1) * d ** 3 / 6
           + (5 - 2 * c1 + 28 * t1 - 3 * c1 ** 2 + 8 * ep2 + 24 * t1 ** 2) * d ** 5 / 120) / c
    return math.degrees(lat), (zona - 1) * 6 - 180 + 3 + math.degrees(lon)


def simplificar(pts, tol):
    """Douglas-Peucker iterativo sobre coordenadas en metros."""
    if len(pts) < 3:
        return pts
    marca = [False] * len(pts)
    marca[0] = marca[-1] = True
    pila = [(0, len(pts) - 1)]
    while pila:
        i, j = pila.pop()
        (x1, y1), (x2, y2) = pts[i], pts[j]
        dx, dy = x2 - x1, y2 - y1
        l2 = dx * dx + dy * dy
        peor, k = -1.0, -1
        for m in range(i + 1, j):
            px, py = pts[m]
            if l2 == 0:
                dist = math.hypot(px - x1, py - y1)
            else:
                dist = abs(dy * px - dx * py + x2 * y1 - y2 * x1) / math.sqrt(l2)
            if dist > peor:
                peor, k = dist, m
        if peor > tol:
            marca[k] = True
            pila += [(i, k), (k, j)]
    return [p for p, ok in zip(pts, marca) if ok]


def largo_km(partes):
    return sum(math.dist(a, b) for pts in partes for a, b in zip(pts, pts[1:])) / 1000


# ---------- Excel de la ATU ----------
def exportar_excel():
    """Hoja 1 del .xlsx → CSV (zipfile + regex; sin openpyxl)."""
    z = zipfile.ZipFile(XLSX)
    ss = [re.sub("<[^>]+>", "", s) for s in re.findall(r"<si>(.*?)</si>", z.read("xl/sharedStrings.xml").decode(), re.S)]
    filas = []
    for fila in re.findall(r"<row [^>]*>(.*?)</row>", z.read("xl/worksheets/sheet1.xml").decode(), re.S):
        out = []
        for attrs, cuerpo in re.findall(r"<c ([^>]*?)(?:/>|>(.*?)</c>)", fila, re.S):
            v = re.search(r"<v>(.*?)</v>", cuerpo or "")
            v = v.group(1) if v else ""
            if 't="s"' in attrs and v:
                v = ss[int(v)]
            out.append(v.replace("&amp;", "&").strip())
        if any(out):
            filas.append(out[:4])
    with XCSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ruta", "ruc", "operador", "flota_requerida"])
        w.writerows(filas[1:])


def main():
    if XLSX.exists():
        exportar_excel()
    excel = {r["ruta"]: r for r in csv.DictReader(XCSV.open(encoding="utf-8"))}

    z = zipfile.ZipFile(SHP_ZIP)
    base = next(n[:-4] for n in z.namelist() if n.endswith(".shp"))
    atributos = leer_dbf(z.read(base + ".dbf"))
    geometrias = leer_shp(z.read(base + ".shp"))
    assert len(atributos) == len(geometrias)

    feats, rutas, pts_orig, pts_simpl = [], {}, 0, 0
    for at, partes in zip(atributos, geometrias):
        ruta = at["RUTA"]
        sentido = at["SENTIDO"].upper()
        lineas = []
        for pts in partes:
            pts_orig += len(pts)
            s = simplificar(pts, TOLERANCIA_M)
            pts_simpl += len(s)
            lineas.append([[round(lon, DECIMALES), round(lat, DECIMALES)]
                           for lat, lon in (utm_a_latlon(x, y) for x, y in s)])
        feats.append({"type": "Feature",
                      "properties": {"ruta": ruta, "sentido": sentido, "operador": at["OPERADOR"],
                                     "tipo": at["TIPO_DE_RU"], "carroceria": at["CARROCERIA"]},
                      "geometry": {"type": "MultiLineString", "coordinates": lineas}})
        r = rutas.setdefault(ruta, {
            "ruta": ruta, "codigo_antiguo": at["EX_CODIGO"], "operador": at["OPERADOR"],
            "ruc": excel.get(ruta, {}).get("ruc", ""), "tipo_ruta": at["TIPO_DE_RU"],
            "carroceria": at["CARROCERIA"], "categoria": at["CATEGORIA"],
            "flota_operativa": at["FLOTA_OPER"], "flota_reten": at["FLOTA_RETE"],
            "flota_requerida": at["FLOTA_REQU"], "intervalo": at["INTERVALO_"],
            "distrito_inicio": at["DISTRITO_I"], "distrito_fin": at["DISTRITO_F"],
            "punto_inicio": at["PUNTO_INIC"], "punto_fin": at["PUNTO_FINA"],
            "resolucion": at["RESOLUCION"], "sentidos": "", "km_atu": 0.0, "km_trazado": 0.0})
        r["sentidos"] = " ".join(sorted(set(r["sentidos"].split()) | {sentido}))
        try:
            r["km_atu"] += float(at["LONGITUD"].replace(",", ".") or 0)
        except ValueError:
            pass
        r["km_trazado"] += largo_km(partes)

    GEOJSON.write_text(json.dumps({"type": "FeatureCollection", "features": feats},
                                  ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    filas = sorted(rutas.values(), key=lambda r: r["ruta"])
    for r in filas:
        r["km_atu"], r["km_trazado"] = round(r["km_atu"], 2), round(r["km_trazado"], 2)
    with SALIDA.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    print(f"{len(feats)} trazados, {len(filas)} rutas; puntos {pts_orig:,} → {pts_simpl:,}; "
          f"GeoJSON {GEOJSON.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
