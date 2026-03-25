.PHONY: venv install run-backend run-frontend test test-backend test-frontend clean

venv:
	uv venv
	uv pip install -e .

install:
	uv sync

run-backend:
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && streamlit run app.py --server.port 8501

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
