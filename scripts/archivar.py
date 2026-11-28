"""Archiva las noticias para que no se pierdan si el medio las borra. Solo biblioteca estándar + curl.

Para cada nota de data/raw/noticias.jsonl que aún no esté archivada:
  1. Decodifica el enlace de Google Noticias → enlace real del medio.
  2. Descarga la página y guarda SOLO el texto (título, fecha, cuerpo) en data/raw/articulos/<id>.json
     (fuera de git: los textos tienen derechos de autor y el repositorio es público).
  3. Busca o pide una copia en Internet Archive (Wayback Machine).
El estado queda en data/raw/archivo.jsonl (una línea por nota; sí va a git: enlaces públicos).

Uso:
    python3 -I scripts/archivar.py                 # enlace real + texto de las notas nuevas (~5 s por nota)
    python3 -I scripts/archivar.py --reintentar    # además reintenta las que fallaron
    python3 -I scripts/archivar.py --wayback       # copias en Internet Archive (~30-50 s por nota)
    --limite N procesa solo N notas. Se puede cortar con Ctrl+C: el registro se guarda tras cada nota.
"""
import argparse
import datetime as dt
import hashlib
import html
import json
import pathlib
import re
import subprocess
import sys
import time
import urllib.parse

RAIZ = pathlib.Path(__file__).resolve().parent.parent
NOTICIAS = RAIZ / "data" / "raw" / "noticias.jsonl"
ESTADO = RAIZ / "data" / "raw" / "archivo.jsonl"
TEXTOS = RAIZ / "data" / "raw" / "articulos"
PARAMS = json.loads((RAIZ / "params.json").read_text(encoding="utf-8"))
PAUSA = PARAMS.get("pausa_segundos", 1.5)
PAUSA_WAYBACK = PARAMS.get("pausa_wayback_segundos", 6)
PAUSA_GOOGLE = PARAMS.get("pausa_google_segundos", 8)  # más rápido → Google bloquea (429) tras ~30 notas
UA = "Mozilla/5.0 (Macintosh) mapa-crimen/0.1"
MAX_HTML = 5_000_000  # no leer páginas de más de 5 MB


def curl(url, datos=None, max_s=30):
    """Devuelve (código HTTP, url final, cuerpo en bytes) o (0, '', b'') si falla la red."""
    cmd = ["curl", "-sL", "-m", str(max_s), "-A", UA, "--max-filesize", str(MAX_HTML),
           "-w", "\n%{http_code} %{url_effective}", url]
    if datos is not None:
        cmd += ["-H", "Content-Type: application/x-www-form-urlencoded;charset=UTF-8", "--data", datos]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=max_s + 10)
    except subprocess.TimeoutExpired:
        return 0, "", b""
    cuerpo, _, fin = r.stdout.rpartition(b"\n")
    try:
        codigo, final = fin.decode().split(" ", 1)
        return int(codigo), final, cuerpo
    except ValueError:
        return 0, "", b""


class Bloqueo(Exception):
    """Google respondió 429 / página de 'tráfico inusual': parar y reintentar otro día."""


def enlace_real(url_google):
    """Google Noticias ya no deja el enlace en el id: hay que pedir firma y hora y llamar a batchexecute."""
    gid = urllib.parse.urlparse(url_google).path.rstrip("/").split("/")[-1]
    cod, final, cuerpo = curl(f"https://news.google.com/articles/{gid}?hl=es-419&gl=PE&ceid=PE:es-419")
    if cod == 429 or "/sorry/" in final:
        raise Bloqueo
    t = cuerpo.decode("utf-8", "replace")
    firma = re.search(r'data-n-a-sg="([^"]+)"', t)
    hora = re.search(r'data-n-a-ts="([^"]+)"', t)
    if not (firma and hora):
        return None
    pedido = ["Fbv4je", f'["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,'
                        f'null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{gid}",{hora.group(1)},'
                        f'"{firma.group(1)}"]']
    datos = "f.req=" + urllib.parse.quote(json.dumps([[pedido]]))
    time.sleep(PAUSA_GOOGLE / 2)
    cod, final, cuerpo = curl("https://news.google.com/_/DotsSplashUi/data/batchexecute", datos)
    if cod == 429 or "/sorry/" in final:
        raise Bloqueo
    try:
        bloque = json.loads(cuerpo.decode("utf-8").split("\n\n", 1)[1])
        return json.loads(bloque[0][2])[1]
    except Exception:
        return None


def texto_articulo(crudo):
    """Título, fecha y cuerpo desde el HTML. Primero JSON-LD (articleBody), si no los <p>."""
    t = crudo.decode("utf-8", "replace")
    titulo = fecha = cuerpo = ""
    for bloque in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', t, re.S | re.I):
        try:
            d = json.loads(bloque.strip())
        except Exception:
            continue
        pila = d if isinstance(d, list) else [d]
        while pila:
            x = pila.pop()
            if isinstance(x, dict):
                if x.get("articleBody") and not cuerpo:
                    cuerpo = x["articleBody"]
                    titulo = titulo or x.get("headline", "")
                    fecha = fecha or x.get("datePublished", "")
                pila.extend(v for v in x.values() if isinstance(v, (dict, list)))
            elif isinstance(x, list):
                pila.extend(x)
    if not titulo:
        m = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', t) or \
            re.search(r"<title>(.*?)</title>", t, re.S)
        titulo = m.group(1) if m else ""
    if not fecha:
        m = re.search(r'<meta[^>]+property="article:published_time"[^>]+content="([^"]*)"', t)
        fecha = m.group(1) if m else ""
    # el JSON-LD a veces trae solo el resumen: comparar con los <p> del <article> y de toda la página
    t2 = re.sub(r"<(script|style|noscript)\b.*?</\1>", "", t, flags=re.S | re.I)
    zona = re.search(r"<article\b.*?</article>", t2, re.S | re.I)
    for parte in ([zona.group(0)] if zona else []) + [t2]:
        ps = re.findall(r"<p\b[^>]*>(.*?)</p>", parte, re.S | re.I)
        ps = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", p)).strip() for p in ps]
        candidato = "\n\n".join(p for p in ps if len(p) > 40)
        if len(candidato) > 1.5 * len(cuerpo):
            cuerpo = candidato
            break
    limpio = lambda s: re.sub(r"\s+\n|\n\s+", "\n", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()
    return limpio(titulo), fecha.strip(), limpio(cuerpo)


def wayback(url):
    """Enlace a una copia en Internet Archive: usa la existente o pide una nueva (Save Page Now)."""
    cod, _, cuerpo = curl("https://archive.org/wayback/available?url=" + urllib.parse.quote(url, safe=""))
    try:
        snap = json.loads(cuerpo)["archived_snapshots"].get("closest")
        if snap and snap.get("available"):
            return snap["url"], "existente"
    except Exception:
        pass
    time.sleep(PAUSA_WAYBACK)
    cod, final, _ = curl("https://web.archive.org/save/" + url, max_s=120)
    if cod == 200 and "/web/" in final:
        return final, "nueva"
    return "", f"error {cod}"


def cargar_estado():
    hechos = {}
    if ESTADO.exists():
        for l in ESTADO.open(encoding="utf-8"):
            e = json.loads(l)
            hechos[e["guid"]] = e  # si hay repetidos, vale el último
    return hechos


def guardar_estado(hechos):
    tmp = ESTADO.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for e in hechos.values():
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    tmp.replace(ESTADO)


def archivar_texto(n, hechos):
    nid = hashlib.sha1(n["guid"].encode()).hexdigest()[:12]
    e = hechos.get(n["guid"]) or {"guid": n["guid"], "id": nid, "medio": n["medio"], "fecha": n["fecha"],
                                  "url_real": "", "texto": "", "chars": 0, "wayback": "", "wayback_estado": ""}
    e["archivado"] = dt.date.today().isoformat()
    if not e["url_real"]:
        e["url_real"] = enlace_real(n["url"]) or ""
        time.sleep(PAUSA_GOOGLE / 2)
    if not e["url_real"]:
        e["texto"] = "sin enlace real"
        return e
    cod, _, crudo = curl(e["url_real"])
    if cod == 200 and crudo:
        titulo, fecha, cuerpo = texto_articulo(crudo)
        if len(cuerpo) >= 200:
            (TEXTOS / f"{nid}.json").write_text(json.dumps(
                {"id": nid, "url": e["url_real"], "titulo": titulo, "fecha_publicacion": fecha,
                 "texto": cuerpo, "descargado": e["archivado"]}, ensure_ascii=False, indent=1), encoding="utf-8")
            e["texto"], e["chars"] = "ok", len(cuerpo)
        else:
            e["texto"] = "sin cuerpo"
    else:
        e["texto"] = f"http {cod}"
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wayback", action="store_true",
                    help="pedir copias a Internet Archive de lo ya archivado (lento, ~30-50 s por nota)")
    ap.add_argument("--limite", type=int, default=0, help="procesar solo N notas")
    ap.add_argument("--reintentar", action="store_true", help="volver a intentar el texto de las que fallaron")
    a = ap.parse_args()
    hechos = cargar_estado()
    notas = [json.loads(l) for l in NOTICIAS.open(encoding="utf-8")]
    if a.wayback:
        pendientes = [n for n in notas if n["guid"] in hechos and hechos[n["guid"]]["url_real"]
                      and not hechos[n["guid"]]["wayback"]]
    else:
        pendientes = [n for n in notas if n["guid"] not in hechos
                      or hechos[n["guid"]]["texto"] == "sin enlace real"
                      or (a.reintentar and hechos[n["guid"]]["texto"] != "ok")]
    pendientes.sort(key=lambda n: n["fecha"], reverse=True)  # lo más reciente primero
    if a.limite:
        pendientes = pendientes[:a.limite]
    TEXTOS.mkdir(parents=True, exist_ok=True)
    print(f"{len(pendientes)} notas por {'copiar en Wayback' if a.wayback else 'archivar'} "
          f"({len(hechos)} en el registro)")
    t0 = time.time()
    for i, n in enumerate(pendientes, 1):
        if a.wayback:
            e = hechos[n["guid"]]
            e["wayback"], e["wayback_estado"] = wayback(e["url_real"])
        else:
            try:
                e = archivar_texto(n, hechos)
            except Bloqueo:
                print(f"Google limitó las consultas (429) en la nota {i}. Se detiene; lo pendiente se "
                      "retoma en la próxima corrida (esperar unas horas).")
                break
        hechos[n["guid"]] = e
        guardar_estado(hechos)  # se guarda tras cada nota: se puede cortar con Ctrl+C sin perder nada
        print(f"[{i}/{len(pendientes)}] {n['medio'][:18]:18} texto={e['texto']:<15} {e['chars']:>6} car. "
              f"wayback={e['wayback_estado'] or '-'}", flush=True)
    print(f"Listo en {time.time() - t0:.0f}s")


if __name__ == "__main__":
    sys.exit(main())
