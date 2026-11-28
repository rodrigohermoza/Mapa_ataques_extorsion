# Retomar

**Última actualización:** 2026-11-28 (sesión 6: datos de la ATU, mapa con ataques ubicados y filtro por fecha). Leer primero `../CLAUDE.md`.

## En una frase
Base automática de ataques al transporte de Lima y Callao armada desde Google Noticias (342 hechos; 71% de cobertura frente al Ministerio Público), con código de ruta ATU para el 82% de los ataques que mencionan empresa. **Los trazados oficiales de la ATU (445 rutas) ya están en GeoJSON y cruzados con los ataques** (`results/rutas_atu.md`). **Primer mapa listo: `results/mapa.html`.**

## Estado
**Repositorio:** https://github.com/rodrigohermoza/Mapa_ataques_extorsion (público, rama `main`). Commits con seudónimo (Mapa-crimen). Los titulares de noticias, aunque nombren a víctimas, se quedan públicos (D-08).

**Ataques** (`data/processed/ataques.csv`)
- Fuente: Google Noticias RSS (`params.json`, 3 consultas), ago-2024 → hoy. 1 902 notas → 342 hechos. Sin IA.
- Cobertura frente al Ministerio Público (ataques con víctimas, ago-2024 a may-2026): 117/214 = 55%; **sin mototaxis ni taxis: 117/164 = 71%** (R-01, D-04).
- 87% con distrito y 63% con empresa. Columnas `codigos_ruta` y `cruce_ruta` (exacto / familia / oficial / aproximado).
- Actualización: **El autor corre `make diario` a mano los fines de semana** (D-06). Retoma desde la última nota bajada.

**Rutas**
- `data/processed/rutas_atu.csv`: **tabla oficial de 462 rutas** (Plan Regulador 2024, sección 14): código antiguo, código nuevo (1001–1462) y empresa, más los sobrenombres del blog infotransportenlima (386 de 462).
- `data/processed/lineas.csv`: directorio del blog (410 rutas con sobrenombre y empresa).
- **176 de 215 ataques con empresa (82%) tienen código de ruta.** Sin cruce: Z Buss, El Mandarino, Etcimosa, Acorsa, Midivisa.
- **Trazados oficiales de la ATU** (respuesta SAIP del 24-nov, exp. [n.° reservado]; crudos en `data/raw/atu/`):
  - `rutas_trazados.geojson`: 890 líneas (445 rutas × ida/vuelta) en lat/lon, simplificadas a ~5 m (2.5 MB).
  - `rutas_oficiales.csv`: 445 rutas con RUC, operador, tipo, flota, km, distritos y resolución. `fichas_atu.csv`: vías de cada itinerario (444; la ficha 1030 vino mal, P-09).
  - `ataques_por_ruta.csv`: catálogo de 494 rutas (413 vigentes, 32 nuevas, 49 retiradas) con ataques ponderados / posibles / seguros (D-10). `ataques_por_empresa.csv`: 103 empresas con ataques.
  - 140 rutas con algún ataque. Más atacadas (ponderado): 1388 San Pedro de Pamplona (6), 1084 Santo Cristo (5.5), 1471 Línea Peruana (5). Empresas: Santa Catalina y "Unidos de Pasajeros S.A. 73" (10 cada una).
  - 3 rutas atacadas ya no están autorizadas (1047, 1196, 1335): sin trazado actual.

**Entorno**
- Python estándar para todo, salvo `rutas_atu.py` y `fichas_atu.py` (pypdf 7.0.0 en `~/.venvs/Mapa-crimen`; `.venv` es un enlace).
- `make procesar` (~20 s + consultas nuevas a Nominatim) = lineas → rutas_atu → trazados_atu → fichas_atu → extraer → validar → cruce_rutas → ubicar → mapa. `make diario` = recolectar + procesar.

## Próximos pasos
- **Archivo de noticias (D-09):** `make diario` ahora guarda el texto de cada nota nueva en `data/raw/articulos/` (solo local). Histórico: 44 de 1 902 notas archivadas; Google bloqueó por exceso de consultas (P-08), retomar con `make archivar` tras unas horas. Falta la copia en Internet Archive del histórico: `make wayback` (~20 h; se puede cortar y retomar).
1. **Mapa** (`results/mapa.html`, publicado en https://rodrigohermoza.github.io/Mapa_ataques_extorsion/): ataques como puntos (lugar aproximado) o círculos por distrito, rutas coloreadas por los ataques del periodo, histograma mensual para elegir el periodo, botones por año y ▶ avance mes a mes. **Más puntos exactos:** depende de archivar textos (Google corta tras ~28 notas por corrida, P-11); cada `make diario` suma algunos.
2. **Ataques sin código (166):** proponer rutas con las vías de `fichas_atu.csv` y el distrito del ataque.
3. Revisar a mano los cruces "aproximado" y "oficial" dudosos (p. ej. "estrella" → 4 rutas) y los sobrenombres ambiguos ("La 41" → 4 códigos). Con los recorridos se desambiguan por distrito.
4. Mejorar la cobertura de Lima Este y Lima Noroeste (consultas con nombres de distritos).
5. Mapa final: rutas coloreadas por número de ataques + ranking de empresas.

## Límites conocidos
- El RSS de Google no es oficial; puede cambiar.
- La empresa sale solo del titular.
- El blog de sobrenombres no es oficial (la tabla de la ATU sí).
- Moovit queda descartado: sus condiciones prohíben armar bases con su contenido.
