dev:
  LOG_DB=true uv run python manage.py runserver_plus 0.0.0.0:8000

vite:
  npm run dev

test *ARGS:
    TEST=true PYTHONBREAKPOINT=ipdb.set_trace uv run pytest -s  {{ ARGS }}

lint:
  uv run pre-commit run --all-files

setup:
  uv sync --dev
  npm install

format:
  uv run ruff format app

docs:
  uv run mkdocs serve

docs-build:
  uv run mkdocs build

typecheck *ARGS:
  uv run mypy app {{ ARGS }}

type *ARGS:
  uv run mypy app {{ ARGS }}

celery:
  LOG_DB=true uv run watchmedo auto-restart --directory=app --recursive --pattern '*.py' -- celery --app app worker -E -l INFO -Q celery --pool gevent --concurrency 20

celery-beat:
  LOG_DB=true uv run celery --app app beat -l INFO

flower:
  LOG_DB=true uv run celery --app app flower

makemigrations *ARGS:
  uv run python manage.py makemigrations {{ ARGS }}

migrate *ARGS:
  uv run python manage.py migrate {{ ARGS }}

dbshell *ARGS:
  uv run python manage.py dbshell {{ ARGS }}

lab:
  LOG_DB=true DJANGO_ALLOW_ASYNC_UNSAFE=true uv run python manage.py shell_plus --lab --no-browser

notebook:
  LOG_DB=true DJANGO_ALLOW_ASYNC_UNSAFE=true uv run python manage.py shell_plus --notebook --no-browser

shell:
  uv run python manage.py shell_plus

up *ARGS:
  docker-compose -f development.yml up -d {{ ARGS }}

stop *ARGS:
  docker-compose -f development.yml stop {{ ARGS }}

down *ARGS:
  docker-compose -f development.yml down {{ ARGS }}

docker-shell CONTAINER_NAME:
  docker-compose -f development.yml exec {{ CONTAINER_NAME }} bash
