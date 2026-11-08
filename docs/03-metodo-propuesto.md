# Método propuesto (borrador, sin aprobar)

Idea central: **automatizar el seguimiento de noticias** (lo mismo que hace el Ministerio Público, D-01) para que la base se mantenga sola, sin IA y sin trabajo manual diario.

## 1. Recolector (`scripts/recolectar.py`, solo biblioteca estándar)
- Consulta Google Noticias RSS (y luego GDELT) con 3–5 consultas.
- **Histórico:** ventanas de 1 semana desde ago-2024 (~120 semanas × consultas, con pausas).
- **Diario:** `when:2d`, guardando cada nota en `data/raw/noticias.jsonl` (titular, medio, fecha, URL). Nunca se borra nada.
- Se ejecuta a mano o con una tarea programada local (launchd/cron) — gratis y sin tokens. Pedir aprobación antes de programarla.

## 2. Extracción (`scripts/extraer.py`, sin IA)
De cada titular (y si hace falta del primer párrafo): empresa/línea, distrito, rol de la víctima, muertos/heridos, tipo de unidad. Con diccionarios y patrones (ver `04-datos-fuentes.md`, D3).

## 3. Agrupar notas en hechos → `data/processed/ataques.csv`
Una fila por ataque: `id, fecha, distrito, empresa, linea_popular, tipo_unidad, rol_victima, muertos, heridos, n_notas, urls, revisado`. Lo dudoso queda marcado para revisión.

## 4. Validación
Comparar con el Ministerio Público: atentados con víctimas por año (20 / 107 / 87), por distrito fiscal y por tipo de unidad. Si cubrimos ≥80% del total oficial, la base sirve.

## 5. Rutas y mapa (después)
- Tabla `lineas.csv`: empresa ↔ nombre popular ↔ código ATU ↔ relación OSM.
- Mapa: rutas de OSM coloreadas por número de ataques; ranking de empresas.

## Herramientas
Fases 1–3 con Python estándar (nada que instalar). El mapa necesitará `geopandas`/`folium` o un HTML con Leaflet desde CDN: pedir aprobación con tamaños.
