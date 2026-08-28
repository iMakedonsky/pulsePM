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
