# Quickstart

## 1) Configure Environment
```bash
cp env_template.txt .env
```

## 2) Install Dependencies
```bash
uv sync --dev
npm install
```

## 3) Run Django
```bash
export DJANGO_SETTINGS_MODULE=app.settings.dev
uv run python manage.py runserver
```

## 4) Run Vite
```bash
npm run dev
```

## Common Commands
- `just dev`
- `just vite`
- `just test`
- `just lint`
