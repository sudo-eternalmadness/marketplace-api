# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A pet project ([roadmap.sh e-commerce API](https://roadmap.sh/projects/ecommerce-api)) built to learn
FastAPI and real-world Web API design.

## Commands

Package management is via **uv**, not pip/poetry — use `uv add`/`uv remove` for dependencies, `uv.lock` is committed.

```
uv run pytest
```

Linting, type-checking (`ruff check`, `ruff format`, `ty`) and the test suite all run automaticall via `.pre-commit-config.yaml` on commit. Do not invoke them manually as a separate step — a commit already proves the code is clean.

## Architecture

Standard FastAPI layering, one file per concern:

- `app/models/` — SQLModel entities and their Create/Update/Public schema variants, one module per
  resource (`product.py`, `user.py`, `cart.py`, `token.py`; `base.py` holds shared helpers).
  `__init__.py` is empty; import directly from the submodule (`from app.models.product import Product`).
  Cross-module relationships use `TYPE_CHECKING` imports with string annotations to avoid import cycles
- `app/crud.py` — DB read/write functions, framework-agnostic (no `HTTPException`s here) , for preventing DRY violations
- `app/api/routers/` — one router per resource; HTTP concerns (status codes, `HTTPException`) live here
- `app/api/deps.py` — shared FastAPI dependencies (`SessionDep`, `CurrentUser`, auth)
- `app/core/` — config, DB engine, security (hashing, JWT)

Follow the conventions of the
[full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template/tree/master/backend) or some other FastAPI best practises for anything not already established in this codebase (schema naming, dependency injection, router
structure).

Tests mirror the `app/` structure under `tests/`, using the `session`/`client` fixtures in
`tests/conftest.py` (in-memory SQLite per test, `get_db` overridden).
