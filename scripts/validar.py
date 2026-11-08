"""Compara data/processed/ataques.csv con las cifras del Observatorio de Criminalidad del Ministerio
Público (boletín con corte al 31-may-2026) y escribe results/validacion.md. Sin dependencias.

Uso: python3 -I scripts/validar.py
"""
import collections
import csv
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ATAQUES = RAIZ / "data" / "processed" / "ataques.csv"
SALIDA = RAIZ / "results" / "validacion.md"

# Ministerio Público, atentados CON víctimas (fallecidos o lesionados), Lima y Callao.
OFICIAL_PERIODO = {"2024 (ago-dic)": 20, "2025": 107, "2026 (ene-may)": 87}  # suman 214
OFICIAL_ZONA = {"Lima Norte": 70, "Lima Sur": 44, "Lima Este": 43, "Lima Centro": 21,
                "Callao": 18, "Lima Noroeste": 18}  # ago-2024 a may-2026

# Distritos fiscales (aproximado: el Ministerio Público no publica la lista exacta en el boletín)
ZONA = {}
for z, ds in {
    "Lima Norte": ["Carabayllo", "Comas", "Independencia", "Los Olivos", "San Martín de Porres"],
    "Lima Noroeste": ["Puente Piedra", "Ancón", "Santa Rosa", "Ventanilla", "Mi Perú"],
    "Lima Este": ["San Juan de Lurigancho", "Ate", "Santa Anita", "El Agustino", "Lurigancho-Chosica",
                  "Chaclacayo", "Cieneguilla", "La Molina"],
    "Lima Sur": ["San Juan de Miraflores", "Villa María del Triunfo", "Villa El Salvador", "Chorrillos",
                 "Lurín", "Pachacámac", "Pucusana", "Punta Hermosa", "Punta Negra", "San Bartolo",
                 "Santa María del Mar"],
    "Lima Centro": ["Cercado de Lima", "Rímac", "Breña", "La Victoria", "San Luis", "San Borja",
                    "San Miguel", "Pueblo Libre", "Jesús María", "Lince", "Magdalena del Mar",
                    "Miraflores", "San Isidro", "Surquillo", "Santiago de Surco", "Barranco"],
    "Callao": ["Callao", "Bellavista", "La Perla", "La Punta", "Carmen de la Legua"],
}.items():
    for d in ds:
        ZONA[d] = z


def periodo(fecha):
    if "2024-08" <= fecha[:7] <= "2024-12":
        return "2024 (ago-dic)"
    if fecha.startswith("2025"):
        return "2025"
    if "2026-01" <= fecha[:7] <= "2026-05":
        return "2026 (ene-may)"
    return None


def main():
    filas = list(csv.DictReader(ATAQUES.open(encoding="utf-8")))
    lin = ["# Validación contra el Ministerio Público", "",
           f"Hechos en la base: **{len(filas)}** (todas las fechas).", "",
           "## Por periodo (comparable: ago-2024 a may-2026)", "",
           "| Periodo | Base propia (con víctimas) | Ministerio Público (con víctimas) | Cobertura |", "|---|---|---|---|"]
    por_p = collections.Counter(periodo(f["fecha"]) for f in filas if f["con_victimas"] == "True")
    for p, o in OFICIAL_PERIODO.items():
        lin.append(f"| {p} | {por_p[p]} | {o} | {por_p[p] / o:.0%} |")
    tot_b = sum(por_p[p] for p in OFICIAL_PERIODO)
    tot_o = sum(OFICIAL_PERIODO.values())
    lin.append(f"| **Total** | **{tot_b}** | **{tot_o}** | **{tot_b / tot_o:.0%}** |")
    sin_moto = tot_o - 45 - 5  # el boletín cuenta 45 ataques a mototaxis y 5 a taxis; aquí no se buscan
    lin.append(f"| Total sin mototaxis ni taxis | {tot_b} | {sin_moto} | **{tot_b / sin_moto:.0%}** |")
    sin_v = sum(1 for f in filas if periodo(f["fecha"]) and f["con_victimas"] != "True")
    lin += ["", f"Además hay {sin_v} ataques sin víctimas en el periodo (el Ministerio Público no los incluye aquí).", "",
            "## Por zona (distrito fiscal, ago-2024 a may-2026, con víctimas)", "",
            "| Zona | Base propia | Ministerio Público |", "|---|---|---|"]
    en_periodo = [f for f in filas if periodo(f["fecha"]) and f["con_victimas"] == "True"]
    por_z = collections.Counter(ZONA.get(f["distrito"], "Sin distrito") for f in en_periodo)
    for z, o in OFICIAL_ZONA.items():
        lin.append(f"| {z} | {por_z[z]} | {o} |")
    lin.append(f"| Sin distrito | {por_z['Sin distrito']} | — |")
    con_emp = [f for f in filas if f["empresa"]]
    lin += ["", "## Calidad de la extracción", "",
            f"- Con empresa/línea: {len(con_emp)} de {len(filas)} ({len(con_emp) / len(filas):.0%})",
            f"- Con distrito: {sum(1 for f in filas if f['distrito'])} de {len(filas)}",
            f"- Con muerte mencionada: {sum(1 for f in filas if f['hubo_muerte'] == 'True')}",
            "", "## Empresas / líneas con más ataques (todas las fechas)", "",
            "| Empresa / línea | Ataques | Distritos | Rutas ATU (cruce) |", "|---|---|---|---|"]
    emp = collections.defaultdict(list)
    for f in con_emp:
        emp[f["empresa"]].append(f)
    for e, fs in sorted(emp.items(), key=lambda x: -len(x[1]))[:30]:
        ds = ", ".join(sorted({f["distrito"] for f in fs if f["distrito"]}))
        cod = fs[0].get("codigos_ruta", "") or "—"
        tipo = fs[0].get("cruce_ruta", "")
        lin.append(f"| {e} | {len(fs)} | {ds} | {cod}{' (' + tipo + ')' if tipo and tipo != 'exacto' else ''} |")
    con_cod = sum(1 for f in con_emp if f.get("codigos_ruta"))
    lin.insert(lin.index("## Empresas / líneas con más ataques (todas las fechas)") - 1,
               f"- Con código de ruta ATU: {con_cod} de {len(con_emp)} con empresa ({con_cod / len(con_emp):.0%})")
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text("\n".join(lin) + "\n", encoding="utf-8")
    print("\n".join(lin))


if __name__ == "__main__":
    main()
