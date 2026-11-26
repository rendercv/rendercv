# 0001 Remember each theme's design per CV, on the server

Date: 2026-11-04

## Status

Accepted

## Context

The theme switcher replaces the whole `design:` block with the new theme's
defaults. It has to: the starter design spells out every option, and those
explicit values beat the theme name, so renaming the theme alone changes
nothing. The cost was that any tuning was lost on a round trip. A CV fitted
to one page under Harvard (section spacing `0.25cm`, entry spacing `0.7em`)
came back from a single click on `‹ ›` with Harvard's defaults (`0.5cm`,
`1em`) and ran onto a second page.

The user edits the same CVs from two machines, so a copy kept in the
browser would not be enough.

## Decision

Each CV keeps a `{theme: design}` map in a new `cvs.theme_designs` column.
It is JSON stored as `TEXT`, keeping to the portable column types rule in
`db/models.py`. When the user leaves a theme, the editor stores the design
it is leaving with `PUT /api/cvs/{id}/theme-designs/{theme}`. When the user
arrives at a theme, the editor asks for that theme's design with `GET` and
restores it. Only a theme never left before arrives at its defaults.

- The write leaves `updated_at` and `content_hash` alone. It does not change
  what renders, and moving `updated_at` would make the open editor's next
  autosave 409 against itself.
- Only built-in theme names are accepted, so the map stays at most one entry
  per theme. A design must name the theme in the path, and is held to the
  document size cap.
- The editor reads at switch time, not on CV load, so a design stored on the
  other machine after this one opened the CV still wins.
- A per-tab copy covers the moments the server cannot be reached. When that
  happens a notice says the design is kept in this tab only.
- Duplicating a CV copies the map. Deleting the CV deletes it with the row.
- Reset still means "this theme's defaults" and does not touch the map.

## Alternatives Considered

1. Browser `localStorage` only. No schema change, but invisible to the
   user's other machine, which was the requirement.
2. The existing `preferences` table, one key per CV and theme. No migration,
   but entries outlive a deleted CV, are not copied with a duplicate, and a
   value is capped at 4096 characters, below a full design.
3. Carrying the edited values over to the new theme. This was rejected
   because values tuned for one theme's layout are not meaningful for
   another's, and the result could still overflow the page.
4. Sending the map with the autosave `PUT /api/cvs/{id}`. That would tie it
   to the four-document payload, conflict handling and version snapshots,
   for data that does not render.

## Consequences

Positive:

- A design survives switching away and back, on either machine.
- No change to the autosave contract or version history.

Tradeoffs:

- Version history does not snapshot the map. Restoring an old version leaves
  the remembered designs as they are.
- Two machines leaving the same theme at once: the last write wins for that
  theme. The row lock keeps writes for different themes from dropping each
  other.
- Once migration `b7d2e41c9a05` has run, a deploy of older code fails at
  startup: Alembic cannot find the newer revision. To roll back, first run
  `alembic downgrade 320e31bb905f` against the database.

## Follow-Up

- None planned.
