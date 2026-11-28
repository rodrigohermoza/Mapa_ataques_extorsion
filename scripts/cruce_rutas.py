"""Cruce de las rutas oficiales de la ATU con el Plan Regulador y con los ataques.

Entradas (data/processed/): rutas_oficiales.csv, rutas_trazados.geojson, fichas_atu.csv
(scripts/trazados_atu.py y fichas_atu.py), rutas_atu.csv (Plan Regulador 2024) y ataques.csv.

Salidas:
  data/processed/ataques_por_ruta.csv     todas las rutas (vigentes, nuevas y retiradas) con sus ataques.
  data/processed/ataques_por_empresa.csv  lo mismo agregado por RUC.
  results/rutas_atu.md                    controles de calidad y rankings.

Regla de conteo (D-10): un ataque con n rutas candidatas suma 1/n a cada una ("ponderado"),
para no inflar a las empresas con muchas rutas. También se dan "posibles" (rutas en las que el
ataque es candidato) y "seguros" (ataques con una sola ruta candidata). Por empresa, el peso
de sus rutas se suma; si las candidatas son de varias empresas, el ataque se reparte entre ellas.

Solo Python estándar: python3 -I scripts/cruce_rutas.py
"""
import collections
import csv
import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
P = RAIZ / "data" / "processed"
REPORTE = RAIZ / "results" / "rutas_atu.md"


def leer(nombre):
    with (P / nombre).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def escribir(nombre, filas):
    with (P / nombre).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)


def main():
    oficiales = {r["ruta"]: r for r in leer("rutas_oficiales.csv")}
    plan = {r["codigo"]: r for r in leer("rutas_atu.csv")}
    fichas = {r["ruta"]: r for r in leer("fichas_atu.csv")}
    ataques = leer("ataques.csv")
    geo = json.loads((P / "rutas_trazados.geojson").read_text(encoding="utf-8"))

    # ---- catálogo unificado ----
    rutas = {}
    for cod in sorted(set(oficiales) | set(plan)):
        o, p = oficiales.get(cod), plan.get(cod, {})
        estado = "vigente" if o and p else ("nueva" if o else "retirada")
        rutas[cod] = {
            "ruta": cod, "estado": estado,
            "codigo_antiguo": (o or {}).get("codigo_antiguo") or p.get("codigo_antiguo", ""),
            "empresa": o["operador"] if o else p.get("empresa", ""),
            "ruc": (o or {}).get("ruc", ""), "apodos": p.get("apodos_blog", ""),
            "tipo_ruta": (o or {}).get("tipo_ruta", ""), "carroceria": (o or {}).get("carroceria", ""),
            "flota_requerida": (o or {}).get("flota_requerida", ""),
            "km_trazado": (o or {}).get("km_trazado", ""),
            "distrito_inicio": (o or {}).get("distrito_inicio", ""),
            "distrito_fin": (o or {}).get("distrito_fin", ""),
            "ataques_ponderados": 0.0, "ataques_posibles": 0, "ataques_seguros": 0,
            "muertes_ponderadas": 0.0}

    # ---- reparto de ataques ----
    empresas = collections.defaultdict(lambda: {"ataques_ponderados": 0.0, "ataques_posibles": 0,
                                                "muertes_ponderadas": 0.0, "rutas": set()})
    sin_codigo = 0
    for a in ataques:
        cods = [c for c in a["codigos_ruta"].split() if c in rutas]
        if not cods:
            sin_codigo += 1
            continue
        w = 1 / len(cods)
        muerte = a["hubo_muerte"].strip().lower() in ("1", "si", "sí", "true")
        tocadas = set()
        for c in cods:
            r = rutas[c]
            r["ataques_ponderados"] += w
            r["ataques_posibles"] += 1
            r["ataques_seguros"] += len(cods) == 1
            r["muertes_ponderadas"] += w * muerte
            clave = r["ruc"] or r["empresa"]
            e = empresas[clave]
            e["ataques_ponderados"] += w
            e["muertes_ponderadas"] += w * muerte
            e["nombre"], e["ruc"] = r["empresa"], r["ruc"]
            tocadas.add(clave)
        for clave in tocadas:
            empresas[clave]["ataques_posibles"] += 1

    # rutas de cada empresa (catálogo completo, no solo las atacadas)
    for r in rutas.values():
        e = empresas.get(r["ruc"] or r["empresa"])
        if e is not None and r["estado"] != "retirada":
            e["rutas"].add(r["ruta"])

    filas = list(rutas.values())
    for r in filas:
        r["ataques_ponderados"] = round(r["ataques_ponderados"], 3)
        r["muertes_ponderadas"] = round(r["muertes_ponderadas"], 3)
    escribir("ataques_por_ruta.csv", filas)
    filas_e = sorted(({"ruc": e["ruc"], "empresa": e["nombre"], "rutas_vigentes": len(e["rutas"]),
                       "ataques_ponderados": round(e["ataques_ponderados"], 3),
                       "ataques_posibles": e["ataques_posibles"],
                       "muertes_ponderadas": round(e["muertes_ponderadas"], 3)}
                      for e in empresas.values()), key=lambda e: -e["ataques_ponderados"])
    escribir("ataques_por_empresa.csv", filas_e)

    # ---- controles ----
    est = collections.Counter(r["estado"] for r in filas)
    sentidos = collections.Counter(f["properties"]["ruta"] for f in geo["features"])
    lon = [c[0] for f in geo["features"] for l in f["geometry"]["coordinates"] for c in l]
    lat = [c[1] for f in geo["features"] for l in f["geometry"]["coordinates"] for c in l]
    en_lima = -12.6 < min(lat) and max(lat) < -11.5 and -77.3 < min(lon) and max(lon) < -76.5
    km_dif = []
    for cod, o in oficiales.items():
        kt, ka = float(o["km_trazado"]), float(o["km_atu"] or 0)
        kf = float(fichas.get(cod, {}).get("km_total") or 0)
        if ka and abs(kt / ka - 1) > 0.05:
            km_dif.append((cod, ka, kf, kt))
    ant_dif = [c for c in oficiales if c in plan and plan[c]["codigo_antiguo"]
               and oficiales[c]["codigo_antiguo"] and plan[c]["codigo_antiguo"] != oficiales[c]["codigo_antiguo"]]
    retiradas_atacadas = sorted({c for a in ataques for c in a["codigos_ruta"].split()
                                 if c in rutas and rutas[c]["estado"] == "retirada"})
    con_trazado = sum(any(c in oficiales for c in a["codigos_ruta"].split()) for a in ataques)
    con_codigo = len(ataques) - sin_codigo
    asignado = sum(r["ataques_ponderados"] for r in filas)

    L = ["# Rutas oficiales de la ATU: controles y cruce con ataques", "",
         "Generado por `scripts/cruce_rutas.py` (`make procesar`). Fuente: respuesta SAIP de la ATU "
         "del 2026-11-24 (shapefile al 5-nov-2026, fichas técnicas y relación de rutas).", "",
         "## Controles de calidad", "",
         "| Control | Resultado |", "|---|---|",
         f"| Rutas en el shapefile / fichas / Excel con RUC | {len(oficiales)} / {len(fichas)} / "
         f"{sum(bool(o['ruc']) for o in oficiales.values())} |",
         f"| Rutas sin ficha técnica válida | {' '.join(sorted(set(oficiales) - set(fichas))) or 'ninguna'} "
         "(el PDF «RUTA 1030» que envió la ATU es copia de la ficha 1130) |",
         f"| Rutas con ida y vuelta | {sum(v == 2 for v in sentidos.values())} de {len(sentidos)} |",
         f"| Coordenadas dentro de Lima y Callao | {'sí' if en_lima else 'NO'} "
         f"(lat {min(lat):.3f} a {max(lat):.3f}, lon {min(lon):.3f} a {max(lon):.3f}) |",
         f"| Longitud del trazado vs. campo LONGITUD (±5 %) | {len(oficiales) - len(km_dif)} de {len(oficiales)} coinciden |",
         f"| Código antiguo distinto entre Plan 2024 y shapefile | {len(ant_dif)} {' '.join(ant_dif[:10])} |",
         f"| Catálogo unificado | {len(filas)} rutas: {est['vigente']} vigentes, {est['nueva']} nuevas, "
         f"{est['retirada']} retiradas |", ""]
    if km_dif:
        L += ["Rutas cuya longitud no cuadra (km): en todas, la ficha técnica coincide con el trazado, "
              "así que el desactualizado es el campo LONGITUD del shapefile.", "",
              "| Ruta | LONGITUD shapefile | Ficha | Trazado |", "|---|---|---|---|"]
        L += [f"| {c} | {a:.2f} | {f:.2f} | {t:.2f} |" for c, a, f, t in sorted(km_dif)]
        L.append("")
    L += ["## Cruce con ataques", "",
          f"- Ataques: {len(ataques)}; con código de ruta: {con_codigo}; con al menos una ruta con trazado: {con_trazado}.",
          f"- Peso repartido entre rutas: {asignado:.1f} (debe ser igual a {con_codigo}).",
          f"- Rutas retiradas que aparecen en ataques (sin trazado actual): {', '.join(retiradas_atacadas) or 'ninguna'}.",
          f"- Rutas con algún ataque: {sum(r['ataques_posibles'] > 0 for r in filas)} de {len(filas)}.", "",
          "### 15 rutas con más ataques (ponderados)", "",
          "| Ruta | Empresa | Estado | Ponderados | Posibles | Seguros |", "|---|---|---|---|---|---|"]
    for r in sorted(filas, key=lambda r: -r["ataques_ponderados"])[:15]:
        L.append(f"| {r['ruta']} | {r['empresa'][:60]} | {r['estado']} | {r['ataques_ponderados']:.2f} | "
                 f"{r['ataques_posibles']} | {r['ataques_seguros']} |")
    L += ["", "### 15 empresas con más ataques (ponderados)", "",
          "| Empresa | RUC | Rutas vigentes | Ponderados | Posibles |", "|---|---|---|---|---|"]
    for e in filas_e[:15]:
        L.append(f"| {e['empresa'][:60]} | {e['ruc']} | {e['rutas_vigentes']} | "
                 f"{e['ataques_ponderados']:.2f} | {e['ataques_posibles']} |")
    REPORTE.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(filas)} rutas, {len(filas_e)} empresas con ataques → results/rutas_atu.md")


if __name__ == "__main__":
    main()
