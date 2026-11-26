---
name: documentation
description: Update project documentation after a feature or decision — plan progress, decision records, API contracts, runbooks. Use at the end of every completed work item.
---

# Documentation

## Where each thing goes (repository is the system of record)

| Content | Location | Template |
|---|---|---|
| Lasting product/architecture decision | `docs/decisions/` | `docs/templates/decision.md` |
| Progress, task-local decisions | `docs/plans/completed/cv-editor-web-app.md` | (same file — no parallel logs) |
| API contract | `web/backend/README.md` | method, path, request/response, errors |
| How to run/deploy the app | runbook per `docs/templates/application-runbook.md` | |
| User-facing docs | mkdocs tree under `docs/` | must pass `just build-docs` |

## Method

1. Start from the qa-engineer's verification report; document only what it
   evidences. Unverified behavior is labeled "not yet verified".
2. Update the plan: tick Progress items, append dated Decisions, refresh
   Validation with the actual commands and results.
3. Promote a decision to `docs/decisions/` only when it constrains future
   work (stack choice, schema invariant, API shape) — not routine choices.
4. Style: short sentences, imperative, present tense, no marketing
   adjectives. Match the surrounding file's structure exactly.
5. Finish by listing every file you touched and why in one line each.

## Never

Invent endpoints, results, links, or screenshots; duplicate content across
locations (link instead); leave the plan's Progress section stale after a
phase completes.
