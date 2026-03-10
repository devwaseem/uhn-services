# Agent Guide (uhn_services)

Purpose: give coding agents a concise map of build, test, style, and
architecture so they can work safely in this repository.

## Project background

<Insert the project description here>

## General Conventions

- Frontend events: avoid inline `onclick`/`onkeydown` attributes. Keep
  interaction logic in `entry.ts` files via event listeners.
- Styling: prefer shared component classes in `frontend/shared/css/main.css`
  before adding page-specific CSS.
- Migrations: do not delete existing migrations; add new migrations to preserve
  history.

## Rules

- Ask clarifying questions before implementation whenever any requirement is
  ambiguous.
- Ask at least one targeted clarification question instead of guessing when
  behavior, constraints, or acceptance criteria are not explicit.
- Avoid assumptions about product behavior, business rules, and data contracts.
- Confirm open design decisions before implementation when they affect
  architecture, API shape, persistence, or security.
- Use UUIDs by default for new identifiers (including model primary keys)
  unless an existing schema or integration requires a different type.
- Avoid `async_to_sync` and `sync_to_async` where possible. If introducing them
  is the only practical option, ask for explicit approval first.
- Do not edit generated assets under `dist/` directly.

## Project snapshot

- Backend: Django + Celery, Python 3.14, uv-managed environment.
- Frontend: Vite + Tailwind CSS v4, TypeScript.
- Rendering: SSR-first templates via django-frontend-kit; datastar is optional
  and may be used only when interactivity is required.

## Authentication conventions

- Auth engine is `django-allauth`, but auth UI uses custom frontend-kit templates.
- Do not mount `include("allauth.urls")` for login/signup entry points.
- Current auth routes are:
    - `/login/` (`account_login`)
    - `/logout/` (`account_logout`)
    - `/register/` (`account_signup`)
    - `/password/reset/` (`account_reset_password`)
    - `/password/reset/done/` (`account_reset_password_done`)
    - `/password/reset/key/<uidb36>-<key>/` (`account_reset_password_from_key`)
    - `/password/reset/key/done/` (`account_reset_password_from_key_done`)
- Auth pages live under `frontend/pages/auth/` and render through frontend-kit
  page classes in `app/account/views.py`; keep using existing form components
  under `app/templates/components/form/`.
- `ACCOUNT_ALLOW_REGISTRATION` controls signup availability; preserve this
  behavior in templates and views.
- `SITE_ID` must be set in env for `django.contrib.sites` and allauth flows.

## Quick commands

### Dev and build

```bash
# Django dev server
just dev

# Vite dev server
just vite

# Frontend production build
npm run build
```

### Migrations

```bash
just makemigrations
just migrate
```

## Linting, formatting, typing

### Full lint (preferred)

```bash
just lint
# uv run pre-commit run --all-files
```

### Python

```bash
uv run ruff format app
uv run ruff check --fix app
just type
# or: just typecheck
```

### Templates (Django HTML)

```bash
uv run djlint app --reformat
```

### Frontend formatting

```bash
npx prettier --write "frontend/**/*.{ts,js,css}"
```

## Testing (pytest)

```bash
# All tests
just test

# Single file
just test app/tests/test_core.py

# Single test
just test app/tests/test_helpers/test_list/test_remove_none_from_list.py::test_remove_none_from_list

# Keyword or marker
just test -k remove_none
just test -m unit
```

## Architecture and workflow

- Prefer domain-oriented organization for new business logic (for example,
  `app/<domain>/domain/` when appropriate).
- Keep views and API handlers thin; move business rules into reusable services.
- Keep orchestration layers (views/tasks/commands) focused on control flow and
  delegate business rules to domain services.
- Keep clear responsibility boundaries between transport/orchestration, domain
  logic, and persistence layers.
- Design for testability by injecting dependencies and keeping contracts
  explicit at service boundaries.
- Prefer async end-to-end by default: async views, async domain services, async
  ORM methods (`aget`, `acreate`, `aexists`, `asave`), and async HTTP clients
  for external calls.
- Treat sync implementations as exceptions and document why async is not
  feasible when one is introduced.
- Prefer async middleware, background task boundaries, and integration clients
  where async alternatives exist.
- Write or update tests with behavior changes; TDD is preferred.

## Specs and docs

- Feature specs should live under `spec/`.
- Read only the relevant module spec to keep context focused.

## Code style guidelines

### General

- Document public modules, classes, and functions with useful docstrings.
- Prefer small, composable functions with clear inputs and outputs.

### SOLID principles

- Single Responsibility Principle (SRP): each module/class/function should have
  one clear reason to change; avoid mixing orchestration, business logic, and
  persistence concerns in one place.
- Open/Closed Principle (OCP): prefer extension (new strategies/services,
  composition, adapters) over modifying stable code paths.
- Liskov Substitution Principle (LSP): replacements for an abstraction must
  preserve behavior and contracts (return types, invariants, error semantics).
- Interface Segregation Principle (ISP): expose narrow, purpose-specific
  interfaces/functions; avoid large "god" services.
- Dependency Inversion Principle (DIP): depend on abstractions/protocols for
  external integrations and boundary components; keep concrete wiring at edges.

### Python (Django)

- Use type annotations consistently; mypy is configured in `pyproject.toml`.
- Prefer `from __future__ import annotations` in new modules.
- Follow Ruff formatting (79-char lines, 4-space indentation).
- Use guard clauses and early returns in views.
- Use explicit exceptions for invariant failures.
- Add user-facing validation errors via `form.add_error` when applicable.
- Use async auth helpers (`aauthenticate`, `alogin`, `alogout`) where needed.
- Use structlog-backed logging; avoid print statements.

### Tests

- Tests live in `app/tests` and domain-local test folders when present.
- Use pytest markers from `pyproject.toml` (`unit`, `integration`, `e2e`).
- Keep tests deterministic and scoped to behavior.

### Frontend (TypeScript + Vite)

- TypeScript is strict; avoid `any` unless unavoidable.
- Use path aliases (`@`, `@pages`, `@shared`, `@layouts`).
- Prettier handles formatting; import ordering is managed by
  `prettier-plugin-organize-imports`.
- Tailwind class sorting is handled by `prettier-plugin-tailwindcss`.

### Django Frontend Kit

- Layout templates should load the Django template tag library: `load fk_tags`.
- Layouts inject assets via frontend-kit template tags: `fk_preloads`,
  `fk_stylesheets`, `fk_head_scripts`, and `fk_body_scripts`.
- Page templates should inherit layouts; avoid duplicating FK tags in pages.
- Frontend entries live in `frontend/pages` and `frontend/layouts`.
- Vite outputs assets to `./dist`.

### HTML/CSS

- Tailwind v4 is enabled; keep custom CSS scoped to layout/page files.
- Templates are formatted with djLint via pre-commit.

## Error handling and safety

- Validate input early and return consistent error states.
- Prefer Celery native retries (`autoretry_for`, backoff, jitter) for background
  task retries instead of manual retry orchestration.
- Use `tenacity` only where local retry behavior is explicitly needed inside a
  function/service.
- Do not use broad exception handling; catch only the exceptions you can handle
  meaningfully and let other exceptions bubble up.
- Use `url_has_allowed_host_and_scheme` for redirect safety.
- Prefer `HttpResponseRedirect` for redirects.
- Use `typing.cast` only when narrowing types is required.

## Repo layout

- Backend code: `app/`.
- Frontend pages: `frontend/pages/`.
- Frontend layouts: `frontend/layouts/`.
- Shared frontend utilities: `frontend/shared/`.
- Follow existing page-domain conventions (for example, `auth/`, `root/`) unless
  a migration plan says otherwise.

## Tooling rules

- Pre-commit runs Ruff, djLint, mypy, and repository hygiene checks.

## Helpful commands

```bash
just shell
just celery
just celery-beat
just flower
```
