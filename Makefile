.PHONY: build down logs

build:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f
