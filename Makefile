.PHONY: venv install run-backend run-frontend test test-backend test-frontend clean

VENV_PYTHON := .venv/bin/python
PYTHON_BIN := python3.13
PYTHON_VERSION := 3.13.9

venv:
	uv venv --python $(PYTHON_BIN)
	uv pip install -e .

install:
	@if [ -x "$(VENV_PYTHON)" ]; then \
		VERSION=`$(VENV_PYTHON) -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" 2>/dev/null`; \
		if [ "$$VERSION" != "$(PYTHON_VERSION)" ]; then \
			echo "Existing .venv uses Python $$VERSION; recreating with Python $(PYTHON_VERSION)."; \
			rm -rf .venv; \
		fi; \
	fi
	@if [ ! -x "$(VENV_PYTHON)" ]; then \
		uv venv --python $(PYTHON_BIN); \
	fi
	uv sync

run-backend:
	@if [ ! -x "$(VENV_PYTHON)" ]; then echo "Missing .venv. Run 'make install' first."; exit 1; fi
	@$(VENV_PYTHON) -c "import uvicorn" >/dev/null 2>&1 || (echo "Missing backend dependencies. Run 'make install' first."; exit 1)
	cd backend && ../$(VENV_PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	@if [ ! -x "$(VENV_PYTHON)" ]; then echo "Missing .venv. Run 'make install' first."; exit 1; fi
	@$(VENV_PYTHON) -c "import streamlit" >/dev/null 2>&1 || (echo "Missing frontend dependencies. Run 'make install' first."; exit 1)
	cd frontend && ../$(VENV_PYTHON) -m streamlit run app.py --server.port 8501

test:
	@echo "Running all tests..."
	make test-backend
	make test-frontend

test-backend:
	@echo "Backend tests not yet implemented"

test-frontend:
	@echo "Frontend tests not yet implemented"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .venv/ uv.lock
