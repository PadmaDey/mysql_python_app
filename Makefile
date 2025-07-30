# .PHONY: build down logs local restart test db ci-pipeline clean tree

# build:
# 	docker compose up --build 

# down:
# 	docker compose down

# logs:
# 	docker compose logs -f

# local:
# 	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# restart:
# 	make down
# 	make build

# test:
# 	pytest

# db:
# 	docker run -d --name mysql -p 3306:3306 --env-file ./env/db/.env -v mysql_data:/var/lib/mysql --rm mysql:latest

# ci-pipeline:
# 	act

# clean:
# 	find . -type d -name "__pycache__" -exec rm -rf {} +
# 	find . -type d -name ".pytest_cache" -exec rm -rf {} +
# 	find . -type d -name ".mypy_cache" -exec rm -rf {} +
# 	find . -name "*.pyc" -delete

# tree:
# 	tree -I "mysql_conn_venv|__pycache__|.pytest_cache|.mypy_cache"


.PHONY: build down logs local restart test db ci-pipeline clean tree

ifeq ($(CI),true)
BUILD_CMD = docker compose --env-file ./env/db/.env up --build --remove-orphans --detach
else
BUILD_CMD = DOCKER_BUILDKIT=0 docker compose --env-file ./env/db/.env up --build --remove-orphans --detach
endif

build:
	@echo "📦 Building Docker images with Compose..."
	@$(BUILD_CMD)

down:
	@echo "🛑 Attempting to stop Docker containers..."
	@if [ -f ./env/db/.env ]; then \
		DOCKER_BUILDKIT=0 docker compose --env-file ./env/db/.env down; \
	else \
		echo "⚠️  ./env/db/.env not found. Skipping docker compose down."; \
	fi

logs:
	@echo "📜 Showing container logs..."
	docker compose logs -f

local:
	@echo "🚀 Running FastAPI app locally on port 8080..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

restart:
	@echo "🔁 Restarting services..."
	make down
	make build

test:
	@echo "🧪 Running pytest..."
	PYTHONPATH=backend pytest

db:
	@echo "🗄️ Starting standalone MySQL container..."
	docker run -d --name mysql -p 3306:3306 --env-file ./env/db/.env -v mysql_data:/var/lib/mysql --rm mysql:latest

ci-pipeline:
	@echo "⚙️ Running GitHub Actions locally with ACT..."
	act

clean:
	@echo "🧹 Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -name "*.pyc" -delete

tree:
	@echo "🌲 Project directory structure:"
	tree -I "mysql_conn_venv|__pycache__|.pytest_cache|.mypy_cache"
