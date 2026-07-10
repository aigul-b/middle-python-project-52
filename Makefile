install:
	uv sync

collectstatic:
	uv run python manage.py collectstatic --no-input

migrate:
	uv run python manage.py migrate

build:
	./build.sh

render-start:
	uv run gunicorn task_manager.wsgi
test:
	uv run python manage.py test
lint:
	uv run ruff check .

test-coverage:
	uv run coverage run --source='.' manage.py test
	uv run coverage xml
