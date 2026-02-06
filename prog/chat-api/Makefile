.PHONY: help build up down logs test clean migrate shell

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs
	docker-compose logs -f

test: ## Run tests
	docker-compose exec app pytest -v

test-cov: ## Run tests with coverage
	docker-compose exec app pytest --cov=app --cov-report=html --cov-report=term

migrate: ## Run database migrations
	docker-compose exec app alembic upgrade head

migrate-create: ## Create new migration (use MESSAGE variable)
	docker-compose exec app alembic revision --autogenerate -m "$(MESSAGE)"

shell: ## Open Python shell in container
	docker-compose exec app python

db-shell: ## Open PostgreSQL shell
	docker-compose exec db psql -U chatuser -d chatdb

clean: ## Clean up containers and volumes
	docker-compose down -v
	rm -rf __pycache__ .pytest_cache htmlcov .coverage

restart: down up ## Restart all services

rebuild: down build up ## Rebuild and restart all services
