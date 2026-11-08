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
| GitHub | https://github.com/rodrigohermoza/Mapa_ataques_extorsion (**público**), rama `main`. Commits solo a nombre de Rodrigo, sin `Co-Authored-By`. |
| `docs/` | Cuaderno del proyecto. Índice en `docs/README.md`. |
| `BITACORA.md` | Log por sesión: qué se hizo y cómo retomar. |
| `params.json` | Consultas a Google Noticias y pausa entre peticiones. Cambiar aquí, no en el código. |
| `Makefile` | `make diario` (lo corre Rodrigo los fines de semana; retoma desde la última nota y procesa, ~20–60 s), `make procesar`, `make historico` (~70 min). |
| `scripts/recolectar.py` | Google Noticias RSS → `data/raw/noticias.jsonl` (solo se agregan notas nuevas, nunca se borra). Usa `curl` (P-05). |
| `scripts/extraer.py` | Titulares → filtro → distrito, empresa, rol, víctimas → agrupa notas del mismo hecho → `data/processed/ataques.csv` y `notas_clasificadas.csv`. Sin IA. |
| `scripts/validar.py` | Compara con el Ministerio Público → `results/validacion.md` (cobertura y ranking de empresas). |
| `scripts/lineas.py` | Directorio de rutas (blog infotransportenlima) → `data/processed/lineas.csv`: código ATU, sobrenombres, empresa. También `buscar()`, que usa `extraer.py` para llenar `codigos_ruta` y `cruce_ruta` en `ataques.csv`. |
| `scripts/rutas_atu.py` | Tabla oficial de 462 rutas del Plan Regulador (código antiguo ↔ nuevo ↔ empresa) + sobrenombres del blog → `data/processed/rutas_atu.csv`. |
| `solicitudes/` | Borradores de solicitudes de acceso a la información (Ley 27806). Rodrigo las envía; aquí se anota el seguimiento. |
| `data/raw/rutas/` | Lista de rutas del blog (190 KB) y Plan Regulador de Rutas 2024 de la ATU (8.9 MB). |
| `data/raw/` | `noticias.jsonl` (1 891 notas, 2.2 MB al 2026-11-07) y log del histórico. |
| `data/processed/`, `results/` | Se regeneran con `make procesar`. |

Todo con Python estándar, salvo `scripts/rutas_atu.py`, que usa `pypdf` del venv `~/.venvs/Mapa-crimen` (`.venv` es un enlace; instalar con `uv pip install --python .venv/bin/python pypdf`).

## Reglas de Rodrigo (no negociables)
- **Todo gratis** (datos, herramientas, hosting).
- **No instalar ni descargar** datasets ni paquetes sin aprobación, indicando qué es y cuánto pesa.
- Entornos fuera de iCloud: venv en `~/.venvs/Mapa-crimen` con `.venv` como enlace simbólico (ver `../../Personal/Información y manejo/LEEME.md`).
- Si se usan agentes, reportar función, qué hizo, tokens y tiempo (`docs/08-agentes.md`).
- Commits sin coautoría de Claude: nunca agregar `Co-Authored-By` ni menciones a Claude en mensajes de commit o PR.
- No modificar otros proyectos (solo leer).
- Presentar el plan antes de cambios grandes.
- Datos sensibles: son víctimas reales. No publicar nombres de víctimas; el análisis es por línea/empresa/zona.

## Proyectos relacionados (solo leer)
- `../../Personal/Pokemon_Filogenetico/` y `../../Personal/Peptidos-antimicrobianos/` — modelo de estructura de docs y tubería reproducible (Makefile, params.yaml, uv).
- `../../Personal/denge-clima/` — otro proyecto de datos geográficos del Perú.
