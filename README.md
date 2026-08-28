# Project PulsePM

Project PulsePM is a monorepo containing a typed Django application and a TanStack Start frontend. The root `Makefile` is the supported interface for installing, running, and validating both projects.

## Prerequisites

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Bun](https://bun.sh/docs/installation)
- GNU Make (the macOS Command Line Tools version is sufficient)

No global Python packages, Biome installation, or manually activated virtual environment are required.

## Installation

From the repository root:

```sh
make install
make migrate
make pre-commit-install
```

`make install` creates `backend/.venv` through uv and installs the frontend packages from `frontend/bun.lock`. SQLite is used for local development.

## Running the project

Start Django and Vite together:

```sh
make dev
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Django admin: http://localhost:8000/admin/

Press Ctrl-C once to stop both processes. To run either service separately, use `make dev-backend` or `make dev-frontend`.

## Development workflow

```sh
make check       # lint, formatting check, type-check, and tests
make format      # apply backend and frontend formatting
make migrations  # create Django migrations
make migrate     # apply Django migrations
make help        # list every project command
```

Pre-commit hooks select checks by changed directory: backend changes run Ruff, djLint, mypy, and pytest; frontend changes run Biome, TypeScript, and Bun tests. Changes to shared project tooling run both suites.

See [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md) for service-specific details.
