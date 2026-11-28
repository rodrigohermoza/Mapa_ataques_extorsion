"""Mapa de ataques y rutas con filtro por fecha → results/mapa.html.

Un solo HTML autocontenido (datos embebidos). Al verlo carga Leaflet 1.9.4 (unpkg) y el mapa base de
OpenStreetMap en gris. Se publica en GitHub Pages (.github/workflows/pages.yml).

Capas:
  - Ataques con lugar (scripts/ubicar.py, D-12): punto; relleno = hubo muerte, anillo = sin muerte.
  - Ataques ubicados solo por distrito: un círculo por distrito, de tamaño según cuántos son.
  - Rutas de la ATU coloreadas por los ataques DEL PERIODO elegido (reparto 1/n, D-10).
  - Límites de distritos.
El periodo se elige con el histograma mensual (desde/hasta), botones por año o ▶ (avanza mes a mes).
No se muestran titulares (pueden nombrar a víctimas); sí los enlaces a las noticias.

Solo Python estándar: python3 -I scripts/mapa.py
"""
import csv
import datetime
import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
P = RAIZ / "data" / "processed"
SALIDA = RAIZ / "results" / "mapa.html"
CAMPOS = ("estado", "empresa", "ruc", "apodos", "tipo_ruta", "carroceria", "flota_requerida",
          "km_trazado", "distrito_inicio", "distrito_fin")


def leer(nombre):
    with (P / nombre).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def enlaces_reales():
    """URL de Google Noticias → enlace real del medio (si ya se archivó)."""
    guid = {}
    for l in (RAIZ / "data" / "raw" / "noticias.jsonl").open(encoding="utf-8"):
        n = json.loads(l)
        guid[n["guid"]] = n["url"]
    real = {}
    archivo = RAIZ / "data" / "raw" / "archivo.jsonl"
    if archivo.exists():
        for l in archivo.open(encoding="utf-8"):
            e = json.loads(l)
            if e.get("url_real") and e["guid"] in guid:
                real[guid[e["guid"]]] = e["url_real"]
    return real


def main():
    geo = json.loads((P / "rutas_trazados.geojson").read_text(encoding="utf-8"))
    rutas = {}
    for r in leer("ataques_por_ruta.csv"):
        d = {k: r[k] for k in CAMPOS}
        d["lineas"] = []
        rutas[r["ruta"]] = d
    for f in geo["features"]:
        rutas[f["properties"]["ruta"]]["lineas"] += f["geometry"]["coordinates"]

    real = enlaces_reales()
    ataques = []
    for a in leer("ataques_ubicados.csv"):
        urls = a["urls"].split()
        ataques.append({
            "f": a["fecha"], "d": a["distrito"], "p": a["precision"],
            "lat": float(a["lat"]) if a["lat"] else None, "lon": float(a["lon"]) if a["lon"] else None,
            "l": a["lugar"], "c": [c for c in a["codigos_ruta"].split() if c in rutas],
            "m": a["hubo_muerte"] == "True", "r": a["roles"].replace(";", ", "), "e": a["empresa"],
            "u": [real.get(u, u) for u in urls[:3]]})
    ataques.sort(key=lambda a: a["f"])
    distritos = json.loads((P / "distritos_lima.geojson").read_text(encoding="utf-8"))
    meta = dict(generado=datetime.date.today().isoformat())
    datos = json.dumps({"rutas": rutas, "ataques": ataques, "distritos": distritos, "meta": meta},
                       ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    SALIDA.write_text(PLANTILLA.replace("__DATOS__", datos), encoding="utf-8")
    con = {k: sum(a["p"] == k for a in ataques) for k in ("lugar", "distrito")}
    print(f"{len(ataques)} ataques ({con['lugar']} con lugar, {con['distrito']} por distrito) → "
          f"{SALIDA.relative_to(RAIZ)} ({SALIDA.stat().st_size / 1e6:.1f} MB)")


PLANTILLA = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ataques al transporte</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
:root {
  --surface: #fcfcfb; --panel: #ffffff; --border: #e4e3df; --hover: #f1f0ec;
  --text-1: #0b0b0b; --text-2: #52514e; --text-3: #7a7974;
  --cero: #b9b8b2; --hl: #0b0b0b; --pt: #eb6834; --pt-claro: #ffffff;
  --s1: #86b6ef; --s2: #5598e7; --s3: #2a78d6; --s4: #1c5cab; --s5: #0d366b;
  --barra: #c9c8c2; --barra-sel: #eb6834; --enlace: #1c5cab;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --surface: #1a1a19; --panel: #222221; --border: #3a3a38; --hover: #2c2c2a;
  --text-1: #f0efec; --text-2: #c3c2b7; --text-3: #94938c;
  --cero: #4a4a47; --hl: #ffffff; --pt: #d95926; --pt-claro: #1a1a19;
  --s1: #184f95; --s2: #256abf; --s3: #3987e5; --s4: #6da7ec; --s5: #b7d3f6;
  --barra: #4a4a47; --barra-sel: #d95926; --enlace: #6da7ec;
}}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; background: var(--surface); color: var(--text-1);
  font: 14px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif; }
#app { display: flex; height: 100%; }
#panel { width: 390px; flex: none; overflow-y: auto; background: var(--panel);
  border-right: 1px solid var(--border); padding: 20px 20px 32px; }
#mapa { flex: 1; background: var(--surface); }
h1 { font-size: 20px; line-height: 1.25; margin: 0 0 6px; }
h2 { font-size: 12px; text-transform: uppercase; letter-spacing: .05em; color: var(--text-2); margin: 22px 0 8px; }
p { margin: 0 0 8px; color: var(--text-2); }
.nota { font-size: 12px; color: var(--text-3); }
label { display: block; margin: 5px 0; color: var(--text-2); }
select, input[type=search] { width: 100%; padding: 6px 8px; border: 1px solid var(--border);
  border-radius: 6px; background: var(--surface); color: var(--text-1); font: inherit; }
button { font: inherit; border: 1px solid var(--border); background: var(--surface); color: var(--text-1);
  border-radius: 6px; padding: 4px 10px; cursor: pointer; }
button.activo { border-color: var(--text-1); font-weight: 600; }
#periodo-txt { font-size: 15px; font-weight: 600; color: var(--text-1); margin: 2px 0 6px; }
#hist { display: block; width: 100%; height: 84px; cursor: crosshair; touch-action: none; }
.rangos { position: relative; height: 22px; }
.rangos input { position: absolute; width: 100%; left: 0; top: 0; margin: 0; pointer-events: none;
  background: none; -webkit-appearance: none; appearance: none; height: 22px; }
.rangos input::-webkit-slider-thumb { pointer-events: auto; -webkit-appearance: none; width: 16px; height: 16px;
  border-radius: 50%; background: var(--text-1); border: 2px solid var(--panel); cursor: pointer; }
.rangos input::-moz-range-thumb { pointer-events: auto; width: 13px; height: 13px; border-radius: 50%;
  background: var(--text-1); border: 2px solid var(--panel); cursor: pointer; }
.botones { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 4px; }
.leyenda { display: flex; gap: 2px; margin-top: 4px; }
.leyenda div { flex: 1; font-size: 11px; color: var(--text-2); text-align: center; }
.leyenda i { display: block; height: 8px; border-radius: 2px; margin-bottom: 3px; }
.ley-pt { display: flex; gap: 14px; flex-wrap: wrap; font-size: 12px; color: var(--text-2); margin: 2px 0 8px 22px; }
.ley-pt span { display: inline-flex; align-items: center; gap: 6px; }
.ley-pt i { display: inline-block; width: 12px; height: 12px; border-radius: 50%; border: 2px solid var(--pt); }
table { width: 100%; border-collapse: collapse; font-size: 12.5px; table-layout: fixed; }
col.c1 { width: 58px; } col.cn { width: 72px; }
th { text-align: left; font-weight: 600; color: var(--text-2); border-bottom: 1px solid var(--border); padding: 4px; }
td { padding: 4px; border-bottom: 1px solid var(--border); vertical-align: top; }
td:first-child { white-space: nowrap; }
td.e { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
td.n, th.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
tbody tr { cursor: pointer; } tbody tr:hover { background: var(--hover); }
.chip { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 6px; vertical-align: -1px; }
#detalle { display: none; margin-top: 14px; padding: 12px 12px 4px; border: 1px solid var(--border); border-radius: 8px;
  max-height: 340px; overflow-y: auto; position: relative; }
#detalle .cerrar { position: absolute; right: 6px; top: 4px; border: none; padding: 2px 8px; font-size: 16px; }
#detalle dl { display: grid; grid-template-columns: auto 1fr; gap: 2px 10px; margin: 8px 0 0; font-size: 12.5px; }
#detalle dt { color: var(--text-3); } #detalle dd { margin: 0; }
#detalle ul { margin: 6px 0 0; padding-left: 18px; font-size: 12.5px; }
#detalle li { margin-bottom: 6px; }
#detalle a { color: var(--enlace); }
.leaflet-tile-pane { filter: grayscale(1) contrast(.85) brightness(1.05); opacity: .55; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .leaflet-tile-pane {
  filter: grayscale(1) invert(1) brightness(.75) contrast(.9); opacity: .6; } }
.leaflet-tooltip { font: 12px/1.4 system-ui, sans-serif; }
@media (max-width: 760px) {
  #app { flex-direction: column-reverse; }
  #panel { width: 100%; height: 52%; border-right: none; border-top: 1px solid var(--border); padding: 14px 16px 24px; }
}
</style>
</head>
<body>
<div id="app">
  <aside id="panel">
    <h1>Ataques al transporte público en Lima y Callao</h1>
    <p id="resumen"></p>

    <h2>Periodo</h2>
    <div id="periodo-txt"></div>
    <svg id="hist" role="img" aria-label="Ataques por mes; arrastra para elegir el periodo"></svg>
    <div class="rangos">
      <input type="range" id="desde" min="0" value="0" aria-label="Desde">
      <input type="range" id="hasta" min="0" value="0" aria-label="Hasta">
    </div>
    <div class="botones" id="anios"></div>

    <h2>Capas</h2>
    <label><input type="checkbox" id="c-ataques" checked> Ataques</label>
    <div class="ley-pt">
      <span><i style="background:var(--pt)"></i>Con muerte</span>
      <span><i style="background:var(--pt-claro)"></i>Sin muerte</span>
      <span><i style="width:16px;height:16px;background:var(--pt);opacity:.4;border-width:1px"></i>Solo se sabe el distrito</span>
    </div>
    <label><input type="checkbox" id="c-rutas" checked> Rutas, según los ataques del periodo</label>
    <select id="medida" aria-label="Medida de las rutas">
      <option value="pond">Ataques repartidos (1/n por ruta candidata)</option>
      <option value="pos">Ataques posibles (la ruta es candidata)</option>
      <option value="seg">Ataques seguros (única ruta candidata)</option>
    </select>
    <div class="leyenda" id="leyenda"></div>
    <label><input type="checkbox" id="ceros"> Mostrar rutas sin ataques</label>
    <label><input type="checkbox" id="c-distritos" checked> Límites de distritos</label>
    <label style="margin-top:10px">Buscar ruta o empresa
      <input type="search" id="buscar" placeholder="Ej. 1388, Santa Catalina">
    </label>
    <div id="detalle"></div>

    <h2>Distritos con más ataques</h2>
    <table><colgroup><col><col class="cn"><col class="cn"></colgroup>
      <thead><tr><th>Distrito</th><th class="n">Ataques</th><th class="n">Con muerte</th></tr></thead>
      <tbody id="t-distritos"></tbody></table>
    <h2>Rutas con más ataques</h2>
    <table><colgroup><col class="c1"><col><col class="cn"></colgroup>
      <thead><tr><th>Ruta</th><th>Empresa</th><th class="n" id="th-ruta">Ataques</th></tr></thead>
      <tbody id="t-rutas"></tbody></table>
    <h2>Empresas con más ataques</h2>
    <table><colgroup><col><col class="c1"><col class="cn"></colgroup>
      <thead><tr><th>Empresa</th><th class="n">Rutas</th><th class="n">Repartidos</th></tr></thead>
      <tbody id="t-empresas"></tbody></table>

    <h2>Cómo leerlo</h2>
    <p class="nota">Los ataques salen de titulares de Google Noticias (sin IA), agrupados en hechos. Cuando la
      noticia nombra una avenida, paradero u óvalo, se ubicó con OpenStreetMap y se aceptó solo si cae dentro del
      distrito (y cerca de la ruta, si se conoce): es un punto aproximado. Si solo se sabe el distrito, el ataque
      suma al círculo del distrito. Las rutas se colorean con los ataques que nombran a su empresa o línea; si la
      empresa tiene varias rutas, «repartidos» suma 1/n a cada una. Trazados oficiales de la ATU al 5-nov-2026.</p>
    <p class="nota" id="pie"></p>
  </aside>
  <div id="mapa"></div>
</div>
<script>
const D = __DATOS__;
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const fmt = v => Number.isInteger(v) ? String(v) : v.toFixed(2).replace(/0$/, "");
const MESES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"];
const CORTES = { pond: [0.5, 1, 2, 3.5], pos: [1, 2, 4, 6], seg: [1, 2, 3, 4] };
const ETIQ = { pond: ["≤0.5","≤1","≤2","≤3.5",">3.5"], pos: ["1","2","3–4","5–6","7+"], seg: ["1","2","3","4","5+"] };

// ---------- meses ----------
const A = D.ataques;
const meses = [];
{ let [y, m] = A[0].f.slice(0, 7).split("-").map(Number); const fin = A[A.length - 1].f.slice(0, 7);
  while (true) { const k = `${y}-${String(m).padStart(2, "0")}`; meses.push(k); if (k >= fin) break; m === 12 ? (y++, m = 1) : m++; } }
A.forEach(a => a.mi = meses.indexOf(a.f.slice(0, 7)));
const nomMes = i => { const [y, m] = meses[i].split("-"); return `${MESES[+m - 1]} ${y}`; };
let desde = 0, hasta = meses.length - 1, medida = "pond", seleccion = null, enPeriodo = [];

// ---------- mapa ----------
const mapa = L.map("mapa", { preferCanvas: true }).setView([-12.05, -77.0], 11);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · Rutas: ATU (5-nov-2026) · Distritos: peru-geojson'
}).addTo(mapa);
mapa.createPane("distritos").style.zIndex = 350;
mapa.createPane("puntos").style.zIndex = 450;
const capaDistritos = L.geoJSON(D.distritos, { pane: "distritos", interactive: false,
  style: () => ({ color: css("--text-3"), weight: 1, opacity: .5, fill: false }) }).addTo(mapa);
const grupoRutas = L.layerGroup().addTo(mapa);
const grupoAtaques = L.layerGroup().addTo(mapa);
const rend = L.canvas({ pane: "puntos" });

// ---------- rutas ----------
const capas = {};
for (const [cod, r] of Object.entries(D.rutas)) {
  r.pond = r.pos = r.seg = 0;
  if (!r.lineas.length) continue;
  const capa = L.polyline(r.lineas.map(l => l.map(([x, y]) => [y, x])));
  capa.bindTooltip(() => `<b>Ruta ${cod}</b> · ${esc(r.empresa)}<br>${etiq(r)}`, { sticky: true });
  capa.on("click", e => { L.DomEvent.stop(e); elegirRuta(cod); });
  capas[cod] = capa;
}
const etiq = r => `En el periodo: repartidos ${fmt(r.pond)} · posibles ${r.pos} · seguros ${r.seg}`;
function clase(v) { if (!v) return 0; const c = CORTES[medida]; let i = 0; while (i < c.length && v > c[i]) i++; return i + 1; }
const colorClase = k => k ? css("--s" + k) : css("--cero");
const ancho = k => [1, 2, 2.5, 3, 4, 5][k];
function coincide(r, cod) {
  const q = document.getElementById("buscar").value.trim().toLowerCase();
  return !q || cod.includes(q) || r.empresa.toLowerCase().includes(q) || r.apodos.toLowerCase().includes(q);
}
function pintarRutas() {
  grupoRutas.clearLayers();
  if (!document.getElementById("c-rutas").checked) return;
  const ceros = document.getElementById("ceros").checked, q = document.getElementById("buscar").value.trim();
  Object.keys(capas).sort((a, b) => D.rutas[a][medida] - D.rutas[b][medida]).forEach(cod => {
    const r = D.rutas[cod], k = clase(r[medida]);
    if ((!k && !ceros && !q && cod !== seleccion) || !coincide(r, cod)) return;
    const sel = cod === seleccion;
    capas[cod].setStyle({ color: sel ? css("--hl") : colorClase(k), weight: ancho(k) + (sel ? 2 : 0), opacity: k ? .85 : .45 });
    grupoRutas.addLayer(capas[cod]);
  });
  if (seleccion && capas[seleccion]) capas[seleccion].bringToFront();
}

// ---------- ataques ----------
function agrupar(lista) {
  const g = {}; lista.forEach(a => { const k = a.lat + "," + a.lon; (g[k] = g[k] || []).push(a); }); return Object.values(g);
}
function pintarAtaques() {
  grupoAtaques.clearLayers();
  if (!document.getElementById("c-ataques").checked) return;
  const pt = css("--pt"), claro = css("--pt-claro");
  for (const lista of agrupar(enPeriodo.filter(a => a.p === "distrito"))) {
    const a = lista[0], n = lista.length, t = `${a.d}: ${n} ataque${n > 1 ? "s" : ""} sin lugar exacto`;
    L.circleMarker([a.lat, a.lon], { renderer: rend, radius: 5 + 3.2 * Math.sqrt(n), color: pt, weight: 1.5,
      fillColor: pt, fillOpacity: .28 })
      .bindTooltip(`<b>${esc(a.d)}</b><br>${n} ataque${n > 1 ? "s" : ""} sin lugar exacto`)
      .on("click", e => { L.DomEvent.stop(e); mostrarAtaques(t, lista); }).addTo(grupoAtaques);
  }
  for (const lista of agrupar(enPeriodo.filter(a => a.p === "lugar"))) {
    const a = lista[0], n = lista.length, muerte = lista.some(x => x.m), t = `${a.l} (${a.d || "sin distrito"})`;
    L.circleMarker([a.lat, a.lon], { renderer: rend, radius: 6 + 2 * (n - 1), color: pt, weight: 2.5,
      fillColor: muerte ? pt : claro, fillOpacity: 1 })
      .bindTooltip(`<b>${esc(a.l)}</b> · ${esc(a.d || "sin distrito")}<br>${n} ataque${n > 1 ? "s" : ""}${muerte ? " · con muerte" : ""} · lugar aproximado`)
      .on("click", e => { L.DomEvent.stop(e); mostrarAtaques(t, lista); }).addTo(grupoAtaques);
  }
}

// ---------- periodo ----------
function calcular() {
  enPeriodo = A.filter(a => a.mi >= desde && a.mi <= hasta);
  for (const r of Object.values(D.rutas)) r.pond = r.pos = r.seg = 0;
  for (const a of enPeriodo) {
    if (!a.c.length) continue;
    const w = 1 / a.c.length;
    for (const c of a.c) { const r = D.rutas[c]; r.pond += w; r.pos++; if (a.c.length === 1) r.seg++; }
  }
}
const cuentaMes = meses.map((_, i) => A.filter(a => a.mi === i).length);
function histograma() {
  const svg = document.getElementById("hist"), W = svg.clientWidth || 340, H = 84, base = H - 16;
  const max = Math.max(...cuentaMes), bw = W / meses.length, gap = Math.min(2, bw * .25);
  let s = "";
  cuentaMes.forEach((n, i) => {
    const h = n ? Math.max(2, (base - 12) * n / max) : 0, sel = i >= desde && i <= hasta;
    s += `<rect x="${(i * bw + gap / 2).toFixed(1)}" y="${(base - h).toFixed(1)}" width="${(bw - gap).toFixed(1)}" height="${h.toFixed(1)}" rx="1.5" fill="${sel ? css("--barra-sel") : css("--barra")}"><title>${nomMes(i)}: ${n} ataques</title></rect>`;
  });
  s += `<line x1="0" x2="${W}" y1="${base}" y2="${base}" stroke="${css("--border")}"/>`;
  [...new Set(meses.map(m => m.slice(0, 4)))].forEach(y => { const i = meses.findIndex(m => m.startsWith(y));
    s += `<text x="${i * bw + 1}" y="${H - 3}" font-size="10" fill="${css("--text-3")}">${y}</text>`; });
  s += `<text x="${W}" y="9" font-size="10" text-anchor="end" fill="${css("--text-3")}">máx. ${max} al mes</text>`;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`); svg.innerHTML = s;
}
function actualizar() {
  calcular(); histograma(); pintarRutas(); pintarAtaques(); tablas();
  rDesde.value = desde; rHasta.value = hasta;
  const n = enPeriodo.length, lug = enPeriodo.filter(a => a.p === "lugar").length,
        dis = enPeriodo.filter(a => a.p === "distrito").length, mu = enPeriodo.filter(a => a.m).length;
  document.getElementById("periodo-txt").textContent = desde === hasta ? nomMes(desde) : `${nomMes(desde)} – ${nomMes(hasta)}`;
  document.getElementById("resumen").innerHTML =
    `<b>${n}</b> ataques registrados en noticias en el periodo, <b>${mu}</b> con muertes: ` +
    `${lug} con lugar aproximado, ${dis} solo con distrito y ${n - lug - dis} sin ubicación. Toca un punto, un círculo o una ruta.`;
  document.querySelectorAll("#anios button[data-d]").forEach(b => b.classList.toggle("activo", +b.dataset.d === desde && +b.dataset.h === hasta));
}

// ---------- tablas y detalle ----------
const corto = s => s.replace(/^EMPRESA DE (TRANSPORTES?|SERVICIOS?)( Y SERVICIOS)?( MULTIPLES)?\s*/i, "")
  .replace(/^EMP DE SERV DE TRANSP\s*/i, "").replace(/\s*(SOCIEDAD ANONIMA|S\.?\s?A\.?C?\.?)( - .*)?$/i, "")
  .replace(/^[\s,.-]+/, "") || s;
function tablas() {
  const pd = {};
  enPeriodo.forEach(a => { if (!a.d) return; const x = pd[a.d] = pd[a.d] || { n: 0, m: 0, l: [] }; x.n++; x.m += a.m; x.l.push(a); });
  const td = Object.entries(pd).sort((a, b) => b[1].n - a[1].n).slice(0, 10);
  document.getElementById("t-distritos").innerHTML = td.map(([d, x], i) =>
    `<tr data-i="${i}"><td class="e">${esc(d)}</td><td class="n">${x.n}</td><td class="n">${x.m}</td></tr>`).join("")
    || `<tr><td colspan="3" class="nota">Sin ataques en el periodo.</td></tr>`;
  document.querySelectorAll("#t-distritos tr[data-i]").forEach(tr => tr.onclick = () => {
    const [d, x] = td[+tr.dataset.i]; mostrarAtaques(`${d}: ${x.n} ataques en el periodo`, x.l);
    const pts = x.l.filter(a => a.lat).map(a => [a.lat, a.lon]);
    if (pts.length) mapa.fitBounds(L.latLngBounds(pts).pad(.8), { maxZoom: 14 });
  });
  document.getElementById("th-ruta").textContent = { pond: "Repartidos", pos: "Posibles", seg: "Seguros" }[medida];
  const tr = Object.entries(D.rutas).filter(([, r]) => r[medida] > 0)
    .sort((a, b) => b[1][medida] - a[1][medida] || b[1].pos - a[1].pos).slice(0, 15);
  document.getElementById("t-rutas").innerHTML = tr.map(([c, r]) =>
    `<tr data-ruta="${c}"><td><span class="chip" style="background:${colorClase(clase(r[medida]))}"></span>${c}</td>` +
    `<td class="e" title="${esc(r.empresa)}">${esc(corto(r.empresa))}${r.estado === "retirada" ? " <span class='nota'>(retirada)</span>" : ""}</td>` +
    `<td class="n">${fmt(r[medida])}</td></tr>`).join("") || `<tr><td colspan="3" class="nota">Sin ataques con ruta en el periodo.</td></tr>`;
  document.querySelectorAll("#t-rutas tr[data-ruta]").forEach(t => t.onclick = () => elegirRuta(t.dataset.ruta, true));
  const em = {};
  for (const r of Object.values(D.rutas)) {
    const k = r.ruc || r.empresa; if (!k) continue;
    const e = em[k] = em[k] || { nombre: r.empresa, rutas: 0, pond: 0 };
    if (r.estado !== "retirada") e.rutas++; e.pond += r.pond;
  }
  const te = Object.values(em).filter(e => e.pond > 0).sort((a, b) => b.pond - a.pond).slice(0, 12);
  document.getElementById("t-empresas").innerHTML = te.map((e, i) =>
    `<tr data-i="${i}"><td class="e" title="${esc(e.nombre)}">${esc(corto(e.nombre))}</td><td class="n">${e.rutas}</td><td class="n">${fmt(e.pond)}</td></tr>`).join("")
    || `<tr><td colspan="3" class="nota">Sin ataques con empresa en el periodo.</td></tr>`;
  document.querySelectorAll("#t-empresas tr[data-i]").forEach(t => t.onclick = () => {
    document.getElementById("buscar").value = te[+t.dataset.i].nombre; buscar(); });
}
function detalle(html) {
  const d = document.getElementById("detalle");
  d.style.display = "block"; d.innerHTML = `<button class="cerrar" aria-label="Cerrar">×</button>` + html;
  d.querySelector(".cerrar").onclick = () => { d.style.display = "none"; seleccion = null; pintarRutas(); };
  d.scrollIntoView({ block: "nearest", behavior: "smooth" });
}
function mostrarAtaques(titulo, lista) {
  const items = [...lista].sort((a, b) => b.f.localeCompare(a.f)).map(a => {
    const enl = a.u.map((u, i) => `<a href="${esc(u)}" target="_blank" rel="noopener">nota ${i + 1}</a>`).join(" · ");
    return `<li><b>${esc(a.f)}</b>${a.m ? " · con muerte" : ""}${a.r ? ` · ${esc(a.r)}` : ""}` +
      `${a.e ? `<br>Empresa en la noticia: ${esc(a.e)}` : ""}${a.l ? `<br>Lugar: ${esc(a.l)} (aprox.)` : ""}` +
      `${a.c.length ? `<br>Rutas candidatas: ${a.c.join(", ")}` : ""}<br>${enl}</li>`;
  }).join("");
  detalle(`<b>${esc(titulo)}</b><ul>${items}</ul>`);
}
function elegirRuta(cod, zoom) {
  seleccion = cod; pintarRutas();
  const r = D.rutas[cod], lista = enPeriodo.filter(a => a.c.includes(cod));
  detalle(`<b>Ruta ${cod}</b>${r.apodos ? ` · ${esc(r.apodos)}` : ""}<br>${esc(r.empresa)}
    <dl><dt>Ataques</dt><dd>${etiq(r)}</dd><dt>Estado</dt><dd>${r.estado}</dd>
    <dt>Recorrido</dt><dd>${esc(r.distrito_inicio)} – ${esc(r.distrito_fin)}${r.km_trazado ? ` · ${(+r.km_trazado).toFixed(1)} km (ida y vuelta)` : ""}</dd>
    <dt>Vehículo</dt><dd>${esc(r.carroceria)}${r.flota_requerida ? ` · flota ${r.flota_requerida}` : ""}</dd>
    <dt>RUC</dt><dd>${esc(r.ruc)}</dd></dl>
    ${lista.length ? `<ul>${lista.slice().reverse().map(a => `<li>${esc(a.f)} · ${esc(a.d || "sin distrito")}${a.m ? " · con muerte" : ""}${a.c.length > 1 ? ` · 1 de ${a.c.length} rutas candidatas` : ""}</li>`).join("")}</ul>` : ""}
    ${capas[cod] ? "" : "<p class='nota'>Ruta retirada: sin trazado actual.</p>"}`);
  if (zoom && capas[cod]) mapa.fitBounds(capas[cod].getBounds(), { padding: [30, 30] });
}
function buscar() {
  seleccion = null; pintarRutas();
  const q = document.getElementById("buscar").value.trim(), b = L.latLngBounds([]);
  const vis = Object.values(capas).filter(c => grupoRutas.hasLayer(c));
  if (q && vis.length && vis.length < 60) { vis.forEach(c => b.extend(c.getBounds())); mapa.fitBounds(b, { padding: [30, 30] }); }
}
function leyenda() {
  document.getElementById("leyenda").innerHTML = `<div><i style="background:${css("--cero")}"></i>0</div>` +
    ETIQ[medida].map((t, i) => `<div><i style="background:${css("--s" + (i + 1))}"></i>${t}</div>`).join("");
}

// ---------- controles ----------
const rDesde = document.getElementById("desde"), rHasta = document.getElementById("hasta");
rDesde.max = rHasta.max = meses.length - 1;
rDesde.oninput = () => { desde = Math.min(+rDesde.value, hasta); parar(); actualizar(); };
rHasta.oninput = () => { hasta = Math.max(+rHasta.value, desde); parar(); actualizar(); };
const svgH = document.getElementById("hist");
let arrastre = null;
const mesEn = e => { const r = svgH.getBoundingClientRect();
  return Math.max(0, Math.min(meses.length - 1, Math.floor((e.clientX - r.left) / r.width * meses.length))); };
svgH.addEventListener("pointerdown", e => { arrastre = mesEn(e); desde = hasta = arrastre; parar(); actualizar(); svgH.setPointerCapture(e.pointerId); });
svgH.addEventListener("pointermove", e => { if (arrastre === null) return; const i = mesEn(e);
  if (Math.min(arrastre, i) !== desde || Math.max(arrastre, i) !== hasta) { desde = Math.min(arrastre, i); hasta = Math.max(arrastre, i); actualizar(); } });
svgH.addEventListener("pointerup", () => { arrastre = null; });
const cajaAnios = document.getElementById("anios");
function boton(txt, d, h) { const b = document.createElement("button"); b.textContent = txt; b.dataset.d = d; b.dataset.h = h;
  b.onclick = () => { desde = d; hasta = h; parar(); actualizar(); }; cajaAnios.appendChild(b); }
boton("Todo", 0, meses.length - 1);
[...new Set(meses.map(m => m.slice(0, 4)))].forEach(y => {
  const idx = meses.map((m, i) => m.startsWith(y) ? i : -1).filter(i => i >= 0); boton(y, idx[0], idx[idx.length - 1]); });
const play = document.createElement("button"); play.textContent = "▶ Ver avance"; cajaAnios.appendChild(play);
let timer = null;
function parar() { if (timer) { clearInterval(timer); timer = null; play.textContent = "▶ Ver avance"; } }
play.onclick = () => {
  if (timer) return parar();
  desde = 0; hasta = 0; actualizar(); play.textContent = "❚❚ Pausa";
  timer = setInterval(() => { if (hasta >= meses.length - 1) return parar(); hasta++; actualizar(); }, 700);
};
document.getElementById("medida").onchange = e => { medida = e.target.value; leyenda(); actualizar(); };
["c-ataques", "c-rutas", "ceros"].forEach(id => document.getElementById(id).onchange = actualizar);
document.getElementById("c-distritos").onchange = e => e.target.checked ? capaDistritos.addTo(mapa) : capaDistritos.remove();
document.getElementById("buscar").oninput = buscar;
addEventListener("resize", histograma);
document.getElementById("pie").textContent = `Generado el ${D.meta.generado} con scripts/mapa.py.`;
leyenda(); actualizar();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
