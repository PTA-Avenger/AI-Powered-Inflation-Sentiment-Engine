# Common Commands Makefile

.PHONY: help setup install test run run-mcp clean db-init db-reset deploy lint

help:
	@echo "Inflation Sentiment Engine - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Complete setup (venv, deps, db)"
	@echo "  make install        - Install dependencies"
	@echo "  make db-init        - Initialize database"
	@echo "  make db-reset       - Reset database (wipes data)"
	@echo ""
	@echo "Development:"
	@echo "  make test           - Run tests"
	@echo "  make test-cov       - Run tests with coverage"
	@echo "  make lint           - Run code linting"
	@echo "  make format         - Format code"
	@echo ""
	@echo "Running:"
	@echo "  make run            - Run full pipeline"
	@echo "  make run-mcp        - Run MCP server locally"
	@echo "  make docker         - Run with Docker Compose"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy-local   - Prepare local deployment"
	@echo "  make deploy-lambda  - Package for AWS Lambda"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make logs           - View application logs"

setup:
	python -m venv venv
	venv\Scripts\activate && pip install -r requirements.txt
	make db-init
	@echo "Setup complete! Run 'make run' to start."

install:
	pip install -r requirements.txt

db-init:
	python -c "from database import init_db; from config import get_settings; init_db(get_settings().database_url); print('Database initialized!')"

db-reset:
	@echo "Warning: This will delete all data!"
	@read -p "Continue? (y/N) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		psql -c "DROP DATABASE IF EXISTS inflation_sentiment; CREATE DATABASE inflation_sentiment;"; \
		make db-init; \
	fi

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=. --cov-report=html --cov-report=term

lint:
	pylint config database scrapers sentiment mcp_server utils
	flake8 config database scrapers sentiment mcp_server utils

format:
	black config database scrapers sentiment mcp_server utils tests main.py

run:
	python main.py

run-mcp:
	python run_mcp_server.py

docker:
	docker-compose up -d
	@echo "Services running:"
	@echo "  PostgreSQL: localhost:5432"
	@echo "  MCP Server: http://localhost:8000"
	@echo "  Docs: http://localhost:8000/docs"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f mcp-server

deploy-local:
	@echo "Preparing local deployment..."
	mkdir -p lambda_deployment
	cp -r config database scrapers sentiment utils lambda_deployment/
	cp aws_lambda/handler.py lambda_deployment/
	cp requirements.txt lambda_deployment/
	cd lambda_deployment && zip -r ../lambda_function.zip . && cd ..
	@echo "Lambda package ready: lambda_function.zip"

deploy-lambda: deploy-local
	@echo "Deploying to AWS Lambda..."
	aws lambda update-function-code \
		--function-name inflation-sentiment-engine \
		--zip-file fileb://lambda_function.zip

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build dist *.egg-info
	rm -rf lambda_deployment lambda_function.zip lambda_layer.zip
	rm -rf htmlcov .coverage

logs:
	tail -f logs/app.log

logs-errors:
	grep ERROR logs/app.log | tail -20

shell:
	python

shell-db:
	psql -d inflation_sentiment

requirements:
	pip install pipreqs
	pipreqs --force --savepath requirements.txt .

.DEFAULT_GOAL := help
