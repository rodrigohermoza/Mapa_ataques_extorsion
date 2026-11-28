# Pendientes

## Preguntas para el autor
1. **Periodo:** ¿ago-2024 en adelante (coincide con el Ministerio Público) o desde antes?
2. **Alcance:** ¿solo Lima y Callao? ¿Incluir combis/custers informales o solo líneas formales?
3. ~~Recopilación~~ → automática con Google Noticias RSS + reglas (D-03). Hecho el 2026-11-07.
6. ~~¿Programar `make diario`?~~ → El autor lo corre a mano los fines de semana (D-06).
4. **Solicitud de acceso a la información:** ¿quieres pedir al Ministerio Público la tabla por empresa/línea y a la ATU el GTFS? (lo envías tú; yo preparo el texto).
5. ~~¿Repositorio en GitHub público o privado?~~ → público, titulares incluidos (D-08).

## Tareas
- [x] Boletines del Ministerio Público revisados: sin desglose por línea (2026-11-07).
- [ ] Revisar en el navegador: datosabiertos.gob.pe, Datacrim (INEI), presentaciones de MININTER al Congreso (una dio 404).
- [ ] Probar ACLED (registro gratis) para ver si codifica estos ataques.
- [x] Recolector, extractor y validación (R-01: 71% de cobertura, 63% con empresa).
- [ ] Tabla de empresas revisada (sinónimos, ¿"El Chino" = "Los Chinos"?).
- [ ] Mejorar cobertura de Lima Este y Noroeste.
- [ ] Medir tamaño de la descarga de rutas OSM y pedir aprobación.
- [ ] Tabla código ATU ↔ empresa ↔ nombre popular.
- [x] Solicitud a la ATU enviada: exp. [n.° reservado] (2026-11-07).
- [ ] Revisar la Bandeja de Observados del SAIP hasta el 11-nov (subsanación en 2 días hábiles).
- [x] ~~23-nov-2026: vence el plazo de la ATU.~~ Respondió el 24-nov; no hace falta apelar. Si no hay respuesta: apelar ante el Tribunal de Transparencia desde el 24-nov (hasta ~16-dic). Borrador listo: `solicitudes/2026-11-ATU-apelacion.md`.
- [x] Procesar la respuesta de la ATU (2026-11-28): GeoJSON, rutas oficiales, fichas y cruce con ataques (`results/rutas_atu.md`).
- [x] Primer mapa: rutas coloreadas por ataques ponderados (D-10) → `results/mapa.html` (2026-11-28).
- [x] Mapa publicado en GitHub Pages (2026-11-28): https://rodrigohermoza.github.io/Mapa_ataques_extorsion/. Flujo de Actions que solo sube `results/mapa.html` como `index.html`.
- [x] Ubicar ataques (lugar aproximado o distrito) y filtro por fecha en el mapa (2026-11-28, D-12).
- [ ] Subir la pausa de Google o buscar otra forma de decodificar enlaces para archivar más textos por corrida (P-11).
- [ ] Revisar a mano los 27 lugares encontrados (p. ej. "Paradero de Comas" queda a 1.6 km de su ruta).
- [ ] Proponer rutas a los 166 ataques sin código usando las vías de `fichas_atu.csv` + distrito.
- [ ] Opcional: pedir a la ATU la ficha correcta de la ruta 1030 (P-09).
- [ ] Archivar el texto de todas las notas (`make archivar`, D-09): 44 de 1 902 hechas; la primera pasada se detuvo por el límite de Google (P-08). Volver a correr dejando pasar unas horas (~6 h con pausa de 8 s; se puede cortar y retomar).
- [ ] Copias en Internet Archive de todo el histórico (`make wayback`, ~20 h; correr por partes).
- [ ] Ver si se puede sacar el texto de La República (página armada con JavaScript); por ahora solo Wayback.
- [ ] Opcional: trazados de OSM para las ~53 rutas que existen.
