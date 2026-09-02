# Project PulsePM frontend

The frontend is a strict TypeScript application built with React, TanStack Start, Vite, Tailwind CSS, and TanStack Query. Bun manages packages and runs scripts; Biome provides formatting and linting.

## Prerequisites

- [Bun](https://bun.sh/docs/installation)

## Setup and development

Prefer the root project commands:

```sh
make install-frontend
make dev-frontend
```

The development server is available at http://localhost:3000. For direct frontend work, run `bun install` and `bun run dev` from this directory.

## Networking

The browser only ever talks to the Vite dev server on port 3000. API calls are made to the
same-origin path `/api/*` and forwarded to Django by the Vite proxy configured in
`vite.config.ts`, so no CORS configuration is needed and the Django `sessionid` cookie is
treated as first-party.

```mermaid
flowchart LR
    U["User<br/>browser"]

    subgraph FE["frontend/ — Bun + Vite — localhost:3000"]
        APP["TanStack Start + React app<br/>src/routes, TanStack Query"]
        PROXY["Vite dev proxy<br/>/api → 127.0.0.1:8000"]
    end

    subgraph BE["backend/ — Django — localhost:8000"]
        API["Django Ninja API<br/>/api/login, /api/logout, /api/auth/me"]
        ADMIN["Django admin<br/>/admin/"]
        DB[("SQLite<br/>db.sqlite3")]
    end

    U -->|"loads app over :3000"| APP
    APP -->|"fetch '/api/...' same-origin<br/>credentials: 'include'"| PROXY
    PROXY -->|"forwards to :8000"| API
    API -->|"JSON + Set-Cookie sessionid"| PROXY
    API --> DB
    U -.->|"direct visit to :8000/admin/"| ADMIN
    ADMIN --- DB
```

- The user loads the app from the frontend on http://localhost:3000.
- `src/lib/auth-api.ts` sends every request to `/api/...` with `credentials: 'include'`.
- Vite proxies those requests to Django at http://127.0.0.1:8000, which serves the Ninja API
  under `/api/` and authenticates with standard Django sessions.
- Django admin at http://localhost:8000/admin/ is reached directly, bypassing the frontend.

## Quality commands

From the repository root:

```sh
make lint-frontend
make format-frontend
make typecheck-frontend
make test-frontend
make check-frontend
```

Production assets can be verified with `bun run --cwd frontend build`.

Routes live in `src/routes`; `src/routeTree.gen.ts` is generated and should not be edited manually. Shared browser/server data access belongs in the existing TanStack Query integration.
