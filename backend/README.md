# Project PulsePM backend

The backend is a Django 6.1 application using SQLite locally. uv owns dependency resolution, the Python virtual environment, and every Python quality command. Ruff handles Python linting and formatting, djLint handles Django templates, mypy with django-stubs provides strict Django-aware type checking, and pytest-django runs tests.

## API Swagger documentation

http://127.0.0.1:8000/api/docs#/

## Prerequisites

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Mailpit](https://mailpit.axllent.org/docs/install/), a local SMTP server with a web UI for testing emails

### Installing Mailpit

**Linux & macOS** — install to `/usr/local/bin/mailpit` with the install script:

```sh
sudo sh < <(curl -sL https://raw.githubusercontent.com/axllent/mailpit/develop/install.sh)
```

To use a different install path, set `INSTALL_PATH`:

```sh
sudo INSTALL_PATH=/usr/bin sh < <(curl -sL https://raw.githubusercontent.com/axllent/mailpit/develop/install.sh)
```

If you hit GitHub rate limits, pass a token via `GITHUB_TOKEN`:

```sh
sudo GITHUB_TOKEN="your_token_here" sh < <(curl -sL https://raw.githubusercontent.com/axllent/mailpit/develop/install.sh)
```

**Windows** — download the static binary from the [Mailpit releases page](https://github.com/axllent/mailpit/releases), extract `mailpit.exe`, and either copy it to a directory on your `PATH` or run it directly as `.\mailpit.exe`.

## Setup and development

From the repository root:

```sh
make install-backend
make migrate
make dev-backend
```

Django is available at http://localhost:8000. uv automatically creates and uses `backend/.venv`; shell activation is optional.

```sh
mailpit
```

Mailpit is available at http://localhost:8025/. 
Mailpit acts as an SMTP server, provides a modern web interface to view & test intercepted emails.

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