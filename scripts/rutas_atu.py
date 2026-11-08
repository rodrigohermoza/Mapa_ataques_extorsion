"""Tabla oficial de rutas de la ATU → data/processed/rutas_atu.csv.

Fuente: Plan Regulador de Rutas para Lima y Callao (Res. 282-2024-ATU/PE), sección 14
"Cuadro de equivalencia de código de ruta" (págs. 87-96): código actual (antiguo), código
nuevo del Plan (PRR) y empresa. Se une con los sobrenombres de data/processed/lineas.csv.

Requiere pypdf (venv del proyecto): .venv/bin/python -I scripts/rutas_atu.py
"""
import csv
import pathlib
import re

import pypdf

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PDF = RAIZ / "data" / "raw" / "rutas" / "plan_regulador_rutas_2024.pdf"
LINEAS = RAIZ / "data" / "processed" / "lineas.csv"
SALIDA = RAIZ / "data" / "processed" / "rutas_atu.csv"
PAGINAS = range(87, 97)  # 1-indexadas
FILA = re.compile(r"^\s*(\d{1,3})\s+(\S+)\s+(1[0-4]\d\d(?:-?X)?)\s*(.*)$")


def main():
    lector = pypdf.PdfReader(PDF)
    filas, previa = [], None
    for n in PAGINAS:
        for linea in (lector.pages[n - 1].extract_text() or "").split("\n"):
            m = FILA.match(linea)
            if m:
                previa = dict(n=int(m.group(1)), codigo_antiguo=m.group(2),
                              codigo=m.group(3), empresa=m.group(4).strip())
                filas.append(previa)
            elif previa and linea.strip() and not re.search(
                    r"PLAN REGULADOR|^\s*\d+\s*$|N° Ruta|CUADRO DE EQUIVALENCIA", linea):
                previa["empresa"] = (previa["empresa"] + " " + linea.strip()).strip()  # empresa en 2 líneas
    apodos = {}
    if LINEAS.exists():
        for l in csv.DictReader(LINEAS.open(encoding="utf-8")):
            apodos[l["codigo"]] = l
    for f in filas:
        l = apodos.get(f["codigo"], {})
        f["apodos_blog"] = l.get("apodos", "")
        f["empresa_blog"] = l.get("empresas", "")
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with SALIDA.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    nums = [f["n"] for f in filas]
    faltan = sorted(set(range(1, max(nums) + 1)) - set(nums))
    print(f"{len(filas)} rutas (n.º 1–{max(nums)}; faltan {len(faltan)}: {faltan[:15]}) → "
          f"{SALIDA.relative_to(RAIZ)}")
    print(f"con empresa oficial: {sum(1 for f in filas if f['empresa'])}; "
          f"con sobrenombre del blog: {sum(1 for f in filas if f['apodos_blog'])}")


if __name__ == "__main__":
    main()
