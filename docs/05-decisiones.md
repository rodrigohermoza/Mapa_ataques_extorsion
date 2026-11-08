# Registro de decisiones

Cada entrada: qué se decidió, qué alternativas había, por qué esta, y qué haría cambiar de opinión.

---

## D-01 — La base de ataques se arma desde noticias
**Fecha:** 2026-11-07 · **Estado:** propuesta, falta visto bueno de Rodrigo

No se encontró ninguna base abierta con ataques por línea. Las cifras oficiales están agregadas por zona y el SIDPOL es reservado. Las notas de prensa sí nombran la empresa o línea. Las cifras oficiales sirven para validar la cobertura.

**Alternativas:** solicitud de acceso a la información al Ministerio Público (puede tardar semanas y no garantiza el desglose); ACLED (por confirmar si cubre estos hechos).

**Qué lo cambiaría:** que el Ministerio Público o la ATU entreguen una tabla por línea.

---

## D-02 — Rutas desde OpenStreetMap
**Fecha:** 2026-11-07 · **Estado:** propuesta

Es la única fuente abierta con trazados descargables (672 rutas). Se completa con las resoluciones de la ATU para saber qué empresa opera cada código.

**Qué lo cambiaría:** acceso al GTFS de Plaza Cívica / ATU.

---

## D-03 — Seguir solo si se puede automatizar
**Fecha:** 2026-11-07 · **Estado:** decidido por Rodrigo

Mantener una base a mano es tedioso; el proyecto vale la pena solo si la recolección es automática. La prueba con Google Noticias RSS indica que sí se puede: los titulares traen empresa y distrito, y el histórico se puede recuperar por semanas (ver `04-datos-fuentes.md`, D).

**Qué lo cambiaría:** que el RSS se corte o que la extracción sin IA falle en muchos casos (entonces evaluar IA con costo controlado o abandonar).

**Resultado (2026-11-07):** la automatización funciona: 71% de cobertura frente a las cifras oficiales sin mototaxis (R-01).

---

## D-04 — Comparar solo ataques con víctimas y sin mototaxis
**Fecha:** 2026-11-07 · **Estado:** propuesta

El Ministerio Público cuenta solo ataques con fallecidos o lesionados, e incluye 45 a mototaxis y 5 a taxis. Las consultas de este proyecto buscan buses, combis, cústeres y colectivos, así que la comparación justa es 117 contra 164. Los ataques sin víctimas se guardan igual (columna `con_victimas`).

---

## D-05 — Notas sin distrito ni empresa no forman un hecho propio
**Fecha:** 2026-11-07 · **Estado:** propuesta

Casi siempre son otra versión de un hecho ya contado ("Nuevo atentado contra empresa de transportes en..."). Si no se puede unir a un hecho existente, se descarta. Sin esta regla la base contaba el 163% de lo oficial.

---

## D-06 — La actualización se corre a mano
**Fecha:** 2026-11-07 · **Estado:** decidido por Rodrigo

`make diario` no se programa: Rodrigo lo corre a mano **los fines de semana**. Por eso `--diario` ya no mira solo 3 días: retoma desde la última nota bajada (menos 3 días de margen), sin importar cuánto tiempo haya pasado. Las notas repetidas se descartan.

---

## D-07 — Pedir las fichas técnicas a la ATU por transparencia
**Fecha:** 2026-11-07 · **Estado:** decidido por Rodrigo

Las fichas técnicas del Plan Regulador (recorrido, longitud y flota por ruta) están en un SharePoint de la ATU que pide inicio de sesión, y gob.pe bloquea la página de las copias públicas. Se piden por la Ley 27806 en el formulario SAIP (https://soluciones.atu.gob.pe/saip_portal). También se piden trazados digitales (shapefile/KML/GTFS) y la relación de rutas vigentes. Borrador en `solicitudes/2026-11-ATU-fichas-tecnicas.md`.

**Mientras tanto:** se puede usar OSM para las ~53 rutas que existen (cruce por código antiguo ↔ `old_ref`).

## D-08 — Subir el proyecto a GitHub
**Fecha:** 2026-11-08 · **Estado:** decidido por Rodrigo

Todo el proyecto va a https://github.com/rodrigohermoza/Mapa_ataques_extorsion (rama `main`), con commits solo a nombre de Rodrigo y sin coautoría de Claude. El `.gitignore` excluye `.venv`, `__pycache__`, `.DS_Store` y cualquier cargo (`*cargo*.pdf`). Se revisó que `solicitudes/` no tenga datos personales: solo el número de expediente.

**Nombres de víctimas:** el repositorio es público y algunos titulares (`data/raw/noticias.jsonl`, `data/processed/notas_clasificadas.csv`, columna `titular` de `ataques.csv`) nombran a víctimas. Rodrigo decidió dejarlos: son noticias públicas en internet. Los resultados y el mapa siguen siendo por línea, empresa y zona.

## D-09 — Archivar cada noticia (texto local + Internet Archive)
**Fecha:** 2026-11-08 · **Estado:** decidido por Rodrigo

Los medios pueden borrar las notas, y `noticias.jsonl` solo guarda titular, medio, fecha y el enlace de Google Noticias (que redirige al medio). `scripts/archivar.py`:
1. Decodifica el enlace de Google Noticias al enlace real (página del artículo → firma y hora → `batchexecute`).
2. Guarda solo el texto (título, fecha, cuerpo; JSON-LD `articleBody` o los `<p>`) en `data/raw/articulos/<id>.json`. **Fuera de git**: los textos tienen derechos de autor y el repositorio es público.
3. Pide una copia a Internet Archive (Save Page Now) o usa la que ya exista; el enlace queda en el registro público `data/raw/archivo.jsonl`.

Prueba con 10 notas de distintos medios (2026-11-08): enlace real 10/10, texto 6/10 → 7/10 tras mejorar la extracción, Wayback 9/10, ~5 KB por texto. Sin texto: Facebook (videos), La República (se arma con JavaScript), Perú 21 (403). Para esos queda la copia de Wayback.

Wayback es lento (~30-50 s por nota → ~20 h para todo el histórico), así que va aparte: `make wayback`, que se puede cortar y retomar.
