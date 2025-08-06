.PHONY: build down logs local restart test db ci-pipeline clean tree

# Define build command depending on CI flag
ifeq ($(CI),true)
COMPOSE_CMD = docker compose --env-file ./env/db/.env
else
COMPOSE_CMD = DOCKER_BUILDKIT=0 docker compose --env-file ./env/db/.env
endif

build:
	@echo "🐋 Starting MySQL container first..."
	@$(COMPOSE_CMD) up --build --remove-orphans --detach mysql

	@echo "⏳ Waiting up to 60s for MySQL to become healthy..."
	@timeout 60s bash -c \
		'until [ "$$(docker inspect --format="{{.State.Health.Status}}" db)" = "healthy" ]; do \
			echo "⏱️  Waiting for DB..."; sleep 5; \
		done'

	@echo "🚀 Starting API container..."
	@$(COMPOSE_CMD) up --build --remove-orphans --detach api

down:
	@echo "🛑 Attempting to stop Docker containers..."
	@if [ -f ./env/db/.env ]; then \
		DOCKER_BUILDKIT=0 docker compose --env-file ./env/db/.env down; \
	else \
		echo "⚠️  ./env/db/.env not found. Skipping docker compose down."; \
	fi

logs:
	@echo "📜 Showing container logs..."
	@docker compose logs -f

local:
	@echo "🚀 Running FastAPI app locally on port 8080..."
	@cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

restart:
	@echo "🔁 Restarting services..."
	@make down
	@make build

test:
	@echo "🧪 Running pytest..."
	@PYTHONPATH=backend pytest

db:
	@echo "🗄️ Starting standalone MySQL container..."
	@docker run -d --name mysql -p 3306:3306 --env-file ./env/db/.env -v mysql_data:/var/lib/mysql --rm mysql:latest

ci-pipeline:
	@echo "⚙️ Running GitHub Actions locally with ACT..."
	@act

clean:
	@echo "🧹 Cleaning Python cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -name "*.pyc" -delete

tree:
	@echo "🌲 Project directory structure:"
	@tree -I "mysql_conn_venv|__pycache__|.pytest_cache|.mypy_cache"
