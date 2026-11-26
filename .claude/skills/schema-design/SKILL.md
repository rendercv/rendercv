---
name: schema-design
description: Design database tables and migrations for the web editor's persistence (users, cvs, versions, preferences). Use when a feature adds or changes persistent state.
---

# Schema Design

## Invariants

1. A CV's content is **four YAML text documents** (`cv`, `design`, `locale`,
   `settings`) stored as-is. Never decompose CV content into relational
   columns — the pydantic models own that structure and it changes with the
   core. Columns exist only for what the database must query or enforce:
   ids, ownership, names, timestamps, hashes.
2. Baseline tables:
   - `users(id, email UNIQUE, created_at)`
   - `cvs(id, user_id FK, name, cv_yaml, design_yaml, locale_yaml,
     settings_yaml, updated_at, content_hash)`
   - `cv_versions(id, cv_id FK, snapshot of the four documents, created_at)`
     — append-only; pruned by count/age, never updated.
   - `preferences(user_id FK, key, value)` — UI state (yaml mode, zoom,
     collapsed sidebar), one row per key.
3. Portable across SQLite (dev) and Postgres (prod): text + integer +
   timestamp types only; no arrays, no JSONB-specific operators without a
   decision record in `docs/decisions/`.

## Method

1. List the access patterns first (which endpoint runs which query, how
   often) and design for those — not for hypothetical analytics.
2. Concurrency per `docs/patterns/guardrails.md`: autosave uses a
   conditional update (`WHERE updated_at = :seen`) and inserts a version on
   success; a lost race returns 409 so the client can merge. No external
   calls inside transactions.
3. Every change is an alembic migration with a tested downgrade.
4. Propose DDL and wait for explicit approval before touching any live
   database (project guardrail).

## Output format

Schema diff, migration file path, access-pattern table (endpoint → query →
index used), and risks.
