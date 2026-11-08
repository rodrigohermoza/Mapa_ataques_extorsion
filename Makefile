# Mapa-crimen: tubería sin IA y sin paquetes (solo Python estándar + curl)
PY = python3 -I
PYV = .venv/bin/python -I  # venv del proyecto (pypdf)

.PHONY: diario procesar historico

# Fines de semana: trae lo nuevo desde la última nota bajada y regenera todo (~20–60 s)
diario:
	$(PY) scripts/recolectar.py --diario
	$(MAKE) procesar

# Titulares → hechos → comparación con el Ministerio Público
procesar:
	$(PY) scripts/lineas.py
	$(PYV) scripts/rutas_atu.py
	$(PY) scripts/extraer.py
	$(PY) scripts/validar.py > /dev/null
	@echo "Listo: data/processed/ataques.csv y results/validacion.md"

# Rehace el histórico desde ago-2024 (~70 min, ~2 MB). No borra lo ya bajado.
historico:
	$(PY) scripts/recolectar.py --desde 2024-08-01
