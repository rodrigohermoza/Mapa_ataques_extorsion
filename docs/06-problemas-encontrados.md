# Problemas encontrados

Bitácora de lo que falló de verdad. Formato: síntoma, causa, resolución, lección.

---

## P-01 — `datosabiertos.gob.pe` bloquea `curl`
**Fecha:** 2026-11-07 · **Estado:** abierto

**Síntoma:** la API CKAN (`/api/3/action/package_search`) no devuelve JSON y la búsqueda web devuelve HTTP 418.

**Causa:** protección contra bots.

**Resolución:** pendiente; revisar con el navegador integrado.

**Lección:** para portales del Estado, probar primero en el navegador.

---

## P-02 — Overpass responde 406 sin User-Agent
**Fecha:** 2026-11-07 · **Estado:** resuelto

**Síntoma:** `curl` a `overpass-api.de` devolvía una página "406 Not Acceptable".

**Resolución:** enviar un User-Agent propio (`-A "mapa-crimen-research/0.1"`).

---

## P-05 — El Python de python.org no verifica certificados HTTPS
**Fecha:** 2026-11-07 · **Estado:** resuelto

**Síntoma:** `urllib` falla con `CERTIFICATE_VERIFY_FAILED`.

**Causa:** el instalador de python.org no ejecutó `Install Certificates.command`.

**Resolución:** el recolector llama a `curl` (que usa los certificados del sistema). No se instaló `certifi`.

---

## P-06 — Sobreconteo: 163% del total oficial
**Fecha:** 2026-11-07 · **Estado:** resuelto

**Causa:** notas sin distrito que no se unían a su hecho, buses de orquestas, robos, pedradas, notas de seguimiento policial, resúmenes ("tres atentados en 24 horas"), Jicamarca (fuera de Lima Metropolitana) y ataques sin víctimas.

**Resolución:** filtros en `extraer.py`, D-04 y D-05 → 71% (R-01).

**Lección:** validar siempre contra el total oficial; un conteo alto es tan sospechoso como uno bajo.

---

## P-07 — El Plan Regulador de la ATU no se puede leer sin herramientas
**Fecha:** 2026-11-07 · **Estado:** resuelto

**Síntoma:** de 101 páginas salen solo 6 600 caracteres sin códigos de ruta.

**Causa:** fuentes con codificación Identity-H (hace falta el mapa ToUnicode) y mucho contenido en imágenes.

**Resolución:** El autor aprobó `pypdf`. Instalado pypdf 7.0.0 en `~/.venvs/Mapa-crimen` (Python 3.12, 1.9 MB; `.venv` es un enlace) con `uv pip`, porque el venv creado con `uv` no trae `pip`. Con eso se leyó la tabla de equivalencias (B7). **Resuelto.**

---

## P-03 — LP Derecho devuelve 403 a lectores automáticos
**Fecha:** 2026-11-07 · **Estado:** abierto. El artículo del Observatorio hay que leerlo en el navegador.

---

## P-04 — Leer PDF sin herramientas instaladas
**Fecha:** 2026-11-07 · **Estado:** resuelto (parcial)

**Síntoma:** no hay `pdftotext`, `pdftoppm` ni `pypdf`; el lector de PDF de Claude necesita poppler. Abrir el PDF en el navegador integrado disparó un diálogo de descarga.

**Resolución:** script propio con biblioteca estándar (`zlib` + regex sobre los operadores de texto). Funciona para el boletín del Observatorio; el Boletín Oficial N.º 6 usa fuentes con códigos (sale texto parcial). Cuidado: aplicar la regex a flujos de imagen grandes cuelga el script (se filtra por `BT` y tamaño).

**Lección:** si se van a leer muchos PDF, pedir aprobación para `poppler` (brew).

## P-08 — Google limita el decodificado de enlaces (429)
**Fecha:** 2026-11-08

En la pasada completa de `archivar.py`, tras ~30 notas a ~2 s entre consultas, Google respondió 429 y redirigió a `google.com/sorry` (página de "tráfico inusual" con CAPTCHA). Las 300 notas siguientes quedaron como "sin enlace real". El RSS siguió respondiendo (200).

**Solución:** no se intenta saltar el bloqueo. `archivar.py` espera `pausa_google_segundos` (8 s, en `params.json`) entre consultas, se **detiene** al primer 429 y reintenta solo esas notas en la próxima corrida. Se borraron del registro las 302 notas marcadas por el bloqueo. Si vuelve a pasar con 8 s, subir la pausa o correr el histórico por partes (`--limite 200`).

## P-09 — Detalles en los datos de la ATU
**Fecha:** 2026-11-28

1. **Proyección mal declarada:** el `.prj` dice UTM 18N, pero los northing son negativos (−1.38 a −1.30 millones). Es UTM 18S con el falso norte de 10 000 km ya restado: se convierte sin sumar nada. Resultado dentro de Lima (lat −12.49 a −11.73).
2. **Codificación mezclada en el DBF:** latin-1 con partes en UTF-8 ("NÂ°") y letras de otra página de códigos (MARAÐON, JIRËN). `trazados_atu.py` lo corrige (Ð/ð → Ñ, Ë → Ó).
3. **Ficha mal nombrada:** el PDF "RUTA 1030.pdf" es copia de la ficha 1130. `fichas_atu.py` la descarta; para la 1030 solo queda el shapefile. Se podría pedir la ficha correcta a la ATU.
4. **Campo LONGITUD desactualizado** en 5 rutas (1005, 1057, 1286, 1338, 1341): la ficha coincide con el largo del trazado, no con el campo.

## P-10 — El mapa base de CARTO pide clave
**Fecha:** 2026-11-28

Las teselas `basemaps.cartocdn.com` respondieron con "API KEY REQUIRED". Se cambió a las teselas estándar de OpenStreetMap con un filtro CSS gris (y uno invertido en modo oscuro), con su atribución. Su política de uso permite el tráfico bajo de un proyecto así; si el mapa se vuelve popular habrá que buscar otro proveedor gratuito.

## P-11 — Límites sin polígono y nuevo bloqueo de Google
**Fecha:** 2026-11-28

1. En `peru_distrital_simple.geojson`, **Santa Anita y La Punta** no tienen geometría (y Mi Perú no existe: la fuente es anterior a 2014). Para esos dos, el centro se pide a Nominatim y "dentro del distrito" se aproxima como ≤3 km del centro; no se dibuja su límite.
2. `make archivar` volvió a recibir 429 de Google tras 28 notas (pausa de 8 s). Se agregó `--primero-ataques` para que lo poco que se archive en cada corrida sea lo que sirve para ubicar ataques. Con solo ~60 textos archivados, la mayoría de los lugares sale del titular: 27 ataques con lugar, 262 solo con distrito, 53 sin ubicación. Cada `make diario` archivará unas 25 notas más y `ubicar.py` las aprovechará.
