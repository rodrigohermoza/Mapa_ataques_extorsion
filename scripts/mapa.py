"""Primer mapa: rutas de la ATU coloreadas por número de ataques → results/mapa.html.

Un solo HTML autocontenido (datos embebidos), que se abre con doble clic. Al verlo carga Leaflet
1.9.4 desde unpkg y el mapa base de OpenStreetMap (en gris) (gratis, con atribución). No hay nada
que instalar.

Entradas: data/processed/rutas_trazados.geojson, ataques_por_ruta.csv, ataques_por_empresa.csv.
Conteo de ataques según D-10 (ponderado 1/n, posibles, seguros).

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


def main():
    geo = json.loads((P / "rutas_trazados.geojson").read_text(encoding="utf-8"))
    rutas = {}
    for r in leer("ataques_por_ruta.csv"):
        d = {k: r[k] for k in CAMPOS}
        d.update(pond=float(r["ataques_ponderados"]), pos=int(r["ataques_posibles"]),
                 seg=int(r["ataques_seguros"]), lineas=[])
        rutas[r["ruta"]] = d
    for f in geo["features"]:
        rutas[f["properties"]["ruta"]]["lineas"] += f["geometry"]["coordinates"]
    empresas = [dict(ruc=e["ruc"], empresa=e["empresa"], rutas=int(e["rutas_vigentes"]),
                     pond=float(e["ataques_ponderados"]), pos=int(e["ataques_posibles"]))
                for e in leer("ataques_por_empresa.csv")]
    ataques = leer("ataques.csv")
    con_codigo = sum(bool(a["codigos_ruta"].strip()) for a in ataques)
    fechas = sorted(a["fecha"] for a in ataques if a["fecha"])
    meta = dict(n_ataques=len(ataques), con_codigo=con_codigo, desde=fechas[0], hasta=fechas[-1],
                generado=datetime.date.today().isoformat(),
                sin_trazado=sorted(c for c, r in rutas.items() if r["pos"] and not r["lineas"]))
    datos = json.dumps({"rutas": rutas, "empresas": empresas, "meta": meta},
                       ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    SALIDA.write_text(PLANTILLA.replace("__DATOS__", datos), encoding="utf-8")
    print(f"{sum(bool(r['lineas']) for r in rutas.values())} rutas con trazado → "
          f"{SALIDA.relative_to(RAIZ)} ({SALIDA.stat().st_size / 1e6:.1f} MB)")


PLANTILLA = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ataques por ruta</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
:root {
  --surface: #fcfcfb; --panel: #ffffff; --border: #e4e3df;
  --text-1: #0b0b0b; --text-2: #52514e; --text-3: #7a7974;
  --cero: #b9b8b2; --hl: #0b0b0b;
  --s1: #86b6ef; --s2: #5598e7; --s3: #2a78d6; --s4: #1c5cab; --s5: #0d366b;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --surface: #1a1a19; --panel: #222221; --border: #3a3a38;
  --text-1: #f0efec; --text-2: #c3c2b7; --text-3: #94938c;
  --cero: #4a4a47; --hl: #ffffff;
  --s1: #184f95; --s2: #256abf; --s3: #3987e5; --s4: #6da7ec; --s5: #b7d3f6;
}}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; background: var(--surface); color: var(--text-1);
  font: 14px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif; }
#app { display: flex; height: 100%; }
#panel { width: 380px; flex: none; overflow-y: auto; background: var(--panel);
  border-right: 1px solid var(--border); padding: 20px 20px 32px; }
#mapa { flex: 1; background: var(--surface); }
h1 { font-size: 20px; line-height: 1.25; margin: 0 0 6px; }
h2 { font-size: 13px; text-transform: uppercase; letter-spacing: .04em; color: var(--text-2);
  margin: 22px 0 8px; }
p { margin: 0 0 8px; color: var(--text-2); }
.nota { font-size: 12px; color: var(--text-3); }
label { display: block; margin: 6px 0; color: var(--text-2); }
select, input[type=search] { width: 100%; padding: 6px 8px; border: 1px solid var(--border);
  border-radius: 6px; background: var(--surface); color: var(--text-1); font: inherit; }
.leyenda { display: flex; gap: 2px; margin-top: 6px; }
.leyenda div { flex: 1; font-size: 11px; color: var(--text-2); text-align: center; }
.leyenda i { display: block; height: 8px; border-radius: 2px; margin-bottom: 3px; }
table { width: 100%; border-collapse: collapse; font-size: 12.5px; table-layout: fixed; }
col.c1 { width: 58px; } col.cn { width: 72px; }
td.e { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
th { text-align: left; font-weight: 600; color: var(--text-2); border-bottom: 1px solid var(--border);
  padding: 4px 4px; }
td { padding: 4px 4px; border-bottom: 1px solid var(--border); vertical-align: top; }
td.n, th.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
tbody tr { cursor: pointer; }
tbody tr:hover { background: var(--border); }
.chip { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 6px;
  vertical-align: -1px; }
#detalle { display: none; margin-top: 14px; padding: 12px; border: 1px solid var(--border);
  border-radius: 8px; }
#detalle b { color: var(--text-1); }
#detalle dl { display: grid; grid-template-columns: auto 1fr; gap: 2px 10px; margin: 8px 0 0;
  font-size: 12.5px; }
#detalle dt { color: var(--text-3); } #detalle dd { margin: 0; }
.leaflet-tile-pane { filter: grayscale(1) contrast(.85) brightness(1.05); opacity: .55; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .leaflet-tile-pane {
  filter: grayscale(1) invert(1) brightness(.75) contrast(.9); opacity: .6; } }
td:first-child { white-space: nowrap; }
.leaflet-tooltip { font: 12px/1.4 system-ui, sans-serif; }
@media (max-width: 760px) {
  #app { flex-direction: column-reverse; }
  #panel { width: 100%; height: 48%; border-right: none; border-top: 1px solid var(--border);
    padding: 14px 16px 24px; }
}
</style>
</head>
<body>
<div id="app">
  <aside id="panel">
    <h1>Ataques al transporte público por ruta</h1>
    <p id="resumen"></p>
    <label>Medida
      <select id="medida">
        <option value="pond">Ataques repartidos (1/n por ruta candidata)</option>
        <option value="pos">Ataques posibles (la ruta es candidata)</option>
        <option value="seg">Ataques seguros (única ruta candidata)</option>
      </select>
    </label>
    <div class="leyenda" id="leyenda"></div>
    <label><input type="checkbox" id="ceros" checked> Mostrar rutas sin ataques</label>
    <label>Buscar ruta o empresa
      <input type="search" id="buscar" placeholder="Ej. 1388, Santa Catalina">
    </label>
    <div id="detalle"></div>
    <h2>Rutas con más ataques</h2>
    <table><colgroup><col class="c1"><col><col class="cn"></colgroup><thead><tr><th>Ruta</th><th>Empresa</th><th class="n" id="th-ruta">Ataques</th></tr></thead>
      <tbody id="t-rutas"></tbody></table>
    <h2>Empresas con más ataques</h2>
    <table><colgroup><col><col class="c1"><col class="cn"></colgroup><thead><tr><th>Empresa</th><th class="n">Rutas</th><th class="n">Repartidos</th></tr></thead>
      <tbody id="t-empresas"></tbody></table>
    <h2>Cómo leerlo</h2>
    <p class="nota">Los ataques salen de titulares de Google Noticias (sin IA), agrupados en hechos.
      Solo los que nombran a la empresa o la línea tienen ruta. Si una noticia solo dice la empresa,
      el ataque queda con varias rutas candidatas: en «repartidos» suma 1/n a cada una; «posibles»
      es el máximo y «seguros» el mínimo. Trazados oficiales de la ATU al 5-nov-2026 (solicitud de
      acceso a la información). Las rutas retiradas no tienen trazado.</p>
    <p class="nota" id="pie"></p>
  </aside>
  <div id="mapa"></div>
</div>
<script>
const D = __DATOS__;
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const CORTES = { pond: [0.5, 1, 2, 3.5], pos: [1, 2, 4, 6], seg: [1, 2, 3, 4] };
const ETIQ = { pond: ["≤0.5", "≤1", "≤2", "≤3.5", ">3.5"], pos: ["1", "2", "3–4", "5–6", "7+"],
               seg: ["1", "2", "3", "4", "5+"] };
const fmt = v => Number.isInteger(v) ? String(v) : v.toFixed(2).replace(/0$/, "");
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
let medida = "pond", seleccion = null;

function clase(v) {
  if (!v) return 0;
  const c = CORTES[medida]; let i = 0;
  while (i < c.length && v > c[i]) i++;
  return i + 1;
}
const color = k => k ? css("--s" + k) : css("--cero");
const ancho = k => [1, 2, 2.5, 3, 4, 5][k];

const mapa = L.map("mapa", { preferCanvas: true, zoomControl: true }).setView([-12.05, -77.0], 11);
// Mapa base: OpenStreetMap estándar en gris (filtro CSS) para que las rutas resalten.
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · Rutas: ATU (5-nov-2026)'
}).addTo(mapa);

const capas = {};
for (const [cod, r] of Object.entries(D.rutas)) {
  if (!r.lineas.length) continue;
  const capa = L.polyline(r.lineas.map(l => l.map(([x, y]) => [y, x])), { interactive: true });
  capa.bindTooltip(() => `<b>Ruta ${cod}</b> · ${esc(r.empresa)}<br>${etiquetaAtaques(r)}`, { sticky: true });
  capa.on("click", () => elegir(cod));
  capa.on("mouseover", () => capa.setStyle({ weight: ancho(clase(r[medida])) + 2 }));
  capa.on("mouseout", () => pintar(cod));
  capas[cod] = capa;
}
const etiquetaAtaques = r => `Repartidos ${fmt(r.pond)} · posibles ${r.pos} · seguros ${r.seg}`;

function pintar(cod) {
  const r = D.rutas[cod], capa = capas[cod], k = clase(r[medida]);
  const visible = (k > 0 || document.getElementById("ceros").checked) && coincide(r, cod);
  if (!visible) { capa.remove(); return; }
  if (!mapa.hasLayer(capa)) capa.addTo(mapa);
  const sel = cod === seleccion;
  capa.setStyle({ color: sel ? css("--hl") : color(k), weight: ancho(k) + (sel ? 2 : 0),
                  opacity: k ? 0.9 : 0.45 });
}
function coincide(r, cod) {
  const q = document.getElementById("buscar").value.trim().toLowerCase();
  return !q || cod.includes(q) || r.empresa.toLowerCase().includes(q) || r.apodos.toLowerCase().includes(q);
}
function pintarTodo() {
  // de menos a más ataques, para que las más atacadas queden encima
  Object.keys(capas).sort((a, b) => D.rutas[a][medida] - D.rutas[b][medida]).forEach(cod => {
    pintar(cod); if (mapa.hasLayer(capas[cod])) capas[cod].bringToFront();
  });
  if (seleccion && capas[seleccion]) capas[seleccion].bringToFront();
}

function leyenda() {
  document.getElementById("leyenda").innerHTML =
    `<div><i style="background:${css("--cero")}"></i>0</div>` +
    ETIQ[medida].map((t, i) => `<div><i style="background:${css("--s" + (i + 1))}"></i>${t}</div>`).join("");
}

function tablas() {
  const nom = { pond: "Repartidos", pos: "Posibles", seg: "Seguros" }[medida];
  document.getElementById("th-ruta").textContent = nom;
  const top = Object.entries(D.rutas).filter(([, r]) => r[medida] > 0)
    .sort((a, b) => b[1][medida] - a[1][medida] || b[1].pos - a[1].pos).slice(0, 20);
  document.getElementById("t-rutas").innerHTML = top.map(([c, r]) =>
    `<tr data-ruta="${c}"><td><span class="chip" style="background:${color(clase(r[medida]))}"></span>${c}</td>` +
    `<td class="e" title="${esc(r.empresa)}">${esc(corto(r.empresa))}${r.estado === "retirada" ? " <span class='nota'>(retirada)</span>" : ""}</td>` +
    `<td class="n">${fmt(r[medida])}</td></tr>`).join("");
  document.querySelectorAll("#t-rutas tr").forEach(tr => tr.onclick = () => elegir(tr.dataset.ruta, true));
  document.getElementById("t-empresas").innerHTML = D.empresas.slice(0, 15).map(e =>
    `<tr data-q="${esc(e.ruc || e.empresa)}"><td class="e" title="${esc(e.empresa)}">${esc(corto(e.empresa))}</td><td class="n">${e.rutas}</td>` +
    `<td class="n">${fmt(e.pond)}</td></tr>`).join("");
  document.querySelectorAll("#t-empresas tr").forEach(tr => tr.onclick = () => {
    const e = D.empresas.find(x => (x.ruc || x.empresa) === tr.dataset.q);
    filtrarEmpresa(e);
  });
}
const corto = s => s.replace(/^EMPRESA DE (TRANSPORTES?|SERVICIOS?)( Y SERVICIOS)?( MULTIPLES)?\s*/i, "")
  .replace(/^EMP DE SERV DE TRANSP\s*/i, "").replace(/\s*(SOCIEDAD ANONIMA|S\.?\s?A\.?C?\.?)( - .*)?$/i, "")
  .replace(/^[\s,.-]+/, "") || s;

function filtrarEmpresa(e) {
  const caja = document.getElementById("buscar");
  caja.value = e.empresa; seleccion = null; pintarTodo(); detalleOff();
  const b = L.latLngBounds([]);
  for (const [c, capa] of Object.entries(capas)) if (mapa.hasLayer(capa) && D.rutas[c].empresa === e.empresa) b.extend(capa.getBounds());
  if (b.isValid()) mapa.fitBounds(b, { padding: [30, 30] });
}

function elegir(cod, zoom) {
  seleccion = cod; pintarTodo();
  const r = D.rutas[cod], d = document.getElementById("detalle");
  d.style.display = "block";
  d.innerHTML = `<b>Ruta ${cod}</b>${r.apodos ? ` · ${esc(r.apodos)}` : ""}<br>${esc(r.empresa)}
    <dl><dt>Ataques</dt><dd>${etiquetaAtaques(r)}</dd>
    <dt>Estado</dt><dd>${r.estado}</dd>
    <dt>Recorrido</dt><dd>${esc(r.distrito_inicio)} – ${esc(r.distrito_fin)}${r.km_trazado ? ` · ${(+r.km_trazado).toFixed(1)} km (ida y vuelta)` : ""}</dd>
    <dt>Vehículo</dt><dd>${esc(r.carroceria)}${r.flota_requerida ? ` · flota ${r.flota_requerida}` : ""}</dd>
    <dt>RUC</dt><dd>${esc(r.ruc)}</dd></dl>
    ${capas[cod] ? "" : "<p class='nota'>Ruta retirada: sin trazado actual.</p>"}`;
  if (zoom && capas[cod]) mapa.fitBounds(capas[cod].getBounds(), { padding: [30, 30] });
}
const detalleOff = () => { document.getElementById("detalle").style.display = "none"; };

const M = D.meta;
document.getElementById("resumen").innerHTML =
  `${M.n_ataques} ataques registrados en noticias entre ${M.desde} y ${M.hasta}; ` +
  `${M.con_codigo} se pudieron asociar a una ruta. Toca una ruta para ver su detalle.`;
document.getElementById("pie").textContent = `Generado el ${M.generado} con scripts/mapa.py.` +
  (M.sin_trazado.length ? ` Rutas atacadas sin trazado (retiradas): ${M.sin_trazado.join(", ")}.` : "");
document.getElementById("medida").onchange = e => { medida = e.target.value; leyenda(); tablas(); pintarTodo(); };
document.getElementById("ceros").onchange = pintarTodo;
document.getElementById("buscar").oninput = () => {
  seleccion = null; detalleOff(); pintarTodo();
  const q = document.getElementById("buscar").value.trim(), b = L.latLngBounds([]);
  const vis = Object.values(capas).filter(c => mapa.hasLayer(c));
  if (q && vis.length < 60) { vis.forEach(c => b.extend(c.getBounds())); mapa.fitBounds(b, { padding: [30, 30] }); }
};
leyenda(); tablas(); pintarTodo();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
