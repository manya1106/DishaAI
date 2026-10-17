.PHONY: install dev-api dev-web test test-scoring test-ai lint contracts build-web

install:
	cd apps/api && python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
	cd apps/web && npm install

dev-api:
	cd apps/api && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

dev-web:
	cd apps/web && npm run dev

test: test-scoring test-ai

test-scoring:
	cd apps/api && source .venv/bin/activate && pytest tests/scoring -v

test-ai:
	cd apps/api && source .venv/bin/activate && pytest tests/ai -v

lint:
	cd apps/api && source .venv/bin/activate && ruff check .
	cd apps/web && npm run lint

contracts:
	cd apps/api && source .venv/bin/activate && python ../../scripts/export_openapi.py
	cd apps/web && npm run gen:types
