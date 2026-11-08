"""Recolecta titulares de Google Noticias (RSS) sobre ataques al transporte en Lima y Callao.

Solo biblioteca estándar. Guarda cada nota una sola vez en data/raw/noticias.jsonl.

Uso:
    python3 -I scripts/recolectar.py --diario              # desde la última nota bajada (-3 días)
    python3 -I scripts/recolectar.py --desde 2024-08-01    # histórico (ventanas adaptativas)

Google Noticias devuelve ~10 notas por consulta en fechas antiguas, así que el histórico
parte en ventanas de 7 días y, si una ventana llega al tope, la divide en días.
"""
import argparse
import datetime as dt
import email.utils
import json
import pathlib
import subprocess
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "data" / "raw" / "noticias.jsonl"
PARAMS = json.loads((RAIZ / "params.json").read_text(encoding="utf-8"))
CONSULTAS = PARAMS["consultas"]
PAUSA = PARAMS.get("pausa_segundos", 1.5)
TOPE = 9  # si una ventana devuelve >= TOPE notas, se divide
UA = "Mozilla/5.0 (Macintosh) mapa-crimen/0.1"



def pedir(consulta, desde=None, hasta=None, when=None):
    q = consulta
    if when:
        q += f" when:{when}"
    else:
        q += f" after:{desde.isoformat()} before:{hasta.isoformat()}"
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": q, "hl": "es-419", "gl": "PE", "ceid": "PE:es-419"})
    for intento in range(4):
        try:
            # curl en vez de urllib: el Python de python.org no trae certificados (P-05)
            r = subprocess.run(["curl", "-sfL", "-m", "30", "-A", UA, url],
                               capture_output=True, check=True)
            raiz = ET.fromstring(r.stdout)
            break
        except Exception as e:  # red o límite de tasa: esperar y reintentar
            espera = 10 * (intento + 1)
            print(f"  error ({e}); reintento en {espera}s", file=sys.stderr)
            time.sleep(espera)
    else:
        return None
    time.sleep(PAUSA)
    notas = []
    for it in raiz.iter("item"):
        fecha = email.utils.parsedate_to_datetime(it.findtext("pubDate"))
        notas.append({
            "titulo": it.findtext("title", "").strip(),
            "medio": it.findtext("source", "").strip(),
            "fecha": fecha.date().isoformat(),
            "url": it.findtext("link", "").strip(),
            "guid": it.findtext("guid", "").strip(),
        })
    return notas


def cargar_vistos():
    vistos = set()
    if SALIDA.exists():
        for linea in SALIDA.open(encoding="utf-8"):
            vistos.add(json.loads(linea)["guid"])
    return vistos


def guardar(notas, vistos, consulta_id):
    nuevas = 0
    with SALIDA.open("a", encoding="utf-8") as f:
        for n in notas:
            if n["guid"] in vistos:
                continue
            vistos.add(n["guid"])
            n["consulta"] = consulta_id
            n["recolectado"] = dt.date.today().isoformat()
            f.write(json.dumps(n, ensure_ascii=False) + "\n")
            nuevas += 1
    return nuevas


def ventana(consulta_id, consulta, desde, hasta, vistos, fallos):
    notas = pedir(consulta, desde, hasta)
    if notas is None:
        fallos.append((consulta_id, desde.isoformat(), hasta.isoformat()))
        return 0
    total = guardar(notas, vistos, consulta_id)
    dias = (hasta - desde).days
    if len(notas) >= TOPE and dias > 1:
        d = desde
        while d < hasta:
            total += ventana(consulta_id, consulta, d, d + dt.timedelta(days=1), vistos, fallos)
            d += dt.timedelta(days=1)
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", type=dt.date.fromisoformat)
    ap.add_argument("--hasta", type=dt.date.fromisoformat, default=dt.date.today() + dt.timedelta(days=1))
    ap.add_argument("--diario", action="store_true")
    a = ap.parse_args()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    vistos = cargar_vistos()
    fallos = []
    if a.diario:
        # se corre a mano los fines de semana (D-06): retomar desde la última nota bajada,
        # con 3 días de margen por notas publicadas tarde (las repetidas se descartan)
        ultima = max((json.loads(l)["fecha"] for l in SALIDA.open(encoding="utf-8")), default=None) \
            if SALIDA.exists() else None
        a.desde = (dt.date.fromisoformat(ultima) - dt.timedelta(days=3)) if ultima \
            else dt.date.today() - dt.timedelta(days=7)
        print(f"Actualizando desde {a.desde} (última nota: {ultima})")
    if a.desde:
        d = a.desde
        while d < a.hasta:
            h = min(d + dt.timedelta(days=7), a.hasta)
            nuevas = sum(ventana(cid, c, d, h, vistos, fallos) for cid, c in CONSULTAS.items())
            print(f"{d} → {h}: {nuevas} nuevas (total {len(vistos)})", flush=True)
            d = h
    else:
        ap.error("usar --diario o --desde AAAA-MM-DD")
    if fallos:
        print(f"Ventanas fallidas: {fallos}", file=sys.stderr)


if __name__ == "__main__":
    main()
