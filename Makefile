PYTHON ?= python
PACKAGE = symbo_agentic_reasoners

.PHONY: install install-dev lint format test test-fast coverage docs clean

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e .[dev]

lint:
	$(PYTHON) -m ruff check src tests
	$(PYTHON) -m black --check src tests

format:
	$(PYTHON) -m black src tests

test:
	$(PYTHON) -m pytest

test-fast:
	$(PYTHON) -m pytest -m "not slow"

coverage:
	$(PYTHON) -m pytest --cov=src/$(PACKAGE) --cov-report=term --cov-report=xml

docs:
	@echo "Docs are Markdown in docs/api; publish with your preferred static site generator."

clean:
	rm -rf .pytest_cache .coverage htmlcov coverage.xml
