# Mapa-crimen: ataques al transporte urbano de Lima por línea

Referencia esencial del proyecto. Si se hizo /clear o /compact, leer en este orden:
1. Este archivo (reglas y estructura).
2. `docs/00-retomar.md` (estado actual y próximos pasos).
3. Las últimas entradas de `BITACORA.md`.

Responder siempre en **español**.

**Al terminar cada sesión:** agregar entrada en `BITACORA.md`, actualizar `docs/00-retomar.md` y, si aplica, `docs/04-datos-fuentes.md`, `docs/05-decisiones.md`, `docs/06-problemas-encontrados.md` y `docs/07-pendientes.md`.

## Objetivo
Recopilar los ataques (balaceras, explosivos, asesinatos) contra cobradores, choferes y unidades de transporte público en Lima y Callao, asociarlos a la **empresa / línea / ruta**, y cruzarlos con el trazado de las rutas para ver qué líneas y zonas concentran más ataques. Detalle en `docs/01-objetivos.md`.

## Estructura
| Ruta | Qué es |
|---|---|
| GitHub | https://github.com/rodrigohermoza/Mapa_ataques_extorsion (**público**), rama `main`. Commits con el seudónimo **Mapa-crimen** y el correo privado de GitHub; nunca nombre ni correo reales, ni `Co-Authored-By`. |
| `docs/` | Cuaderno del proyecto. Índice en `docs/README.md`. |
| `BITACORA.md` | Log por sesión: qué se hizo y cómo retomar. |
| `params.json` | Consultas a Google Noticias y pausa entre peticiones. Cambiar aquí, no en el código. |
| `Makefile` | `make diario` (lo corre el autor los fines de semana; retoma desde la última nota, archiva el texto de las nuevas y procesa, ~1–5 min), `make procesar`, `make historico` (~70 min). |
| `scripts/recolectar.py` | Google Noticias RSS → `data/raw/noticias.jsonl` (solo se agregan notas nuevas, nunca se borra). Usa `curl` (P-05). |
| `scripts/archivar.py` | Para que las notas no se pierdan: enlace real del medio + texto → `data/raw/articulos/` (**solo en disco**, fuera de git por derechos de autor) y copia en Internet Archive. Registro en `data/raw/archivo.jsonl` (sí va a git). `make archivar`, `make wayback` (D-09). |
| `scripts/extraer.py` | Titulares → filtro → distrito, empresa, rol, víctimas → agrupa notas del mismo hecho → `data/processed/ataques.csv` y `notas_clasificadas.csv`. Sin IA. |
| `scripts/validar.py` | Compara con el Ministerio Público → `results/validacion.md` (cobertura y ranking de empresas). |
| `scripts/lineas.py` | Directorio de rutas (blog infotransportenlima) → `data/processed/lineas.csv`: código ATU, sobrenombres, empresa. También `buscar()`, que usa `extraer.py` para llenar `codigos_ruta` y `cruce_ruta` en `ataques.csv`. |
| `scripts/rutas_atu.py` | Tabla oficial de 462 rutas del Plan Regulador (código antiguo ↔ nuevo ↔ empresa) + sobrenombres del blog → `data/processed/rutas_atu.csv`. |
| `scripts/trazados_atu.py` | Shapefile de la ATU (UTM 18S, northing negativo) → `data/processed/rutas_trazados.geojson` (lat/lon, simplificado a ~5 m, 2.5 MB) y `rutas_oficiales.csv` (445 rutas con RUC). Python estándar. |
| `scripts/fichas_atu.py` | 445 fichas técnicas PDF → `data/processed/fichas_atu.csv` (vías del itinerario). Usa pypdf. |
| `scripts/cruce_rutas.py` | Catálogo unificado (494 rutas: vigentes, nuevas, retiradas) + reparto de ataques (D-10) → `ataques_por_ruta.csv`, `ataques_por_empresa.csv` y `results/rutas_atu.md`. |
| `scripts/ubicar.py` | Ubica cada ataque (D-12): lugar (avenida, paradero…) del titular o del texto archivado → Nominatim/OpenStreetMap, aceptado solo si cae dentro del distrito (y a ≤1 km de su ruta, si la tiene); si no, centro del distrito. Caché en `data/processed/geocache.json`. → `ataques_ubicados.csv`, `distritos_lima.geojson`. |
| `scripts/mapa.py` | Mapa de ataques (puntos con lugar + círculos por distrito) y rutas coloreadas por ataques (D-10), con filtro por mes/año y ▶ avance → `results/mapa.html`: un solo HTML con los datos dentro (2.5 MB). Verlo con `make ver` → http://127.0.0.1:8765/mapa.html. Usa Leaflet 1.9.4 (unpkg) y OpenStreetMap en gris al verlo. **Publicado en https://rodrigohermoza.github.io/Mapa_ataques_extorsion/** (GitHub Pages; `.github/workflows/pages.yml` lo vuelve a publicar en cada push que cambie el mapa). |
| `data/raw/atu/` | Respuesta de la ATU del 24-nov-2026 (10 MB): shapefile y fichas en sus ZIP originales, y la relación de rutas en CSV. La carta y el memorando quedan en `data/ATU/` (fuera de git). |
| `solicitudes/` | Borradores de solicitudes de acceso a la información (Ley 27806). El autor las envía; aquí se anota el seguimiento. |
| `data/raw/limites/` | Límites distritales del Perú (`peru_distrital_simple.geojson`, 1.9 MB, github.com/juaneladio/peru-geojson, MPL-2.0). Santa Anita y La Punta vienen sin polígono (P-11). |
| `data/raw/rutas/` | Lista de rutas del blog (190 KB) y Plan Regulador de Rutas 2024 de la ATU (8.9 MB). |
| `data/raw/` | `noticias.jsonl` (1 891 notas, 2.2 MB al 2026-11-07) y log del histórico. |
| `data/processed/`, `results/` | Se regeneran con `make procesar`. |

Todo con Python estándar, salvo `scripts/rutas_atu.py` y `scripts/fichas_atu.py`, que usan `pypdf` del venv `~/.venvs/Mapa-crimen` (`.venv` es un enlace; instalar con `uv pip install --python .venv/bin/python pypdf`).

## Reglas del autor (no negociables)
- **Todo gratis** (datos, herramientas, hosting).
- **No instalar ni descargar** datasets ni paquetes sin aprobación, indicando qué es y cuánto pesa.
- Entornos fuera de iCloud: venv en `~/.venvs/Mapa-crimen` con `.venv` como enlace simbólico (ver `../../Personal/Información y manejo/LEEME.md`).
- Si se usan agentes, reportar función, qué hizo, tokens y tiempo (`docs/08-agentes.md`).
- Commits sin coautoría de Claude: nunca agregar `Co-Authored-By` ni menciones a Claude en mensajes de commit o PR.
- No modificar otros proyectos (solo leer).
- Presentar el plan antes de cambios grandes.
- Datos sensibles: son víctimas reales. El análisis es por línea/empresa/zona. Los titulares de noticias públicas pueden quedar tal cual en el repositorio aunque nombren a víctimas (D-08); no agregar nombres por cuenta propia en resultados ni mapas.

## Proyectos relacionados (solo leer)
- `../../Personal/Pokemon_Filogenetico/` y `../../Personal/Peptidos-antimicrobianos/` — modelo de estructura de docs y tubería reproducible (Makefile, params.yaml, uv).
- `../../Personal/denge-clima/` — otro proyecto de datos geográficos del Perú.
