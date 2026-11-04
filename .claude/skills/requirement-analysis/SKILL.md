---
name: requirement-analysis
description: Turn a RenderCV web-editor feature request into acceptance criteria grounded in the YAML schema and the observed rendercv.com UX. Use before implementing any feature.
---

# Requirement Analysis

## Inputs to gather first

1. The feature request, verbatim.
2. `docs/plans/completed/cv-editor-web-app.md` — Context (observed reference
   behavior) and the phase the feature belongs to.
3. The schema ground truth for affected fields: `schema.json` and the
   pydantic models under `src/rendercv/schema/models/`.

## Method

1. **Name the user and the moment**: who is editing what, in which tab
   (CV / Design / Locale / Settings), in which mode (form or YAML).
2. **Map to schema**: list the exact YAML paths touched (e.g.
   `cv.sections.<title>[].highlights`). If a field does not exist in the
   pydantic models, the feature needs a core change — flag it, do not
   assume the web layer can add fields.
3. **Specify both editor modes**: every editable thing must state its form
   representation (control type, placeholder, add/remove/reorder) AND its
   YAML representation, plus what a round-trip must preserve.
4. **Specify feedback**: what the preview shows, when it re-renders, what a
   validation failure looks like in each mode.
5. **Write acceptance criteria** as Given/When/Then, one per behavior,
   each independently checkable by the qa-engineer.

## Output format

- User story (one sentence).
- Affected YAML paths and schema types.
- Acceptance criteria (Given/When/Then list).
- UX notes: states, empty state, error state, keyboard path.
- API touchpoints (existing or new, with owner).
- Open questions (decisions a human must make — never resolve these by
  inventing an answer).
