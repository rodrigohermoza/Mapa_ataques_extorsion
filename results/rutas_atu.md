# Rutas oficiales de la ATU: controles y cruce con ataques

Generado por `scripts/cruce_rutas.py` (`make procesar`). Fuente: respuesta SAIP de la ATU del 2026-11-24 (shapefile al 5-nov-2026, fichas técnicas y relación de rutas).

## Controles de calidad

| Control | Resultado |
|---|---|
| Rutas en el shapefile / fichas / Excel con RUC | 445 / 444 / 445 |
| Rutas sin ficha técnica válida | 1030 (el PDF «RUTA 1030» que envió la ATU es copia de la ficha 1130) |
| Rutas con ida y vuelta | 445 de 445 |
| Coordenadas dentro de Lima y Callao | sí (lat -12.494 a -11.726, lon -77.176 a -76.667) |
| Longitud del trazado vs. campo LONGITUD (±5 %) | 440 de 445 coinciden |
| Código antiguo distinto entre Plan 2024 y shapefile | 0  |
| Catálogo unificado | 494 rutas: 413 vigentes, 32 nuevas, 49 retiradas |

Rutas cuya longitud no cuadra (km): en todas, la ficha técnica coincide con el trazado, así que el desactualizado es el campo LONGITUD del shapefile.

| Ruta | LONGITUD shapefile | Ficha | Trazado |
|---|---|---|---|
| 1005 | 63.04 | 72.47 | 72.49 |
| 1057 | 83.36 | 78.58 | 78.62 |
| 1286 | 108.75 | 96.30 | 96.36 |
| 1338 | 81.02 | 91.98 | 92.00 |
| 1341 | 81.85 | 88.68 | 88.71 |

## Cruce con ataques

- Ataques: 342; con código de ruta: 176; con al menos una ruta con trazado: 176.
- Peso repartido entre rutas: 176.0 (debe ser igual a 176).
- Rutas retiradas que aparecen en ataques (sin trazado actual): 1047, 1196, 1335.
- Rutas con algún ataque: 140 de 494.

### 15 rutas con más ataques (ponderados)

| Ruta | Empresa | Estado | Ponderados | Posibles | Seguros |
|---|---|---|---|---|---|
| 1388 | EMPRESA DE TRANSPORTES Y SERVICIOS SAN PEDRO DE PAMPLONA S.A | vigente | 6.00 | 6 | 6 |
| 1084 | EMPRESA CONSORCIO DE TRANSPORTES SANTO CRISTO S.A. - E.C.T.  | vigente | 5.50 | 7 | 4 |
| 1471 | LINEA PERUANA DE TRANSPORTES SA | nueva | 5.00 | 5 | 5 |
| 1097 | EMPRESA DE TRANSPORTES SANTO CRISTO DE PACHACAMILLA SOCIEDAD | vigente | 4.11 | 5 | 4 |
| 1107 | EMPRESA DE TRANSPORTES ROLUESA S.A.C. | vigente | 4.00 | 4 | 4 |
| 1231 | EMPRESA DE TRANSPORTES,SERVICIOS,COMERCIALIZADORA,IMPORTADOR | vigente | 4.00 | 4 | 4 |
| 1065 | EMPRESA DE TRANSPORTES NUEVO HORIZONTE SOCIEDAD ANONIMA | vigente | 3.50 | 5 | 2 |
| 1185 | EMPRESA DE TRANSPORTES URBANOS LOS CHINOS S.A. | vigente | 3.50 | 7 | 0 |
| 1239 | EMPRESA DE SERVICIOS MULTIPLES "EL CONDOR" SOCIEDAD ANONIMA  | vigente | 3.50 | 7 | 0 |
| 1025 | EMPRESA DE TRANSPORTES UNIDOS DE PASAJEROS S.A 73 | vigente | 3.33 | 10 | 0 |
| 1057 | EMP DE SERV DE TRANSP STA CATALINA S A | vigente | 3.33 | 10 | 0 |
| 1059 | EMP DE SERV DE TRANSP STA CATALINA S A | vigente | 3.33 | 10 | 0 |
| 1108 | EMP DE SERV DE TRANSP STA CATALINA S A | vigente | 3.33 | 10 | 0 |
| 1111 | EMPRESA DE TRANSPORTES UNIDOS DE PASAJEROS S.A 73 | vigente | 3.33 | 10 | 0 |
| 1244 | EMPRESA DE TRANSPORTES UNIDOS DE PASAJEROS S.A 73 | vigente | 3.33 | 10 | 0 |

### 15 empresas con más ataques (ponderados)

| Empresa | RUC | Rutas vigentes | Ponderados | Posibles |
|---|---|---|---|---|
| EMP DE SERV DE TRANSP STA CATALINA S A | 20100830362 | 3 | 10.00 | 10 |
| EMPRESA DE TRANSPORTES UNIDOS DE PASAJEROS S.A 73 | 20134161176 | 3 | 10.00 | 10 |
| EMPRESA DE TRANSPORTES Y SERVICIOS VIRGEN DE LA PUERTA S.A. | 20156930963 | 3 | 6.00 | 6 |
| EMPRESA DE TRANSPORTES Y SERVICIOS SAN PEDRO DE PAMPLONA S.A | 20113339072 | 2 | 6.00 | 6 |
| TRANSLIMA S.A. | 20136617746 | 6 | 5.50 | 6 |
| EMPRESA CONSORCIO DE TRANSPORTES SANTO CRISTO S.A. - E.C.T.  | 20600097505 | 1 | 5.50 | 7 |
| LINEA PERUANA DE TRANSPORTES SA | 20191479247 | 1 | 5.00 | 5 |
| EMPRESA DE TRANSPORTES SANTO CRISTO DE PACHACAMILLA SOCIEDAD | 20102110421 | 1 | 4.11 | 5 |
| EMPRESA DE TRANSPORTES,SERVICIOS,COMERCIALIZADORA,IMPORTADOR | 20155274477 | 1 | 4.00 | 4 |
| EMPRESA DE TRANSPORTES Y SERVICIOS NUEVA AMERICA S.A. | 20160058430 | 3 | 4.00 | 4 |
| EMPRESA DE TRANSPORTES ROLUESA S.A.C. | 20517464571 | 2 | 4.00 | 4 |
| EMPRESA DE TRANSPORTES URBANOS LOS CHINOS S.A. | 20194541008 | 1 | 3.50 | 7 |
| EMPRESA DE SERVICIOS MULTIPLES "EL CONDOR" SOCIEDAD ANONIMA  | 20258494696 | 1 | 3.50 | 7 |
| EMPRESA DE TRANSPORTES NUEVO HORIZONTE SOCIEDAD ANONIMA | 20138144578 | 1 | 3.50 | 5 |
| EMPRESA DE TRANSPORTES URBANO LINEA 4 S.A. | 20107648829 | 4 | 3.33 | 4 |
