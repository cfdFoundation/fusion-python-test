# Simple Makefile for running common tasks

# Local development commands
install:
	pip install -r requirements.txt

run:
	python app.py

test:
	pytest test_app.py -v

init-db:
	python init_db.py

clean:
	rm -f products.db
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

fresh-start: clean install run

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up

docker-up-bg:
	docker-compose up -d

docker-down:
	docker-compose down

docker-test:
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit

docker-init-db:
	docker-compose run --rm web python init_db.py

docker-shell:
	docker-compose run --rm web /bin/bash

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v
	docker system prune -f

docker-fresh: docker-clean docker-build docker-up

.PHONY: install run test init-db clean fresh-start docker-build docker-up docker-up-bg docker-down docker-test docker-init-db docker-shell docker-logs docker-clean docker-fresh
