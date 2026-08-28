# Project PulsePM backend

The backend is a Django 6.1 application using SQLite locally. uv owns dependency resolution, the Python virtual environment, and every Python quality command. Ruff handles Python linting and formatting, djLint handles Django templates, mypy with django-stubs provides strict Django-aware type checking, and pytest-django runs tests.

## Prerequisites

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Setup and development

From the repository root:

```sh
make install-backend
make migrate
make dev-backend
```

Django is available at http://localhost:8000. uv automatically creates and uses `backend/.venv`; shell activation is optional.

To create an administrator:

```sh
uv --directory backend run python manage.py createsuperuser
```

## Quality commands

```sh
make lint-backend
make format-backend
make typecheck-backend
make test-backend
make check-backend
```

Add runtime dependencies with `uv --directory backend add <package>` and development-only dependencies with `uv --directory backend add --dev <package>`. Commit the resulting `backend/pyproject.toml` and `backend/uv.lock` changes.
