# Retomar

**Última actualización:** 2026-11-08 (sesión 3: proyecto subido a GitHub). Leer primero `../CLAUDE.md`.

## En una frase
Base automática de ataques al transporte de Lima y Callao armada desde Google Noticias (342 hechos; 71% de cobertura frente al Ministerio Público), con código de ruta ATU para el 82% de los ataques que mencionan empresa. **Se espera la respuesta de la ATU con las fichas técnicas (recorridos) de las rutas.**

## Estado
**Repositorio:** https://github.com/rodrigohermoza/Mapa_ataques_extorsion (público, rama `main`). Commits solo de Rodrigo. Los titulares de noticias, aunque nombren a víctimas, se quedan públicos (D-08).

**Ataques** (`data/processed/ataques.csv`)
- Fuente: Google Noticias RSS (`params.json`, 3 consultas), ago-2024 → hoy. 1 902 notas → 342 hechos. Sin IA.
- Cobertura frente al Ministerio Público (ataques con víctimas, ago-2024 a may-2026): 117/214 = 55%; **sin mototaxis ni taxis: 117/164 = 71%** (R-01, D-04).
- 87% con distrito y 63% con empresa. Columnas `codigos_ruta` y `cruce_ruta` (exacto / familia / oficial / aproximado).
- Actualización: **Rodrigo corre `make diario` a mano los fines de semana** (D-06). Retoma desde la última nota bajada.

**Rutas**
- `data/processed/rutas_atu.csv`: **tabla oficial de 462 rutas** (Plan Regulador 2024, sección 14): código antiguo, código nuevo (1001–1462) y empresa, más los sobrenombres del blog infotransportenlima (386 de 462).
- `data/processed/lineas.csv`: directorio del blog (410 rutas con sobrenombre y empresa).
- **176 de 215 ataques con empresa (82%) tienen código de ruta.** Sin cruce: Z Buss, El Mandarino, Etcimosa, Acorsa, Midivisa.
- **Faltan los recorridos (trazados).** Las fichas técnicas están en un SharePoint de la ATU con login. OSM solo tiene ~53 rutas.
- **Solicitud a la ATU enviada:** exp. **4950-2026-02-0017117** (sáb 7-nov). **Vence el lun 23-nov-2026.** Revisar la Bandeja de Observados del SAIP hasta el 11-nov. Si no responden: apelar ante el Tribunal de Transparencia en 15 días hábiles (~16-dic). Detalle en `../solicitudes/2026-11-ATU-fichas-tecnicas.md`.

**Entorno**
- Python estándar para todo, salvo `rutas_atu.py` (pypdf 7.0.0 en `~/.venvs/Mapa-crimen`; `.venv` es un enlace).
- `make procesar` = lineas → rutas_atu → extraer → validar. `make diario` = recolectar + procesar.

## Próximos pasos
1. **Cuando llegue la respuesta de la ATU:** guardar los archivos en `data/raw/rutas/atu/`, ver el formato (PDF de fichas, shapefile, KML, Excel) y escribir el lector. Unir por código de ruta (1001–1462) con `rutas_atu.csv`.
2. **Mientras tanto (opcional):** bajar los trazados de OSM de las rutas que existan (cruce `codigo_antiguo` ↔ `old_ref` / `ref`). Medir el tamaño antes de descargar y pedir aprobación.
3. Revisar a mano los cruces "aproximado" y "oficial" dudosos (p. ej. "estrella" → 4 rutas) y los sobrenombres ambiguos ("La 41" → 4 códigos). Con los recorridos se desambiguan por distrito.
4. Mejorar la cobertura de Lima Este y Lima Noroeste (consultas con nombres de distritos).
5. Mapa final: rutas coloreadas por número de ataques + ranking de empresas.

## Límites conocidos
- El RSS de Google no es oficial; puede cambiar.
- La empresa sale solo del titular.
- El blog de sobrenombres no es oficial (la tabla de la ATU sí).
- Moovit queda descartado: sus condiciones prohíben armar bases con su contenido.
