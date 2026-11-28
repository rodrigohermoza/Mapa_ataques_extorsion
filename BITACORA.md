# Bitácora

## 2026-11-07 · Sesión 1: arranque y búsqueda de fuentes
- Revisada la estructura de `Personal/Pokemon_Filogenetico` y `Personal/Maestrias y programas` (CLAUDE.md, BITACORA, docs numerados) para replicarla. No se modificó nada fuera de esta carpeta.
- Creados: `CLAUDE.md`, `README.md`, `BITACORA.md`, `docs/` (00–08).
- Búsqueda de fuentes (detalle en `docs/04-datos-fuentes.md`):
  - Ataques: no hay base abierta por línea. El Observatorio de Criminalidad del Ministerio Público da 214 atentados (ago-2024 a may-2026) agregados por zona. SIDPOL es reservado. La base por línea habría que armarla desde noticias.
  - Rutas: OpenStreetMap tiene 672 relaciones de bus en Lima-Callao (consulta de solo etiquetas, ~150 KB, borrada). No hay GTFS público oficial; Plaza Cívica hizo uno con la ATU pero no está publicado.
- `datosabiertos.gob.pe` bloquea `curl` (P-01).
- Nada instalado ni descargado. Agentes: 1 (ver `docs/08-agentes.md`).
- Cómo retomar: `docs/00-retomar.md` y responder las preguntas de `docs/07-pendientes.md`.

## 2026-11-07 · Sesión 1b: boletines y prueba de automatización
- El autor: si no hay base de datos, mantenerla a mano sería tedioso; seguir solo si se puede automatizar (D-03). Dio permiso para revisar los boletines.
- Descargados a la carpeta temporal de la sesión (no al proyecto): boletín del Observatorio vía LP Derecho (6.7 MB) y Boletín Oficial N.º 6-2026 (8.1 MB). Sin herramientas de PDF → script propio con biblioteca estándar (P-04).
- Resultado: **no hay desglose por línea ni empresa.** Sí por año, unidad, distrito, rol (cobradores: 6 muertos y 9 heridos en 214 atentados). Su método: seguimiento de noticias + verificación con Medicina Legal y carpetas fiscales.
- Probado Google Noticias RSS: 29 notas del último mes, con empresa y distrito en el titular; histórico accesible por ventanas (10 notas por rango). GDELT limita a 1 petición / 5 s.
- Al abrir el PDF en el navegador integrado salió un diálogo de descarga para el autor (no se guardó nada desde ahí).
- Nada instalado. Agentes: ninguno en esta parte.

## 2026-11-07 · Sesión 1c: recolector automático y primera base
- El autor aprobó escribir el recolector y bajar el histórico (límite: avisar si pasa de 100 MB; se estimó ≤50 MB de tráfico y bajó 2.2 MB).
- `params.json`, `scripts/recolectar.py` (Google Noticias RSS por ventanas de 7 días que se parten en días si llegan al tope), `scripts/extraer.py`, `scripts/validar.py` y `Makefile`. Solo Python estándar y `curl` (P-05).
- Histórico ago-2024 → 7-nov-2026: 1 891 notas, ~70 min, 0 errores.
- Primera versión contaba el 163% de lo oficial (P-06). Tras filtros y D-04/D-05: 342 hechos y **71% de cobertura** frente a los ataques con víctimas del Ministerio Público sin mototaxis (R-01). 63% con empresa y 87% con distrito.
- Corregido un error: 31/140/112 eran víctimas por año, no atentados (20/107/87).
- Nada instalado. Agentes: ninguno.
- Cómo retomar: `make diario` y ver `docs/00-retomar.md`.
- El autor: `make diario` se corre a mano los fines de semana (D-06). `--diario` ahora retoma desde la última nota bajada (−3 días), así no se pierde nada entre semanas. Probado: 23 s, 11 notas nuevas.

## 2026-11-07 · Sesión 2: búsqueda de rutas de buses
- El autor pidió revisar todas las fuentes de rutas poco a poco, incluida Moovit (usa la app en su iPhone).
- iPhone: no se puede controlar un iPhone físico (solo el simulador).
- Revisadas: datosabiertos.gob.pe (solo Miraflores 2018), TUMI (no carga), una resolución ATU (paraderos, sin rutas), Plan Regulador de Rutas 2024 (no se halló el anexo), Wikipedia (ejemplos sueltos).
- Moovit: leídas sus condiciones para Perú en el navegador; prohíben armar una base descargando su contenido de forma sistemática y usar robots. Descartado.
- Un intento de `curl` con user-agent de navegador contra datosabiertos fue bloqueado por el clasificador de permisos (evasión de bloqueo de bots); se usó el navegador integrado.
- OSM (solo etiquetas, 150 KB, en la carpeta temporal): 671 rutas; 124 con operador; sobrenombres en `alt_name`; cruce con el ranking ~29% de los ataques con empresa.
- Descargado: solo 1 PDF de la ATU (340 KB) y las etiquetas de OSM, ambos en la carpeta temporal de la sesión.
- Agentes: 1 web-fetch (condiciones de Moovit; 18 231 tokens, 27 s; no logró leer el texto, se leyó luego en el navegador).

## 2026-11-07 · Sesión 2b: rutas desde ATU y otras fuentes
- El autor pidió buscar soluciones en la ATU, el MTC y las empresas.
- Encontrado el **Plan Regulador de Rutas 2024** (Res. 282-2024-ATU/PE) con fichas técnicas; gob.pe bloquea la página (418), pero el PDF del plan sí baja del CDN: 8.9 MB, guardado. No se puede leer sin herramientas (P-07).
- Encontrado el blog **infotransportenlima** con el directorio de 410 rutas (código ATU, sobrenombre, empresa) y una página por ruta con el recorrido calle por calle. Guardada la lista (190 KB) y probada una página por ruta (en la carpeta temporal).
- `scripts/lineas.py` → `data/processed/lineas.csv`. Cruce: 106 de 141 ataques con empresa (75%) con código de ruta.
- OSM tiene trazado de solo 53 de las 410 rutas.
- Agentes: 1 web-fetch (lectura del blog; 25 556 tokens, 31 s).

## 2026-11-07 · Sesión 2c: páginas por ruta y cruce con ataques
- El autor aprobó bajar las ~410 páginas por ruta del blog (~60 MB). Antes de descargar, se revisó el feed de Blogger: el blog tiene 16 entradas y la única página de ruta es la 1001. **No se descargó nada** (solo dos feeds JSON, 63 KB).
- `lineas.py` ahora tiene `buscar()` (sinónimos, familias de línea, coincidencias aproximadas). `extraer.py` agrega `codigos_ruta` y `cruce_ruta`; `validar.py` muestra los códigos en el ranking; `make procesar` corre también `lineas.py`.
- Resultado: 167 de 216 ataques con empresa (77%) con código ATU.
- Agentes: ninguno.

## 2026-11-07 · Sesión 2d: pypdf y tabla oficial de rutas
- El autor aprobó instalar `pypdf`. Venv creado con `mantenimiento.sh venv . python3.12` → `~/.venvs/Mapa-crimen` (`.venv` enlace). pypdf 7.0.0 con `uv pip` (1.9 MB en total).
- Plan Regulador leído: sección 14 = tabla oficial de **462 rutas** (código antiguo, código nuevo, empresa). `scripts/rutas_atu.py` → `rutas_atu.csv`, unido a los sobrenombres del blog.
- `lineas.buscar()` ahora busca también en las razones sociales oficiales. Quitadas coincidencias falsas ("unidad", "Perla Argentina").
- Resultado: **176 de 215 ataques con empresa (82%) con código de ruta.**
- Fichas técnicas: SharePoint de la ATU con login (403); gob.pe bloquea (418). Pendiente.
- `make procesar` corre lineas → rutas_atu (venv) → extraer → validar.
- Agentes: ninguno.

## 2026-11-07 · Sesión 2e: solicitud de fichas técnicas a la ATU
- El autor decidió pedir las fichas técnicas a la ATU (D-07).
- Canal: formulario SAIP de la ATU (soluciones.atu.gob.pe/saip_portal). Borrador en `solicitudes/2026-11-ATU-fichas-tecnicas.md`: versión completa y versión corta, pide fichas técnicas vigentes (282-2024, 055-2025, 099-2025), trazados digitales y relación de rutas vigentes; como alternativa, acceso de lectura al SharePoint. Sin datos personales en el archivo.
- No se envió nada: lo envía el autor.

## 2026-11-07 · Sesión 2f: solicitud enviada y cierre
- El autor envió la solicitud por el SAIP: **exp. [n.° reservado]**, sáb 7-nov 14:26. Texto de 438 caracteres (el formulario permite 500), PDF de sustento de 1 página (generado con Chrome sin ventana desde `solicitudes/*_sustento.html`), unidad SSTR/DO, entrega por correo.
- Incidente: al revisar las opciones del formulario, Claude recargó la pestaña donde el autor lo llenaba y se borró la primera parte. Guardado en la memoria: usar siempre una pestaña nueva.
- Plazos: se tiene por presentada el lun 9-nov; **vence el lun 23-nov-2026**; si no responden, apelar ante el Tribunal de Transparencia en 15 días hábiles (~16-dic).
- El cargo con datos personales queda en Descargas; en el proyecto solo se anota el número de expediente.
- `docs/00-retomar.md` reescrito como resumen completo para retomar.

## 2026-11-08 · Sesión 3: subida a GitHub
- `git init` (rama `main`), `.gitignore` (venv, caché, cargos) y primer commit con 34 archivos (~13 MB), solo a nombre del autor. Push a https://github.com/rodrigohermoza/Mapa_ataques_extorsion.
- Revisión previa: sin datos personales del autor en `solicitudes/` ni en el PDF de sustento.
- Hallazgo: el repositorio es **público** y los titulares de las noticias nombran a víctimas (D-08). El autor decide si se vuelve privado o se limpian esos archivos.
- Agentes: ninguno.
- Decisión: los nombres de víctimas en los titulares se quedan (noticias públicas). Regla de `CLAUDE.md` ajustada.

## 2026-11-08 · Sesión 3b: archivo de noticias
- Problema: solo guardábamos titular y enlace de Google; si el medio borra la nota, se pierde. El autor aprobó archivar (D-09).
- `scripts/archivar.py`: enlace real del medio, texto en `data/raw/articulos/` (fuera de git, derechos de autor) y copia en Internet Archive. Registro público en `data/raw/archivo.jsonl`.
- Prueba con 10 medios: enlace 10/10, texto 7/10, Wayback 9/10, ~5 KB por texto. Wayback tarda ~30-50 s por nota → va aparte (`make wayback`).
- `make diario` ahora incluye `archivar.py`. Pasada de texto de las 1 890 notas restantes lanzada en segundo plano.
- Agentes: ninguno.
- La pasada completa se detuvo: Google respondió 429 tras ~30 notas (P-08). `archivar.py` ahora espera 8 s entre consultas y se detiene solo ante un 429. 44 notas archivadas; el resto se retoma con `make archivar`.

## 2026-11-20 · Sesión 4: seguimiento ATU y borrador de apelación
- Gmail: solo los correos de confirmación del 7-nov; sin respuesta ni prórroga. Consulta externa del SGD: "En proceso", en la SSTR desde el 9-nov. Hoy es el día hábil 9 de 10; vence el lun 23-nov.
- Borrador del recurso de apelación por denegatoria ficta en `solicitudes/2026-11-ATU-apelacion.md` (sin datos personales). Presentar desde el 24-nov; antes sería prematura. Con silencio negativo el Tribunal no exige plazo perentorio, pero se apunta a presentarla dentro de 15 días hábiles (~16-dic; 8 y 9-dic feriados).
- Agentes: 1 web-fetch (leer gob.pe/13540; falló con HTTP 418; ~7 k tokens, 9 s).

## 2026-11-24 · Sesión 5: llegó la respuesta de la ATU
- La ATU respondió el 24-nov, completo. Lo hizo con una carta y un memorando de la SSTR, y un enlace a SharePoint. El autor lo bajó a `data/ATU/`, que agregué al `.gitignore` porque la carta y el memorando traen datos personales.
- Revisión de seguridad: no hay ejecutables, macros (el xlsx no tiene vbaProject), JavaScript en los PDF ni rutas `../` en los ZIP. Descomprimido en `data/ATU/extraido/`.
- Lo que llegó:
  - 445 fichas PDF con texto.
  - Shapefile de 890 polilíneas (445 rutas × ida y vuelta), en UTM 18N con northing negativo.
  - Excel de 445 rutas con RUC. Las tres partes coinciden en las 445 rutas.
- Cruces: 413 rutas en común con `rutas_atu.csv`, 32 nuevas y 49 ya no autorizadas. Los 176 ataques con código de ruta tienen trazado.
- La apelación ya no es necesaria; el borrador queda como modelo.
- Nada instalado ni descargado (el autor bajó los archivos). Sin agentes.
- Cómo retomar: `docs/00-retomar.md`, paso 1 (lector del shapefile → GeoJSON y unión).

## 2026-11-28 · Sesión 6: procesamiento de los datos de la ATU
- Plan aprobado por el autor, con tres decisiones: el GeoJSON va a git, los datos crudos de la ATU también (`data/raw/atu/`) y un ataque con varias rutas candidatas se reparte 1/n (D-10).
- `data/raw/atu/`: ZIP originales del shapefile y de las fichas, y la relación de rutas en CSV. El `.xlsx` queda fuera de git porque sus metadatos traen nombres de dos funcionarios. Las fichas no tienen metadatos personales.
- `scripts/trazados_atu.py` (Python estándar): lee el shapefile desde el ZIP, convierte UTM 18S (northing negativo) a lat/lon y simplifica (612 k → 107 k puntos). Salida: `rutas_trazados.geojson` (2.5 MB) y `rutas_oficiales.csv`. Corrige la codificación del DBF.
- `scripts/fichas_atu.py` (pypdf): vías de cada itinerario → `fichas_atu.csv`. El PDF "RUTA 1030" es copia de la 1130 (P-09).
- `scripts/cruce_rutas.py`: catálogo de 494 rutas y reparto de los 176 ataques con código → `ataques_por_ruta.csv`, `ataques_por_empresa.csv` y `results/rutas_atu.md` (controles: ida y vuelta 445/445, coordenadas en Lima, longitud 440/445; las 5 restantes tienen el campo LONGITUD desactualizado).
- Todo dentro de `make procesar` (~17 s). `ataques.csv` y `validacion.md` no cambiaron.
- Nada instalado ni descargado. Sin agentes.
- **Primer mapa** (`scripts/mapa.py` → `results/mapa.html`, 2.5 MB, datos dentro): rutas coloreadas en escala azul de un solo tono (5 clases + gris para 0) y grosor según ataques; selector de medida (repartidos / posibles / seguros), buscador por ruta o empresa, detalle al tocar una ruta y ranking de 20 rutas y 15 empresas. Revisado en el navegador integrado: escritorio, celular y modo claro y oscuro. El mapa base de CARTO pedía clave (P-10): se usa OpenStreetMap en gris.
- **Mapa publicado** con aprobación del autor: GitHub Pages con origen "GitHub Actions" (`.github/workflows/pages.yml`). El sitio solo contiene el mapa; se vuelve a publicar en cada push que cambie `results/mapa.html`. Dirección: https://rodrigohermoza.github.io/Mapa_ataques_extorsion/
- Cómo retomar: `docs/00-retomar.md` (ataques sin código, capa de distritos).

## 2026-11-28 · Sesión 6b: limpieza de datos personales
- El autor pidió que no quede ningún dato suyo público. Revisión del repositorio y de todo su historial: la carta y el memorando de la ATU **nunca se subieron**; el PDF de sustento no tiene datos personales.
- Se quitaron: el nombre del autor en la documentación (ahora "el autor"), el número de expediente de la solicitud a la ATU y los números de la carta y el memorando (permitían ubicar el trámite).
- El nombre y el correo reales iban en los metadatos de los 11 commits. Decisión del autor (D-11): repositorio borrado y creado de nuevo con un solo commit, autor **Mapa-crimen** y correo privado de GitHub. El historial anterior queda solo en una copia local fuera del proyecto.
- Sin agentes. Nada instalado.

## 2026-11-28 · Sesión 6c: ubicar ataques y filtro por fecha
- El autor pidió ubicar los ataques y filtrar por mes/año. Plan aprobado completo: límites distritales, Nominatim y `make archivar` antes.
- `make archivar --primero-ataques` (opción nueva): Google cortó otra vez tras 28 notas (P-11). Quedan ~60 textos archivados.
- Límites: `peru_distrital_simple.geojson` (1.9 MB, MPL-2.0). Santa Anita y La Punta sin polígono (P-11).
- `scripts/ubicar.py`: extrae lugares del titular y del texto, consulta Nominatim (48 consultas, caché en `geocache.json`), acepta solo dentro del distrito y cerca de la ruta (D-12). Resultado: 27 con lugar, 262 solo distrito, 53 sin ubicar. Una avenida ubicada a 17 km de su ruta se descartó con la regla de ≤1 km.
- `scripts/mapa.py` rehecho: puntos (relleno = con muerte), círculos por distrito, rutas recalculadas para el periodo, histograma mensual arrastrable, botones por año, ▶ avance, tablas de distritos/rutas/empresas del periodo, detalle con enlaces a las notas (sin titulares). Probado en el navegador integrado: escritorio, celular, claro y oscuro.
- Sin agentes. Descargas: solo los límites (1.9 MB), aprobadas.
