.PHONY: build down logs local

build:
	docker compose up --build 

down:
	docker compose down

logs:
	docker compose logs -f

local:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

test:
	pytest


