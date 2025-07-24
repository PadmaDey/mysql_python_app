.PHONY: build down logs local restart test db

build:
	docker compose up --build 

down:
	docker compose down

logs:
	docker compose logs -f

local:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

restart:
	make down
	make build

test:
	pytest

db:
	docker run -d --name mysql -p 3306:3306 --env-file ./env/db/.env -v mysql_data:/var/lib/mysql --rm mysql:latest

