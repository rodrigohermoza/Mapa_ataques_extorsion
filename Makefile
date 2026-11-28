# Mapa-crimen: tubería sin IA y sin paquetes (solo Python estándar + curl)
PY = python3 -I
PYV = .venv/bin/python -I  # venv del proyecto (pypdf)

.PHONY: diario procesar historico archivar wayback ver

# Fines de semana: trae lo nuevo desde la última nota bajada y regenera todo (~20–60 s)
diario:
	$(PY) scripts/recolectar.py --diario
	$(PY) scripts/archivar.py
	$(MAKE) procesar

# Titulares → hechos → comparación con el Ministerio Público → cruce con las rutas de la ATU
procesar:
	$(PY) scripts/lineas.py
	$(PYV) scripts/rutas_atu.py
	$(PY) scripts/trazados_atu.py
	$(PYV) scripts/fichas_atu.py
	$(PY) scripts/extraer.py
	$(PY) scripts/validar.py > /dev/null
	$(PY) scripts/cruce_rutas.py
	$(PY) scripts/mapa.py
	@echo "Listo: ataques.csv, ataques_por_ruta.csv, results/validacion.md, results/rutas_atu.md y results/mapa.html"

# Rehace el histórico desde ago-2024 (~70 min, ~2 MB). No borra lo ya bajado.
historico:
	$(PY) scripts/recolectar.py --desde 2024-08-01

# Guarda enlace real + texto de cada nota nueva (~5 s por nota; textos solo en disco, D-09)
archivar:
	$(PY) scripts/archivar.py --reintentar

# Copias en Internet Archive de lo archivado (~30-50 s por nota). Se puede cortar con Ctrl+C y retomar.
wayback:
	$(PY) scripts/archivar.py --wayback

# Ver el mapa en http://127.0.0.1:8765/mapa.html (Ctrl+C para cerrar). Con doble clic también abre,
# pero OpenStreetMap puede negar el mapa base a páginas sin dirección web (file://).
ver:
	@echo "Abre http://127.0.0.1:8765/mapa.html"
	$(PY) -m http.server 8765 --bind 127.0.0.1 --directory results
