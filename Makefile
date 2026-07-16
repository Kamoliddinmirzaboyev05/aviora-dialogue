.PHONY: compose test-backend test-frontend build-frontend seed migrate

compose:
	docker compose up --build

migrate:
	cd backend && python manage.py migrate

seed:
	cd backend && python manage.py seed_demo

test-backend:
	cd backend && pytest -v

test-frontend:
	cd frontend && npm test

build-frontend:
	cd frontend && npm run build
