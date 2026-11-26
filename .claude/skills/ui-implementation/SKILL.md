---
name: ui-implementation
description: Build SvelteKit UI for the web editor — the three-pane layout, four tabs, form ↔ YAML two-way sync, live preview, theme switcher. Use for all frontend feature work.
---

# UI Implementation

## The reference behavior (reproduce, don't redesign)

Observed on rendercv.com (details in the plan's Context section):

- Three panes: collapsible CV sidebar · editor (tabs: CV, Design, Locale,
  Settings) · PDF preview. Top bar: undo/redo, markdown B/I/link, YAML
  toggle, zoom, download, share.
- YAML mode: line numbers, syntax highlighting, markdown links clickable.
  Form mode: label + value rows, placeholders are example values
  ("Mechanical Engineer", "+1 555 123 4567"), `+ Add` for arrays, segmented
  controls for enums (A4 / US Letter), toggles for booleans, color swatch +
  rgb text, `<` `>` steppers for fonts and theme.
- Theme switch re-renders the preview AND merges that theme's defaults into
  the design form (Classic 0.7in margins → Ember 0.6in).

## Architecture rules

1. **One store, two views**: the parsed document store is the single source
   of truth; the YAML editor and the form both read/write it. A change in
   either must appear in the other without focus loss or cursor jump.
2. **Schema-driven form**: build controls from `/api/schema` field types.
   Adding a field to the pydantic models must light up in the form with no
   frontend change.
3. **Preview loop**: store change → debounce ~800ms → `/api/render` →
   `URL.createObjectURL` → embedded viewer. Revoke stale blob URLs. Show a
   skeleton while the first render is pending (the reference does).
4. **Errors inline**: `/api/validate` runs on the same debounce; YAML mode
   marks the line, form mode marks the field. The last good preview stays
   visible while the document is invalid.
5. Undo/redo is a document-store history stack (form and YAML edits share
   it), like the reference.

## Quality bar

TypeScript strict; Vitest for the sync logic (YAML→form→YAML round-trip
preserves comments/order via the backend round-trip endpoint); Playwright
for edit→preview; keyboard-accessible controls with labels; dark/light via
CSS tokens.
