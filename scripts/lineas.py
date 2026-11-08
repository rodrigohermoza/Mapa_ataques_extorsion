"""Directorio de rutas regulares de Lima y Callao → data/processed/lineas.csv. Sin dependencias.

Fuente: blog infotransportenlima (lista "Rutas regulares autorizadas por la ATU", actualizada
mar-2026), guardada en data/raw/rutas/. Cada entrada: código ATU de 4 dígitos + texto libre con
sobrenombres separados por "/" y la empresa entre paréntesis.

Uso: python3 -I scripts/lineas.py
"""
import csv
import html
import pathlib
import re
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "data" / "raw" / "rutas" / "infotransportenlima_lista_2025.html"
SALIDA = RAIZ / "data" / "processed" / "lineas.csv"


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").strip()


def leer():
    t = ENTRADA.read_text(encoding="utf-8")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<br\s*/?>|</(p|div|li|tr|h\d)>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    for linea in t.split("\n"):
        m = re.match(r"\s*(1[0-4]\d\d(?:-X)?)\s*(.*)$", linea.strip())
        if m and not re.fullmatch(r"-*", m.group(2).strip()):
            yield m.group(1), m.group(2).strip()


SINONIMOS = {"el chino": "chinos", "chino": "chinos", "etupsa 73": "etupsa", "rojitos": "rojitos"}


def cargar_indice():
    """{clave normalizada: {códigos}} desde lineas.csv (vacío si no existe)."""
    idx = {}
    if SALIDA.exists():
        for l in csv.DictReader(SALIDA.open(encoding="utf-8")):
            for c in l["claves"].split(" | "):
                idx.setdefault(c, set()).add(l["codigo"])
    # nombres oficiales de empresa (Plan Regulador, scripts/rutas_atu.py), guardados como "oficial:<nombre>"
    oficial = SALIDA.parent / "rutas_atu.csv"
    if oficial.exists():
        for f in csv.DictReader(oficial.open(encoding="utf-8")):
            n = norm(f["empresa"])
            if n:
                idx.setdefault("oficial:" + n, set()).add(f["codigo"])
    return idx


def buscar(empresa, idx):
    """Devuelve (códigos, tipo): tipo = exacto | familia | aproximado | ''."""
    e = SINONIMOS.get(empresa, empresa)
    sin_art = re.sub(r"^(el|la|los|las)\s+", "", e)
    for k in (e, sin_art):
        if k in idx:
            return sorted(idx[k]), "exacto"
    m = re.match(r"^linea\s+([0-9]{1,4})$", e)
    if m:  # "línea 73" → 73A, 73B, 73-1…
        cods = {c for k, v in idx.items() if re.fullmatch(rf"linea {m.group(1)}[a-z0-9]", k) for c in v}
        if cods:
            return sorted(cods), "familia"
    if len(sin_art) >= 4:  # nombre dentro de la razón social oficial: "z buss" → "... Z BUSS S.A."
        pat = re.compile(rf"\b{re.escape(sin_art)}\b")
        cods = {c for k, v in idx.items() if k.startswith("oficial:") and pat.search(k) for c in v}
        if cods:
            return sorted(cods), "oficial"
    if len(sin_art) >= 5:  # "etmosa" → "etmosac": revisar a mano
        cods = {c for k, v in idx.items() if k.startswith(sin_art) and len(k) - len(sin_art) <= 2 for c in v}
        if cods:
            return sorted(cods), "aproximado"
    return [], ""


def main():
    filas = []
    for codigo, texto in leer():
        empresas = re.findall(r"\(([^)]+)\)", texto)
        sin_par = re.sub(r"\([^)]*\)", "", texto)
        apodos = [a.strip() for a in sin_par.split("/") if a.strip()]
        # variantes normalizadas para cruzar con la prensa: "la 47" → "linea 47"; "los chinos" → "chinos"
        claves = set()
        for a in apodos + empresas:
            n = re.sub(r"^la la ", "la ", norm(a))
            claves.add(n)
            m = re.match(r"^(?:la|linea)\s+([0-9a-z]{1,4}(?:-?[0-9a-z])?)$", n)
            if m:
                claves.add("linea " + m.group(1).replace("-", ""))
            claves.add(re.sub(r"^(el|la|los|las)\s+", "", n))
        filas.append(dict(codigo=codigo, texto=texto, apodos=" | ".join(apodos),
                          empresas=" | ".join(empresas), claves=" | ".join(sorted(c for c in claves if c))))
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with SALIDA.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} rutas con nombre → {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
