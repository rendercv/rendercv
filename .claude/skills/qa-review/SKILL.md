---
name: qa-review
description: Verify a web-editor feature against its acceptance criteria and the repository gates (just check, just test, web tests). Use after implementation and before any PR to develop.
---

# QA Review

## Gate ladder (run in order; stop and report on first failure)

1. `just check` — must be zero errors (ruff + ty + pre-commit).
2. `just test` — core pipeline regression. Expected on Windows:
   all pass with exactly 2 skips (chmod, schema-generation). Any new
   failure or skip is a finding.
3. Web workspace: backend contract tests, frontend `vitest run`,
   Playwright E2E for the touched flow.
4. Acceptance criteria from the product-analyst, one by one, each marked
   pass/fail with evidence.

## Scenario checklist (probe what breaks this product)

- Round-trip fidelity: YAML with comments and custom section order → edit
  one field in form mode → YAML unchanged except that field.
- Invalid input: YAML parse error vs schema violation vs empty document —
  each shows its own inline error and the last good preview survives.
- Theme switch: defaults merge (margins change), user overrides survive.
- Concurrency: two tabs autosaving the same CV → second gets 409, no
  silent data loss.
- Scale: a 5-page CV renders; a 1MB YAML is rejected by the size cap.
- Localization: a RTL locale (arabic/hebrew/persian exist in core) renders.

## Reporting standard (docs/WORKFLOW.md)

For each gate: the command, the summary line of its output, pass/fail.
Separate facts / limitations / not-attempted. A check you did not run is
"not attempted", never implied as passing. File findings as a ranked list:
severity, reproduction, expected vs actual.
