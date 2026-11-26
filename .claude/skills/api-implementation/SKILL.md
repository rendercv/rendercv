---
name: api-implementation
description: Implement FastAPI endpoints in web/backend that wrap the rendercv core — request/response contracts, error boundary, caching, tests. Use for all server-side feature work.
---

# API Implementation

## Core endpoints (the contract to extend, not replace)

| Endpoint | Purpose | Core function used |
|---|---|---|
| `POST /api/validate` | 4 YAML docs → ok or structured errors | `build_rendercv_dictionary_and_model()` |
| `POST /api/render` | 4 YAML docs → PDF bytes | renderer pipeline (as in `run_rendercv.py`) |
| `GET /api/schema` | JSON Schema for the form generator | repo `schema.json` |
| `GET /api/themes` | theme names + per-theme design defaults | `schema/models/design/` |
| `POST /api/files` | debounced autosave | persistence layer |

## Method

1. **Wrap, don't reimplement**: any behavior that exists in `rendercv`
   (validation, date logic, theme defaults, rendering) is imported. If the
   web layer needs something the core almost does, change the core with
   tests — never fork the logic.
2. Request/response models are pydantic; nothing enters the pipeline
   unvalidated (guardrails: "trust no one" — a request body can be 1M chars;
   cap sizes explicitly).
3. One error boundary: `RenderCVUserError` family → 422 with
   `{errors: [{location, message, yaml_line}]}` (reuse the structured data
   the core already produces); unexpected exceptions → 500 with an opaque
   id, full detail only in server logs. Never leak stack traces.
4. Renders are expensive: cache by `(sha256(yaml docs), theme)`, debounce is
   the client's job, but the server still rate-limits per session.
5. Repo conventions apply (`CLAUDE.md`): strict typing, `just check` zero
   errors, Google-style docstrings with Why.

## Tests (required, same PR)

Contract tests in `web/backend/tests/` per endpoint: happy path with a
sample YAML from `examples/`, each error class, the cache hit, and the size
cap. Run them and paste the summary line in your report.
