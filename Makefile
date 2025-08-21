PYTHON := python

.PHONY: install install-dev test test-comsol check-fresnel check-kumar smoke provenance lint lint-docs test-cov clean mph-check mph-solve

install:
	uv pip install -e .

install-dev:
	uv pip install -e .[dev]

test:
	PYTHONPATH=$$(pwd) uv run pytest -q

test-comsol:
	RUN_COMSOL=1 PYTHONPATH=$$(pwd) uv run pytest -m comsol -q

check-fresnel:
	uv run python src/pp_model.py --check-only --absorption-model fresnel

check-kumar:
	uv run python src/pp_model.py --check-only --absorption-model kumar

smoke: check-fresnel check-kumar
	@echo "Smoke checks completed."

provenance:
	LOG_LEVEL=INFO uv run python src/pp_model.py --check-only

# MPh-based builder (no solve); requires COMSOL env configured
mph-check:
	. scripts/setup_comsol_env.sh >/dev/null 2>&1 || true; \
	uv run euv-mph --check-only --variant fresnel --log-level INFO

# MPh-based builder + solve (headless). Provide COMSOL_HOST/PORT via env if remote
mph-solve:
	. scripts/setup_comsol_env.sh >/dev/null 2>&1 || true; \
	uv run euv-mph --solve --variant fresnel --log-level INFO

lint:
	@command -v ruff >/dev/null 2>&1 && ruff check . || \
	  (command -v flake8 >/dev/null 2>&1 && flake8 || \
	   echo "No linter (ruff/flake8) found; skipping lint.")

lint-docs:
	@echo "Running markdownlint..." && \
	command -v markdownlint >/dev/null 2>&1 || echo "Tip: npm i -g markdownlint-cli"; \
	markdownlint "**/*.md" --ignore node_modules --config .markdownlint.jsonc || true; \
	echo "Running Vale..." && \
	command -v vale >/dev/null 2>&1 || echo "Tip: install Vale from https://vale.sh/"; \
	vale . || true

test-cov:
	PYTHONPATH=$$(pwd) uv run pytest --cov=src --cov-report=xml:coverage.xml -q

compare:
	@if [ -z "$(BASE)" ] || [ -z "$(CAND)" ]; then \
	  echo "Usage: make compare BASE=results/baseline CAND=results/candidate [RTOL=1e-5 ATOL=1e-8]"; \
	  exit 2; \
	fi; \
	uv run euv-compare --baseline $(BASE) --candidate $(CAND) --rtol $${RTOL:-1e-5} --atol $${ATOL:-1e-8}

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} + || true
	rm -rf .pytest_cache .coverage coverage.xml || true
	@echo "Cleaned caches (kept data/ and results/ intact)."
