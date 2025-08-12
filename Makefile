.PHONY: build down logs local restart test db ci-pipeline clean tree

# Define build command depending on CI flag
ifeq ($(CI),true)
COMPOSE_CMD = docker compose --env-file ./env/db/.env
else
COMPOSE_CMD = DOCKER_BUILDKIT=0 docker compose --env-file ./env/db/.env
endif

build:
	@echo "Starting MySQL container first..."
	@$(COMPOSE_CMD) up --build --remove-orphans --detach mysql

	@echo "Waiting up to 90s for MySQL to become healthy..."
	@\
	i=0; \
	while [ "$$(docker inspect --format='{{.State.Health.Status}}' db)" != "healthy" ]; do \
		if [ "$$i" -ge 18 ]; then \
			echo "DB healthcheck failed after 90s. Logs:"; \
			docker logs db; \
			exit 1; \
		fi; \
		echo "Waiting for DB... ($$((i*5))s)"; \
		sleep 5; \
		i=$$((i+1)); \
	done

	@echo "MySQL is healthy. Starting API..."
	@$(COMPOSE_CMD) up --build --remove-orphans --detach api

down:
	@echo "Attempting to stop Docker containers..."
	@if [ -f ./env/db/.env ]; then \
		DOCKER_BUILDKIT=0 docker compose --env-file ./env/db/.env down; \
	else \
		echo "./env/db/.env not found. Skipping docker compose down."; \
	fi

logs:
	@echo "Showing container logs..."
	@docker compose logs -f

local:
	@echo "Running FastAPI app locally on port 8080..."
	@cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

restart:
	@echo "Restarting services..."
	@make down
	@make build

test:
	@echo "Running pytest..."
	@PYTHONPATH=backend pytest

# Run Locust in UI mode (manual control from browser)
load-test:
	@echo "Starting Locust UI for ALL tests..."
	@locust -f load_tests/locustfile.py --host=http://127.0.0.1:8080 --web-host=127.0.0.1

load-test-signup:
	@echo "Starting Locust UI for SignupUserTest..."
	@locust -f load_tests/endpoints/signup_test.py --host=http://127.0.0.1:8080 --web-host=127.0.0.1

load-test-login:
	@echo "Starting Locust UI for LoginUserTest..."
	@locust -f load_tests/endpoints/login_test.py --host=http://127.0.0.1:8080 --web-host=127.0.0.1

load-test-view-current:
	@echo "Starting Locust UI for ViewCurrentUserTest..."
	@locust -f load_tests/endpoints/view_current_user_test.py --host=http://127.0.0.1:8080 --web-host=127.0.0.1

load-test-view-all:
	@echo "Starting Locust UI for ViewAllUsersTest..."
	@locust -f load_tests/endpoints/view_all_users_test.py --host=http://127.0.0.1:8080 --web-host=127.0.0.1

load-test-update:
	@echo "Starting Locust UI for UpdateUserDataTest..."
	@locust -f load_tests/endpoints/update_user_data_test.py --host=http://127.0.0.1:8080 --web-host=127.0.0.1

load-test-delete:
	@echo "Starting Locust UI for DeleteUserDataTest..."
	@locust -f load_tests/endpoints/delete_user_data_test.py --host=http://127.0.0.1:8080 --web-host=127.0.0.1

load-test-logout:
	@echo "Starting Locust UI for LogoutUserTest..."
	@locust -f load_tests/endpoints/logout_test.py --host=http://127.0.0.1:8080 --web-host=127.0.0.1

# Start backend locally + load test (UI mode)
local-with-load:
	@make db
	@make local &
	@sleep 5 && make load-test

db:
	@echo "Starting standalone MySQL container..."
	@docker run -d --name mysql -p 3306:3306 --env-file ./env/db/.env -v mysql_data:/var/lib/mysql --rm mysql:latest

ci-pipeline:
	@echo "Running GitHub Actions locally with ACT..."
	@act

clean:
	@echo "Cleaning Python cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -name "*.pyc" -delete

tree:
	@echo "Project directory structure:"
	@tree -I "mysql_conn_venv|__pycache__|.pytest_cache|.mypy_cache"
