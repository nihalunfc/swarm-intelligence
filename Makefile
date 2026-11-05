# Common tasks. `make reproduce` regenerates every table in results/ from scratch on this machine
# (hours on a laptop CPU); the same jobs run on GitHub Actions via experiments/queue.yaml.

PY ?= python
SEEDS ?= 0 1 2 3 4
JOBS ?= 2

.PHONY: install test lint reproduce energy wildfire housekeeping robustness clean

install:
	pip install -e ".[dev,hotel,research]"

test:
	pytest -q tests && pytest -q apps/hotel/analytics/tests

lint:
	ruff check .

energy:
	swarm seeds --config configs/energy.yaml --seeds 0 1 2 3 4 5 6 7 8 9 --jobs $(JOBS) --out runs
	swarm aggregate runs/seeds-energy-* --output results/energy

wildfire:
	for c in wildfire wildfire-imitate wildfire-residual; do \
	  swarm seeds --config configs/$$c.yaml --seeds $(SEEDS) --jobs $(JOBS) --out runs; done
	swarm aggregate runs/seeds-wildfire* --output results/wildfire-methods --compare-to wildfire

housekeeping:
	for c in hotel-housekeeping hotel-housekeeping-residual; do \
	  swarm seeds --config configs/$$c.yaml --seeds $(SEEDS) --jobs $(JOBS) --out runs; done
	swarm aggregate runs/seeds-hotel-housekeeping* --output results/hotel-housekeeping-methods \
	  --compare-to hotel-housekeeping

robustness:
	swarm robustness runs/seeds-wildfire-residual-* --output results/robustness-wildfire
	swarm robustness runs/seeds-energy-* --output results/robustness-energy
	swarm robustness runs/seeds-hotel-housekeeping-residual-* --output results/robustness-hotel-housekeeping

reproduce: energy wildfire housekeeping robustness

clean:
	rm -rf runs mlruns
