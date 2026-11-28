"""Convierte titulares (data/raw/noticias.jsonl) en hechos (data/processed/ataques.csv). Sin IA.

Pasos: filtrar relevantes → extraer distrito, empresa, rol, desenlace, unidad → agrupar
notas del mismo hecho (fecha ±2 días, mismo distrito, empresa compatible).

Uso: python3 -I scripts/extraer.py
"""
import collections
import csv
import datetime as dt
import json
import pathlib
import re
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "data" / "raw" / "noticias.jsonl"
SALIDA_NOTAS = RAIZ / "data" / "processed" / "notas_clasificadas.csv"
SALIDA = RAIZ / "data" / "processed" / "ataques.csv"


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


# --- Distritos de Lima Metropolitana y Callao (+ alias de la prensa) -----------------
DISTRITOS = {
    "Ancón": ["ancon"], "Ate": ["ate", "ate vitarte", "vitarte", "huaycan", "santa clara"],
    "Barranco": ["barranco"], "Breña": ["brena"], "Carabayllo": ["carabayllo"],
    "Chaclacayo": ["chaclacayo"], "Chorrillos": ["chorrillos"], "Cieneguilla": ["cieneguilla"],
    "Comas": ["comas"], "El Agustino": ["el agustino"], "Independencia": ["independencia"],
    "Jesús María": ["jesus maria"], "La Molina": ["la molina"], "La Victoria": ["la victoria", "gamarra"],
    "Cercado de Lima": ["cercado de lima", "cercado", "centro de lima", "barrios altos", "avenida abancay",
                        "av. abancay", "plaza dos de mayo"],
    "Lince": ["lince"], "Los Olivos": ["los olivos"],
    "Lurigancho-Chosica": ["chosica", "lurigancho-chosica", "huachipa", "cajamarquilla"],
    "Lurín": ["lurin"], "Magdalena del Mar": ["magdalena"], "Miraflores": ["miraflores"],
    "Pachacámac": ["pachacamac", "manchay"], "Pucusana": ["pucusana"], "Pueblo Libre": ["pueblo libre"],
    "Puente Piedra": ["puente piedra"], "Punta Hermosa": ["punta hermosa"], "Punta Negra": ["punta negra"],
    "Rímac": ["rimac"], "San Bartolo": ["san bartolo"], "San Borja": ["san borja"],
    "San Isidro": ["san isidro"], "San Juan de Lurigancho": ["san juan de lurigancho", "sjl"],
    "San Juan de Miraflores": ["san juan de miraflores", "sjm"], "San Luis": ["san luis"],
    "San Martín de Porres": ["san martin de porres", "smp"], "San Miguel": ["san miguel"],
    "Santa Anita": ["santa anita"], "Santa María del Mar": ["santa maria del mar"], "Santa Rosa": ["santa rosa"],
    "Santiago de Surco": ["surco", "santiago de surco"], "Surquillo": ["surquillo"],
    "Villa El Salvador": ["villa el salvador", "ves"], "Villa María del Triunfo": ["villa maria del triunfo", "vmt"],
    "Callao": ["callao", "minka"], "Bellavista": ["bellavista"], "Carmen de la Legua": ["carmen de la legua"],
    "La Perla": ["la perla"], "La Punta": ["la punta"], "Ventanilla": ["ventanilla"], "Mi Perú": ["mi peru"],
}
# los alias más largos primero ("san juan de miraflores" antes que "miraflores")
ALIAS = sorted(((a, d) for d, al in DISTRITOS.items() for a in al), key=lambda x: -len(x[0]))

# ojo: no poner países (hay avenidas Argentina, Colombia, México en Lima)
FUERA_DE_LIMA = re.compile(r"\b(trujillo|piura|chiclayo|arequipa|tumbes|chimbote|huancayo|cusco|ica|"
                           r"huanuco|la libertad|lambayeque|sullana|huaral|huacho|canete|chincha|"
                           r"pisco|tacna|puno|ayacucho|cajamarca|iquitos|pucallpa|ecuador|"
                           r"interprovincial|panamericana norte|panamericana sur|huaraz|con destino a|jicamarca|"
                           r"huarochiri|ricardo palma|san antonio de chaclla)\b")
TRANSPORTE = re.compile(r"\b(bus|buses|combi|combis|custer|coaster|colectivo|omnibus|microbus|"
                        r"chofer|choferes|chofere?s?|cobrador|cobradora|cobradores|conductor|conductora|conductores|"
                        r"transportista|transportistas|"
                        r"empresa de transportes?|transporte publico|unidad de transporte|linea)\b")
ATAQUE = re.compile(r"(balea|balean|balacera|balazo|baleado|baleada|dispar|asesin|acribill|atentado|"
                    r"explosiv|dinamita|bomba|atac|ataq|sicari|matan|mataron|incendian|incendiaron|"
                    r"a tiros|abatid|ejecut)")
ACCIDENTE = re.compile(r"(accidente|choque|chocan|choca |volcadura|vuelca|despiste|colisi|atropell|embiste|"
                       r"inundacion|atascado|hundido|sin frenos|piedras|pedrada|\bpalo\b|orquesta|cumbia|agrupacion|"
                       r"armonia 10|tropical|cantantes|musicos|durante robo|asalto|asaltan|robo a)")
NO_HECHO = re.compile(r"(captur|detien|detenid|\bcaen?\b|desarticul|prision|condena|intervien|"
                      r"cifras|estadistic|\bpollada\b|"
                      r"\bcongreso\b|ministro|ministerio|premier|presidente|alcalde|opinion|editorial|"
                      r"\bcomo\b.*\?|\bque se sabe\b|\bquienes son\b|homenaje|velorio|sepelio|despiden|"
                      r"\bpnp\b|policia (?:detuvo|identifica|captura)|mininter|plan escudo|patrullaje|"
                      r"audios|revelan|asi coordinan|asi fue|videos? del|camaras captan|"
                      r"\b(?:dos|tres|cuatro|cinco) (?:atentados|ataques)|doble atentado|ultimas 24 horas|"
                      r"fin de semana sangrient|en lo que va del|en lo que va de|\bsuman\b|"
                      r"gerente|dirigente|jalador|vigilante|mototaxi)")
LESION = re.compile(r"(herid|lesion|grave|baleado|baleada|hospital|internad|uci\b|disparo en|recibio)")
MOTOTAXI = re.compile(r"mototaxi")

ROLES = [("cobrador", r"cobrador"), ("chofer", r"chofer|conductor|conductora|transportista"),
         ("pasajero", r"pasajer")]
MUERTE = re.compile(r"(asesin|acribill|matan|mataron|muere|murio|muerto|sin vida|fallec|ejecut)")
UNIDAD = [("combi", r"combi"), ("cúster", r"custer|coaster"), ("colectivo", r"colectivo"),
          ("mototaxi", r"mototaxi"), ("bus", r"\bbus|omnibus|microbus")]

COMILLAS = r"[\"'‘’“”«»]"
PAT_EMPRESA = [
    re.compile(COMILLAS + r"([^\"'‘’“”«»]{2,40})" + COMILLAS),  # nombre entre comillas
    re.compile(r"empresa (?:de transportes? )?(?:y servicios )?((?:[A-ZÁÉÍÓÚÑ0-9][\wÁÉÍÓÚÑáéíóúñ\.]*\s?){1,4})"),
    re.compile(r"(?:bus|buses|unidad|combi|custer|cúster|chofer|conductor|cobrador) de (?:la )?((?:El|La|Los|Las|Línea|Linea)\s[\wÁÉÍÓÚÑáéíóúñ0-9]+(?:\s[A-ZÁÉÍÓÚÑ0-9][\wáéíóúñ]*)?)"),
    re.compile(r"\b((?:línea|linea|ruta)\s+[0-9]{1,4}[A-Z]?|(?:línea|linea)\s+[A-Z]{1,2})\b", re.I),
    re.compile(r"(?:línea|linea) ([A-ZÁÉÍÓÚÑ][\wáéíóúñ]{3,}(?:\s[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+)?)"),  # "línea Pesqueros"
    # "bus de Translima", "chofer de Etmosa": una palabra con mayúscula que no sea distrito
    re.compile(r"(?:bus|buses|ómnibus|omnibus|combi|cúster|custer|chofer|conductor|cobrador|unidad) de ([A-ZÁÉÍÓÚÑ][\wáéíóúñ]{3,}(?:\s(?:del?\s)?[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+)?)"),
    re.compile(r"\b(?:la|de la)\s+([0-9]{1,3}[A-Z]?)\b"),  # "la 91", "de la 10E"
]
CONTEXTO_EMPRESA = re.compile(r"(bus|buses|empresa|linea|chofer|conductor|cobrador|combi|custer|"
                              r"unidad|transportes?|ruta|de la|del|de)\s*$")
VACIAS = {"el", "la", "los", "las", "de", "del", "y", "en", "con", "a", "su", "un", "una"}
NO_EMPRESA = re.compile(r"^(lima|callao|el callao|la victoria|los olivos|la molina|la perla|la punta|"
                        r"los mexicanos|el tren de aragua|tren de aragua|los pulpos|los pepes|terror|"
                        r"a plena luz del dia|video|videos|en vivo|urgente|ultimo minuto|"
                        r"pagaba|no pago|cupo|cupos|el|la|callao unido|los injertos|los malditos|"
                        r"los pulpos|la jauria|el monstruo|unidad|perla argentina|la perla argentina)$")


# nombres que la prensa escribe de varias formas (clave: sin espacios)
SINONIMOS = {"zbuss": "z buss", "chino": "el chino", "chinos": "el chino", "etuchisa": "el chino",
             "sol": "sol de oro", "flores": "las flores", "rapido": "el rapido",
             "elrapido": "el rapido", "triangulo": "el triangulo", "mandarino": "el mandarino",
             "tigrillo": "el tigrillo", "losrojitos": "rojitos", "cruz": "cruz del centro"}


def limpiar_empresa(s):
    s = s.strip(" .,:;-–—!¡?¿")
    s = re.sub(r"\s+(en|de|y|con|tras|por|que|al|a|frente|cerca)$", "", s.strip(), flags=re.I)
    s = re.sub(r"\s+(en|tras|por|que|frente|cerca)\s.*$", "", s, flags=re.I)
    n = norm(s)
    n = re.sub(r"^(empresa|linea)\s+", lambda m: m.group(0) if m.group(1) == "linea" else "", n)
    n = re.sub(r"\s+(s\.?a\.?c?\.?|sac|sa)$", "", n).strip()
    n = re.sub(r"^(?:la|de la|ruta|linea)\s+([0-9]{1,4}[a-z]?)$", r"linea \1", n)
    n = re.sub(r"^(?:la|las|los)\s+(?=[a-z]{4,})", "", n) if not n.startswith(("la 5", "la 9")) else n
    if not n or n in VACIAS or NO_EMPRESA.match(n) or any(n == a for a, _ in ALIAS):
        return None
    if re.match(r"^[0-9]{1,4}[a-z]?$", n):
        n = "linea " + n
    n = re.sub(r"^(?:e\.?\s?t\.?|ett|empresa de transportes?)\s+", "", n).strip(" .")
    n = SINONIMOS.get(n.replace(" ", ""), n)
    if n in ("linea", "ruta", "empresa", "transportes") or len(n.replace(" ", "")) < 3:
        return None
    return n


def elegir_distrito(t):
    """Prefiere el distrito que sigue a 'en' o abre el titular ('SJM: ...'); si no, el primero."""
    hallados = []
    ocupado = set()
    for a, d in ALIAS:  # largos primero; no contar "miraflores" dentro de "san juan de miraflores"
        for m in re.finditer(rf"\b{re.escape(a)}\b", t):
            if any(i in ocupado for i in range(m.start(), m.end())):
                continue
            ocupado.update(range(m.start(), m.end()))
            antes = t[max(0, m.start() - 4):m.start()]
            prioridad = 0 if (m.start() == 0 or antes.endswith(("en ", "el ")) or
                              t[m.end():m.end() + 1] == ":") else 1
            hallados.append((prioridad, m.start(), d))
    return min(hallados)[2] if hallados else ""


def extraer(nota):
    titulo = re.sub(r"\s+-\s+[^-]{2,60}$", "", nota["titulo"])  # quitar " - Medio"
    t = norm(titulo)
    r = dict(fecha=nota["fecha"], medio=nota["medio"], titulo=titulo, url=nota["url"])
    r["relevante"] = bool(TRANSPORTE.search(t) and ATAQUE.search(t)
                          and not NO_HECHO.search(t) and not ACCIDENTE.search(t)
                          and not FUERA_DE_LIMA.search(t))
    r["distrito"] = elegir_distrito(t)
    emp = ""
    for i, p in enumerate(PAT_EMPRESA):
        for m in p.finditer(titulo):
            if i == 0:  # comillas: exigir contexto de transporte justo antes y nombre corto
                antes = norm(titulo[max(0, m.start() - 30):m.start()])
                if not CONTEXTO_EMPRESA.search(antes) or len(m.group(1).split()) > 4:
                    continue
            e = limpiar_empresa(m.group(1))
            if e:
                emp = e
                break
        if emp:
            break
    r["empresa"] = emp
    r["roles"] = ";".join(n for n, p in ROLES if re.search(p, t))
    r["muerte"] = bool(MUERTE.search(t))
    # el Ministerio Público solo cuenta ataques con fallecidos o lesionados
    r["con_victimas"] = bool(r["muerte"] or LESION.search(t))
    r["unidad"] = next((n for n, p in UNIDAD if re.search(p, t)), "")
    return r


def agrupar(notas):
    hechos = []
    for n in sorted(notas, key=lambda x: x["fecha"]):
        f = dt.date.fromisoformat(n["fecha"])
        elegido = None
        for h in reversed(hechos):
            if (f - h["_ultima"]).days > 3:
                break
            if not n["distrito"] or n["distrito"] != h["distrito"]:
                # sin distrito: solo unir si la empresa coincide
                if not (n["empresa"] and n["empresa"] in h["_empresas"]):
                    continue
            if n["empresa"] and h["_empresas"] and n["empresa"] not in h["_empresas"]:
                continue
            elegido = h
            break
        if elegido is None and not n["distrito"] and not n["empresa"]:
            continue  # no se puede ubicar ni distinguir: suele ser otra nota del mismo hecho
        if elegido is None:
            elegido = dict(fecha=n["fecha"], distrito=n["distrito"], _empresas=collections.Counter(),
                           _ultima=f, _notas=[])
            hechos.append(elegido)
        elegido["_notas"].append(n)
        elegido["_ultima"] = max(elegido["_ultima"], f)
        if n["empresa"]:
            elegido["_empresas"][n["empresa"]] += 1
        if not elegido["distrito"] and n["distrito"]:
            elegido["distrito"] = n["distrito"]
    filas = []
    for i, h in enumerate(hechos, 1):
        ns = h["_notas"]
        unidades = collections.Counter(x["unidad"] for x in ns if x["unidad"])
        roles = collections.Counter(r for x in ns for r in x["roles"].split(";") if r)
        filas.append(dict(
            id=f"A-{i:04d}", fecha=h["fecha"], distrito=h["distrito"],
            empresa=h["_empresas"].most_common(1)[0][0] if h["_empresas"] else "",
            unidad=unidades.most_common(1)[0][0] if unidades else "",
            roles=";".join(r for r, _ in roles.most_common()),
            hubo_muerte=any(x["muerte"] for x in ns),
            con_victimas=any(x["con_victimas"] for x in ns), n_notas=len(ns),
            titular=max(ns, key=lambda x: len(x["titulo"]))["titulo"],
            urls=" ".join(x["url"] for x in ns[:5]),
        ))
    return filas


def main():
    notas = [json.loads(l) for l in ENTRADA.open(encoding="utf-8")]
    # mismo titular en varias consultas → una sola nota
    unicas = {}
    for n in notas:
        unicas.setdefault((n["fecha"], norm(n["titulo"])), n)
    ext = [extraer(n) for n in unicas.values()]
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with SALIDA_NOTAS.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(ext[0]))
        w.writeheader()
        w.writerows(sorted(ext, key=lambda x: x["fecha"]))
    rel = [e for e in ext if e["relevante"]]
    filas = agrupar(rel)
    # código de ruta ATU según el directorio de líneas (scripts/lineas.py)
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    import lineas
    idx = lineas.cargar_indice()
    for f in filas:
        cods, tipo = lineas.buscar(f["empresa"], idx) if f["empresa"] else ([], "")
        f["codigos_ruta"] = " ".join(cods)
        f["cruce_ruta"] = tipo
    with SALIDA.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    con_emp = sum(1 for x in filas if x["empresa"])
    con_dis = sum(1 for x in filas if x["distrito"])
    print(f"notas: {len(notas)} ({len(unicas)} únicas), relevantes: {len(rel)}")
    print(f"hechos: {len(filas)}; con empresa {con_emp} ({con_emp/len(filas):.0%}), "
          f"con distrito {con_dis} ({con_dis/len(filas):.0%})")


if __name__ == "__main__":
    main()
