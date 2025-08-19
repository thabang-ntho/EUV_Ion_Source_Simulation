PYTHON := python

.PHONY: install install-dev test test-comsol check-fresnel check-kumar provenance lint test-cov clean

install:
	uv pip install -e .

install-dev:
	uv pip install -e .[dev]

test:
	PYTHONPATH=$$(pwd) uv run pytest -q

test-comsol:
	PYTHONPATH=$$(pwd) uv run pytest -m comsol -q

check-fresnel:
	uv run python src/pp_model.py --check-only --absorption-model fresnel

check-kumar:
	uv run python src/pp_model.py --check-only --absorption-model kumar

provenance:
	LOG_LEVEL=INFO uv run python src/pp_model.py --check-only

lint:
	@command -v ruff >/dev/null 2>&1 && ruff check . || \
	  (command -v flake8 >/dev/null 2>&1 && flake8 || \
	   echo "No linter (ruff/flake8) found; skipping lint.")

test-cov:
	PYTHONPATH=$$(pwd) uv run pytest --cov=src --cov-report=xml:coverage.xml -q

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} + || true
	rm -rf .pytest_cache .coverage coverage.xml || true
	@echo "Cleaned caches (kept data/ and results/ intact)."
