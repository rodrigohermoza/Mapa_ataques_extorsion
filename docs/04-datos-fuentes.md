# Datos y fuentes

Estado al **2026-11-07**. Nada descargado todavía (salvo una consulta de solo etiquetas a OpenStreetMap, ~150 KB, borrada después).

Conclusión corta: **no existe una base de datos abierta de ataques por línea de bus**. Las cifras oficiales existen pero agregadas (por zona o distrito). Las rutas sí están disponibles, sobre todo en OpenStreetMap. Lo más probable es que haya que **construir la base de ataques a partir de noticias**.

---

## A. Ataques al transporte

### A1. Observatorio de Criminalidad del Ministerio Público — la fuente oficial más completa
- **Qué tiene:** 214 atentados contra transporte público en Lima y Callao entre ago-2024 y may-2026; 283 víctimas (152 muertos, 131 heridos); 202 dentro de la unidad. Por zona: Lima Norte 70, Lima Sur 44, Lima Este 43, Lima Centro 21, Callao 18, Lima Noroeste 18. Distritos con más incidencia: SJL, Comas, SJM. 69.3% de las víctimas son choferes; 97.7% con arma de fuego.
- **Cortes anteriores:** 125 atentados ago-2024 a dic-2025; 118 víctimas 2024-2025 (oct-2025).
- **Formato:** boletines PDF. **Revisado el 2026-11-07: no hay desglose por línea ni empresa.** Solo por mes, día, hora, tipo de unidad, distrito fiscal y distrito, forma de ataque, arma y víctimas.
- **Método del propio Ministerio Público:** desde abril de 2025 hace *seguimiento sistemático de noticias* y luego lo verifica con Medicina Legal, sus sistemas de denuncias y las carpetas fiscales. O sea: **la fuente oficial también parte de noticias.**
- **Datos útiles del boletín (ago-2024 a may-2026, 214 atentados con víctimas):**
  - Atentados con víctimas por año: 20 (ago-dic 2024), 107 (2025), 87 (ene-may 2026). Además, 39 sin víctimas en ene-may 2026 (126 en total en 2026).
  - Víctimas por año: 31, 140 y 112 (= 283).
  - Tipo de unidad: bus 51, combi 50, mototaxi 45, minivan colectivo 20, auto colectivo 16, cúster 15, taxi 5.
  - Rol de la víctima: chofer 125 muertos / 71 heridos; pasajero 15 / 43; **cobrador 6 / 9**; jalador 4 / 1.
  - Forma: interceptación 170, falso pasajero 38. Medio: arma de fuego 209, explosivo 13. Vehículo del atacante: moto 129.
  - Noche (18:00–24:00) concentra la mayoría.
- **Enlaces:**
  - Boletín (may-2026) alojado por LP Derecho: https://img.lpderecho.pe/wp-content/uploads/2026/06/Extorsion-Boletin-LPDerecho.pdf
  - Boletín oficial N.º 6-2026 (gob.pe): https://cdn.www.gob.pe/uploads/document/file/9451078/7740401-boletin-oficial-n-6-2026.pdf
  - Nota resumen: https://www.expreso.com.pe/actualidad/fiscalia-presenta-reporte-sobre-atentados-al-transporte-publico-152-fallecidos-en-lima-y-callao-san-juan-de-lurigancho-comas-san-juan-de-miraflores-noticia/1297965/
  - https://elperuano.pe/noticia/299079-cifras-del-ministerio-publico-reportan-214-atentados-contra-transportistas
- **Uso:** validar el total de la base propia (si armamos ~214 casos en el mismo periodo, la cobertura es buena) y la distribución por zona.
- **Posible vía para el detalle:** solicitud de acceso a la información pública (Ley 27806, gratis) al Ministerio Público pidiendo la tabla por empresa/línea/distrito/fecha.

### A2. SIDPOL (denuncias policiales, MININTER/PNP)
- Reportes mensuales en PDF, p. ej. https://cdn.www.gob.pe/uploads/document/file/9435842/7729200-reporte-de-denuncias-registradas-en-el-sidpol-a-enero-del-2026.pdf
- Son denuncias de **extorsión** por región/distrito, no ataques a buses. La PNP declaró reservada la información del SIDPOL por 5 años (Infobae, 2025-09-17), así que el detalle no es abierto.
- Presentaciones de MININTER al Congreso con datos de transporte: https://www3.congreso.gob.pe/Docs/comisiones2025/transportes/files/mininter_ppt_06_10_2025.pdf y https://www.congreso.gob.pe/Docs/comisiones2025/transportes/files/20_10_2025_ppt_mininter.pdf (por revisar: pueden traer empresas).
- **Uso:** capa de contexto por distrito (tasa de extorsión), no la base principal.

### A3. datosabiertos.gob.pe / Datacrim (INEI)
- El portal bloquea `curl` (HTTP 418, P-01). Revisar con el navegador integrado si hay datasets de denuncias por distrito.
- Datacrim (INEI) publica estadísticas de criminalidad por distrito. Por revisar.

### A4. ACLED (eventos de violencia georreferenciados)
- Cubre Perú; registro gratuito para uso no comercial. No se confirmó si codifica los ataques a buses (muchos son crimen común, que ACLED no siempre registra). **Por probar** con una cuenta.

### A5. Noticias (la fuente más prometedora para el nivel de línea)
Las notas casi siempre dicen **empresa, línea, distrito, avenida, fecha y tipo de víctima** (chofer, cobrador, pasajero). Ejemplos: Translicsa (SMP), El Tigrillo (SMP, cobrador, ago-2025), Lipetsa (SJM), Línea 20 (Chorrillos), Línea S (Carabayllo, may-2026), Vipusa (Puente Piedra), Nueva América, Consorcio Vía Colonial (Callao, cobrador).
Medios con etiquetas útiles: Caretas (`caretas.pe/tags/cupos/`), Trome, Panamericana 24 Horas, América TV, RPP, Exitosa, La República, Expreso, Infobae Perú, El Popular.
Vías para recopilar (todas gratis):
- Búsqueda manual + planilla (lenta pero precisa).
- RSS / mapas de sitio de los medios filtrando por palabras clave (sicario, bus, cobrador, chofer, cupo, extorsión, empresa de transportes).
- GDELT (API gratuita de noticias, sin descarga masiva): buscar artículos en español sobre Lima + transporte + ataque.
- Extracción de campos (empresa, línea, distrito, fecha, víctimas) desde el texto: con reglas, o con un modelo (pedir aprobación por costo/tokens).

---

## B. Rutas de buses de Lima y Callao

### B1. OpenStreetMap (recomendado para empezar)
- Consulta de prueba (2026-11-07, Overpass, caja de Lima-Callao): **672 relaciones `route=bus`**, 619 con `ref`.
  - 63 del Metropolitano y 23 del SIT (corredores) bien etiquetadas.
  - Muchas con códigos ATU tipo `X-EO65B-I`, `X-SO49A-I`, `X-NO24-I` (zona + número + sentido Ida/Vuelta), casi sin operador.
  - Algunas con número clásico y empresa: `Ruta 1028`, `Ruta 1179`.
- Licencia ODbL (gratis, atribución). Descarga vía Overpass o extracto Geofabrik de Perú (~ 200–300 MB, por medir).
- **Problema:** la cobertura de rutas "convencionales" es parcial y el operador casi nunca está. Hay que construir una tabla de equivalencias código ATU ↔ empresa ↔ nombre popular ("La 50", "El Chino", etc.).

### B2. ATU (Autoridad de Transporte Urbano)
- Publica resoluciones en PDF con rutas autorizadas (códigos, empresa, recorrido en texto), p. ej. https://cdn.www.gob.pe/uploads/document/file/7914096/6662321-d-000298-2025-atu-do-sstr.pdf
- No se encontró un GTFS público oficial. Sirven para la **tabla código ↔ empresa**.
- Posible solicitud de acceso a la información: pedir el GTFS o los trazados (shapefile) de rutas autorizadas.

### B3. GTFS de Plaza Cívica (con ATU, Ualabee, Google)
- https://plazacivica-web.pages.dev/en/casos/digitalizacion-de-datos-de-transporte-urbano-en-lima-y-callao
- Digitalizaron las rutas de Lima y Callao a GTFS (lo usa Google Maps). **No hay enlace de descarga, ni licencia, ni número de rutas.** Se podría escribir para pedirlo.

### B4. Mobility Database
- Solo aparece Aeroexpreso (https://mobilitydatabase.org/feeds/gtfs/mdb-1985). Nada del transporte convencional.

---

## D. Automatización (probado el 2026-11-07)

### D1. Google Noticias RSS — funciona, gratis, sin clave
- URL: `https://news.google.com/rss/search?q=<consulta>&hl=es-419&gl=PE&ceid=PE:es-419`
- Consulta probada: `(chofer OR cobrador OR bus OR combi) (baleado OR asesinado OR atentado OR disparan) Lima when:30d` → 29 notas del último mes. **Los titulares traen empresa y distrito** casi siempre ("Atacan a balazos bus de la empresa La 91 en avenida Guardia Civil", "bus de El Rápido… Cercado de Lima", "Z Buss sufre su séptimo ataque en el año… Puente Piedra").
- Histórico: con `after:AAAA-MM-DD before:AAAA-MM-DD` funciona hacia atrás (probado sep-2024 y ago-2025: Vipusa en Ancón, TransLima en SMP, Huandoy en Carabayllo, El Chino…), pero **devuelve solo 10 notas por rango antiguo**: hay que pedir ventanas cortas (semana o día) y varias consultas.
- Riesgo: Google puede cambiar o limitar el RSS sin aviso. No es una API oficial.

### D1b. Archivo de cada nota (2026-11-08, D-09)
- Enlace real: los enlaces de Google Noticias (`/rss/articles/CBMi…`) ya no llevan la URL codificada. Se abre `news.google.com/articles/<id>`, se leen `data-n-a-sg` (firma) y `data-n-a-ts` (hora) y se llama a `/_/DotsSplashUi/data/batchexecute` (`Fbv4je`/`garturlreq`). Funcionó 10/10 en la prueba. Puede romperse si Google lo cambia.
- Texto: JSON-LD `articleBody` o los `<p>` (lo más largo). Sin texto: Facebook, La República (JavaScript), Perú 21 (403).
- Internet Archive: `archive.org/wayback/available?url=` (¿ya existe copia?) y `web.archive.org/save/<url>` (pedir copia). Gratis, sin cuenta, ~30-50 s por nota.

### D2. GDELT DOC API — funciona pero limita
- Responde "una petición cada 5 segundos". Útil como segunda fuente y para el histórico; por probar con calma.

### D3. Extracción sin IA
- Empresa: diccionario de empresas/nombres populares (resoluciones ATU + lo que vaya saliendo) + patrones `empresa (de transportes)? X`, `bus de (la )?X`, `línea X`.
- Distrito: lista de los 50 distritos de Lima y Callao.
- Rol y desenlace: palabras clave (chofer, cobrador, pasajero; asesinado, herido, baleado).
- Duplicados: el mismo hecho sale en 5–10 medios → agrupar por fecha ±1 día + distrito + empresa.
- Lo que no se resuelva queda en una cola de revisión manual.

### B5. Revisión del 2026-11-07 (sesión 2): ¿dónde hay rutas con sobrenombre y empresa?
| Fuente | Resultado |
|---|---|
| datosabiertos.gob.pe "Rutas de las empresas de transporte público" | Solo Miraflores, 2018, enlace a un portal municipal viejo. **No sirve.** La ATU no publica nada en el portal (búsquedas "ATU rutas", "Autoridad de Transporte Urbano" sin resultados). |
| TUMI Data Hub (copia del anterior) | No carga (ni `curl` ni navegador). Es el mismo dataset de Miraflores. |
| Resoluciones ATU sueltas (`D-000xxx-2025-ATU/DO-SSTR`) | Revisada la 298-2025 (340 KB): trata de paraderos en una avenida y no lista rutas ni empresas. Juntar cientos de PDF no es práctico. |
| Plan Regulador de Rutas (Res. 282-2024-ATU/PE, 27-dic-2024; ajustes 2025) | Sería **la lista oficial completa** (489 rutas, 21 921 vehículos según la prórroga de 2024). No se encontró el anexo publicado. |
| Wikipedia / foros | Solo ejemplos sueltos. |
| **Moovit** (app y web) | Tiene sobrenombres, pero sus condiciones (Perú) prohíben "create a database by systematically downloading and storing all or any of the content" (cláusula ix) y usar robots o procesos automáticos para "retrieve, index, or data-mine" (iii). Vende el acceso por API comercial (moovit.com/maas-solutions/transit-apis/). **Descartado**, salvo consultas manuales puntuales. |
| **OpenStreetMap** | 671 rutas de bus. Etiquetas útiles: `operator` (124, ~60 convencionales con empresa), `alt_name` con sobrenombres ("La 87B", "La F", "La 13"), `old_ref` con el número antiguo (1502, 1611…), `ref` con el código nuevo. Cruce con el ranking: 9 de las 40 empresas, unos 39 de 136 ataques (~29%). Hay coincidencias falsas que revisar (p. ej. "Huandoy" es un paradero del Corredor Amarillo). |

**Conclusión:** la única fuente abierta descargable es OpenStreetMap, con ~30% de cobertura. La fuente completa sería la base de rutas de la ATU (Plan Regulador o su base de datos), que solo se conseguiría pidiéndola por acceso a la información pública (Ley 27806, gratis).

### B6. Directorio de rutas con sobrenombres (2026-11-07, sesión 2b) — **lo más prometedor**
- **Blog infotransportenlima**, "Rutas regulares autorizadas por la ATU", actualizado mar-2026: https://infotransportenlima.blogspot.com/2025/02/lista-rutas-regulares-2025.html
  - Códigos ATU 1001–1494; **410 con nombre**. Cada uno con sobrenombres y empresa: "La 47 (Translima)", "La 50 (San Sebastián)", "Los Chinos / La A (ETUCHISAC)".
  - Guardado en `data/raw/rutas/infotransportenlima_lista_2025.html` (190 KB) → `scripts/lineas.py` → `data/processed/lineas.csv`.
  - **Cruce con la base de ataques: 106 de 141 ataques con empresa (75%) ya tienen código de ruta** (antes 29% con OSM). Faltan, entre otras, El Chino/Los Chinos (sinónimo por arreglar), línea 73, Z Buss, El Mandarino y Etmosa.
  - No es oficial y no cita resolución; dice seguir el Plan Regulador de Rutas. Verificar casos dudosos contra resoluciones de la ATU.
  - **Páginas por ruta:** solo existe la de la ruta 1001 (estado, distritos, flota, km, recorrido calle por calle). El blog tiene 16 entradas en total (feed de Blogger) y las demás rutas del directorio apuntan a "#". **No hay más que descargar ahí.**
  - Cruce mejorado (sinónimos, familias "línea 73" → 73A/73B/73-1, coincidencias aproximadas): **167 de 216 ataques con empresa (77%) con código de ruta** (149 exactos, 10 por familia, 8 aproximados por revisar). Sin cruce: Z Buss, El Mandarino, Etcimosa, Acorsa, Midivisa…
  - Ambigüedad: algunos sobrenombres los usan varias empresas (p. ej. "La 41" → 4 códigos). Se resolvería con los distritos de cada ruta (hace falta el recorrido).
- **Plan Regulador de Rutas 2024 (oficial)**, Res. 282-2024-ATU/PE: https://cdn.www.gob.pe/uploads/document/file/7433554/6332854-plan-regulador-de-rutas-2024.pdf (8.9 MB, 101 páginas, guardado en `data/raw/rutas/`). El texto usa fuentes con códigos (Identity-H) y 107 imágenes: el extractor propio no lo lee (P-07). Las fichas técnicas (15.7 MB) y sus adecuaciones de 2025 (4.9 + 4.7 MB) están en gob.pe, que bloquea la página (418); falta su enlace directo al CDN.
- **Trazados:** de las 410 rutas, solo **53** aparecen en OpenStreetMap.

### B7. Tabla oficial de la ATU (2026-11-07, sesión 2d) — **fuente principal de rutas**
- Plan Regulador de Rutas 2024, **sección 14 "Cuadro de equivalencia de código de ruta"** (págs. 87–96), leída con `pypdf` (P-07 resuelto).
- **462 rutas** (n.º 1–462 sin huecos): código antiguo (p. ej. 1506, OM75), **código nuevo del Plan (1001–1462)** y **razón social de la empresa** (456 con empresa).
- `scripts/rutas_atu.py` → `data/processed/rutas_atu.csv`, unida a los sobrenombres del blog (386 de 462 con sobrenombre).
- El código antiguo sirve para cruzar con `old_ref` de OpenStreetMap y con prensa antigua.
- Cruce con ataques (sobrenombre del blog + razón social oficial): **176 de 215 ataques con empresa (82%) con código de ruta**. Sin cruce: Z Buss, El Mandarino, Etcimosa, Acorsa, Midivisa (no figuran en la tabla con ese nombre; pueden ser informales u operar con otra razón social).
- **Fichas técnicas** (recorrido, flota, longitud por ruta): el Plan las enlaza a un SharePoint de la ATU (`atugobpe.sharepoint.com/sites/PLANREGULADORDERUTAS/...FICHAS TECNICAS`) que pide inicio de sesión (HTTP 403). Las versiones públicas están en gob.pe (Res. 282-2024: 15.7 MB; Res. 055-2025: 4.9 + 4.7 MB), pero la página bloquea el acceso (418) y no se encontró el enlace directo al CDN.

## C. Capas de contexto
- Límites distritales (INEI / GADM / OSM), población por distrito (censo 2017, INEI).
