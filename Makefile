.PHONY: build down logs local test db

# Path to backend env file
ENV_FILE=backend/.env

# Load environment variables from backend/.env
include $(ENV_FILE)
export $(shell sed 's/=.*//' $(ENV_FILE))

# Build and start the app with Docker (passes env file)
build:
	docker compose --env-file $(ENV_FILE) up --build

# Stop containers
down:
	docker compose down

# View logs
logs:
	docker compose logs -f

# Run app locally with uvicorn, using backend/.env
local:
	cd backend && ENV=local uvicorn app.main:app --reload --host 0.0.0.0 --port $(PORT)

# Run tests (uses backend/.env automatically)
test:
	cd backend && ENV=test pytest

# Start MySQL container using backend/.env credentials
db:
	docker run -d --name mysql \
		-p $(MYSQL_PORT):3306 \
		--env-file $(ENV_FILE) \
		-v mysql_data:/var/lib/mysql \
		--rm mysql:latest
