"""Fichas técnicas de las 445 rutas (PDF de la ATU) → data/processed/fichas_atu.csv.

Cada ficha trae el itinerario (vías de ida y luego de vuelta, sin separador claro en el texto),
distritos de origen y destino, flota, longitud e intervalo. Los atributos numéricos ya están en
el shapefile (scripts/trazados_atu.py); de aquí interesa sobre todo la lista de vías, para más
adelante proponer rutas a los ataques que solo dicen la avenida y el distrito.

Lee los PDF dentro de los ZIP originales (data/raw/atu/fichas_prr_*.zip), sin extraerlos.
Requiere pypdf (venv del proyecto): .venv/bin/python -I scripts/fichas_atu.py
"""
import csv
import io
import pathlib
import re
import zipfile

import pypdf

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ZIPS = sorted((RAIZ / "data" / "raw" / "atu").glob("fichas_prr_*.zip"))
SALIDA = RAIZ / "data" / "processed" / "fichas_atu.csv"


def campo(texto, etiqueta):
    m = re.search(etiqueta + r"\s*\n?:\s*([^\n]*)", texto)
    return m.group(1).strip() if m else ""


def leer(texto):
    ruta = re.search(r"RUTA (\d{4})", texto).group(1)
    tramo = texto.split("Itinerario Vuelta", 1)[1].split("CARROCER", 1)[0]
    vias = []
    for v in (v.strip() for v in tramo.split("\n")):
        if v and vias and vias[-1].count("(") > vias[-1].count(")"):
            vias[-1] += " " + v  # vía partida en dos líneas: "... (VUELTA EN U ALT. AVENIDA HONORIO" + "DELGADO)"
        elif v:
            vias.append(v)
    unicas = list(dict.fromkeys(vias))
    km = re.search(r"TOTAL\s*\n\s*([\d.]+) KM", texto)
    return {"ruta": ruta,
            "distrito_origen": campo(texto, "DISTRITO DE ORIGEN"),
            "distrito_destino": campo(texto, "DISTRITO DE DESTINO"),
            "punto_inicial": campo(texto, "PUNTO INICIAL"),
            "punto_final": campo(texto, "PUNTO FINAL"),
            "km_total": km.group(1) if km else "",
            "n_tramos": len(vias),
            "vias": " | ".join(unicas)}


def main():
    filas = []
    for z in ZIPS:
        with zipfile.ZipFile(z) as zz:
            for nombre in zz.namelist():
                if nombre.lower().endswith(".pdf"):
                    pdf = pypdf.PdfReader(io.BytesIO(zz.read(nombre)))
                    fila = leer("\n".join(p.extract_text() or "" for p in pdf.pages))
                    del_nombre = re.search(r"(\d{4})", nombre).group(1)
                    if fila["ruta"] != del_nombre:  # P-09: "RUTA 1030.pdf" es copia de la ficha 1130
                        print(f"  aviso: {nombre} contiene la ficha de la ruta {fila['ruta']}; se descarta")
                        continue
                    filas.append(fila)
    filas.sort(key=lambda f: f["ruta"])
    with SALIDA.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} fichas → {SALIDA.relative_to(RAIZ)}; "
          f"sin vías: {sum(not f['vias'] for f in filas)}")


if __name__ == "__main__":
    main()
