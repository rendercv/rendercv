# Session Handoff — RenderCV Web Editor

Last updated: 2026-11-26, after release PR #75 went live. Read this
together with [cv-editor-web-app.md](cv-editor-web-app.md), whose Progress
section carries the per-phase verification evidence.

## Status on 2026-11-26: live, after two outages caused by the database

`main` is at release PR #75 (`5799e137`) and that commit is what Render
serves: deploy `dep-dc3qivbbc2fs738smgvg`, triggered by the merge at
10:37 AM (+07:00), live about a minute later.

| Check (2026-11-26) | Result |
| --- | --- |
| Render `rendercv-web`, before the release | Live on `7676d84`. `/`, `/app`, `/api/themes` answer 200; the first request took 52 s (free instance waking up) |
| Render `rendercv-web`, after the release | Live on `5799e137`. `/`, `/app`, `/api/themes` answer 200, and the served bundle `nodes/3.*.js` contains `color-scheme: light` (PR #73's fix) |
| Supabase `RenderCV-Web` | Status *Healthy*, Nano, 5/60 connections |
| Real use after recovery (10:11 AM) | A signed-in session ran `/api/auth/me`, `/api/cvs`, `/api/render`, `PUT /api/cvs/30` -- all 200/204, so the database reads and writes again |
| `/api/cvs` without a session | 401 *Sign in to use this endpoint.* -- expected |

**The outages.** Render's Events page shows the instance failing to start
(exit status 3) repeatedly on **2026-11-20, 02:25–02:37 AM** (instance
`9fs9h`) and **2026-11-26, 09:59–10:07 AM** (instance `ngtw8`). Every failure
has the same log:

```text
psycopg.OperationalError: connection to server at "...", port 5432 failed:
FATAL: (EAUTHQUERY) authentication query failed: connection to database not available
host: aws-0-us-east-2.pooler.supabase.com
ERROR: Application startup failed. Exiting.
```

The Supabase pooler answered, but the database behind it did not. That is
what a paused free project looks like (see *Watch for* below); Supabase's
dashboard also carried a "technical issue" banner on 2026-11-26. Which of the
two it was is not verified. Either way the cause was outside this repository,
and no code change was needed.

**Still open:** while the database is unreachable the whole app refuses to
start, so even the landing page and the anonymous editor go down. Keeping
the project awake (a scheduled ping) or a paid Supabase plan would prevent
it.

## Work merged after 2026-10-20 (PR #58 – #71)

All on `main` and deployed:

- PR #58: this handoff recorded the Supabase move.
- PR #61: the form editor no longer makes the whole page scroll.
- PR #62: the design panel shows when it overrides its theme, and resets it in one click.
- PR #64: undo and redo restyled as glowing tiles.
- PR #66: the page footer is off by default.
- PR #68: each theme's design is remembered, so switching back restores it.
- PR #70: the last CVs in the list can open their actions menu (it was clipped).
- PR #59, #63, #65, #67, #69, #71: `develop → main` releases.

## Work released on 2026-11-26 (PR #72 – #75)

- PR #73: the CV preview stays white paper in dark mode. The preview iframe
  had inherited `color-scheme: dark`, so Chrome's PDF viewer painted the
  pages dark. Confirmed by eye on a side-by-side test page (same PDF, dark
  page: the iframe without the fix rendered dark, the one with
  `color-scheme: light` rendered white). No automated test covers it,
  because Playwright cannot see inside Chrome's PDF viewer.
- PR #74: this handoff recorded the deployment check above.
- PR #72 (progress notes from 2026-11-05): closed unmerged, superseded by #74.
- PR #75: `develop → main` release of #73 and #74.

Not yet checked: the fix inside the real app on production, by a person in
dark mode.

## Next

- Keep-awake job (branch `quan-keep-supabase-awake`): `GET /api/health/db`
  runs `SELECT 1`, and `.github/workflows/keep-supabase-awake.yaml` calls
  it daily at 02:17 UTC, so the free Supabase project never reaches 7 idle
  days. When the database is already paused, the job fails and GitHub
  emails the owner. It only runs once it is on `main`. Not yet verified:
  that a query through the pooler counts as activity for Supabase. Check
  that the project is still awake after 7+ days.
- Still open: the app cannot start at all without the database. Letting it
  start, with only the signed-in features failing, would keep the landing
  page up.
- This machine has no global git identity. Commits made here pass
  `-c user.name=... -c user.email=...` with the author of the earlier commits.

## Status on 2026-10-20: back up, on Supabase

`main` and `develop` are identical at PR #57 (`a5a2ea83`). The deployment
is live and its database is Supabase.

| Resource | Status |
| --- | --- |
| `rendercv-web` (Render, Docker, free) | Live. The auto-deploy of `a5a2ea83` went live in about a minute on 2026-10-20; `/api/themes`, `/` and `/app` answer 200 |
| Supabase project `RenderCV-Web` (`pljtgdmrbjiiguymfhjj`, us-east-2, free) | Holds the data. Reached through the **Session pooler**, port 5432. Sign-in, creating a CV, and the CV surviving a restart were checked by hand on 2026-10-19 |
| `rendercv-web-db` (Render Postgres, free) | **Deleted** by the user on 2026-10-20. It had expired on 2026-10-19 and its data was given up, not copied |
| `p041-backend` and the `P041-Version-3.0` Blueprint | Another repository's. Not this project |

### What happened, 2026-10-19 → 2026-10-20

Render's free Postgres expires about a month after creation. On 2026-10-19
it was suspended (*"Free database expired"*), and every start of the web
service failed with `failed to resolve host 'dpg-daen9if40ujc73fumqn0-a'`.
The options were: upgrade it to paid, recreate another free one (which
expires the same way), or move to a provider without an expiry.

**Chosen: move to Supabase, without copying the data.** The existing
accounts and CVs were given up.

- PR #55: this handoff and the runbook record the outage.
- PR #56: `render.yaml` no longer declares a database;
  `RENDERCV_WEB_DATABASE_URL` is `sync: false` and holds Supabase's Session
  pooler string, set by hand on Render. The steps and the failures met on the
  way (password left in brackets, an unencoded `@`, the direct connection
  being IPv6-only, deploys hanging on free-plan scheduling) are in
  [the runbook](../../runbooks/enable-google-sign-in-and-postgres.md#supabase-the-production-database-since-2026-10-19).
- PR #57: release `develop → main`.
- The old Render database was deleted afterwards, once nothing pointed at it.

### Watch for

- **A free Supabase project pauses after 7 days without activity.** The
  service then fails at startup the same way. *Restore* on the Supabase
  dashboard brings it back with the data intact.
- A free Render instance sleeps after 15 minutes; the first request then
  takes 30–60 s. Deploys on the free plan can also wait 10+ minutes for a
  container with no application log at all -- that is Render, not the code.
- The database password was pasted into a chat session during the move; it
  should be (or have been) reset under Supabase → Database → Settings, and
  the new string saved on Render.

## Work merged after the plan closed (PR #20 – #57)

All of it on `main` and deployed (PR #55 – #57 are the Supabase move above):

- Deployment proved on Render: Postgres confirmed by restart, a smoke test
  from outside, schema.json and the core's Typst baked into the image, the
  image slimmed by 712 MB.
- Google sign-in published to external users; Search Console verification;
  privacy policy; account deletion.
- Editor: a new CV opens on the filled-in example; YAML download and
  import; download as images (every page); form editors fixed; theme
  switcher no longer shows a stale document.
- Operations: database password rotation runbook, a script reporting who
  uses the deployment, deploy checks recorded in
  [the runbook](../../runbooks/enable-google-sign-in-and-postgres.md).

## Where things stand

**The plan is complete.** Everything is merged to `develop`:

- PR #1 (`dd8250e`'s parent, `f831a58`) — phases 0-5, the build roadmap.
- PR #2 (`dd8250e`) — phase 6: landing-first routing, Google sign-in, and
  the fixes that made deployment actually possible.

`main` is untouched and still guarded by the PreToolUse hook. Branches
`quan` and `quan-phase6` are merged but not deleted.

Gates on `develop`: core 1540 passed (2 Windows skips), backend 104/104,
svelte-check 0 errors (366 files), Vitest 295/295, Playwright 35/35,
`just check` clean.

## What is left, and it is not code

Both need credentials this repository does not have:

1. **Google OAuth.** Create a client in Google Cloud Console and set
   `GOOGLE_OAUTH_CLIENT_ID` / `_SECRET` / `_REDIRECT_URI`. The exact
   redirect URI is in `web/README.md`. Until then the app runs anonymously
   and the sign-in UI stays hidden, which is a supported state, not a
   broken one. The backend tests patch one seam because the real flow ends
   at Google's consent screen, so **the first real sign-in still needs a
   human**.
2. **Postgres.** Pick a provider, then run the migration against it before
   anything else: only driver and dialect resolution were exercised here
   (the Docker daemon was unavailable), plus the full migration round trip
   on SQLite. `uv sync --extra postgres` is required; a pasted
   `postgres://` or `postgresql://` URL is normalized in code.

`RENDERCV_WEB_SECRET` and `RENDERCV_WEB_HTTPS` must both be set before any
deployment. `web/README.md` is the operator's document; this file is not.

## How this project was run

1. Per phase: present a change list → user approves → implement → run every
   gate → report → commit only after the user has seen the result.
2. Push over HTTPS; SSH is broken on this machine:
   `git push https://github.com/NguyenMinhQuan-2A202601478/rendercv_P-041.git <branch>`
3. `/code-review` after each PR, before merging. It earned its place: it
   found 10 real defects in PR #1 and 5 in PR #2, including one that
   destroyed a user's account when a second person signed in on the same
   browser. Both times the fixes came with regression tests that were
   verified to fail without them.

## Gates

- Repo: `just check`, `just test` (expect 2 Windows skips).
- Backend: `cd web/backend && uv run pytest -q`.
- Frontend: `npm run check && npm run test && npm run build`, then
  `npx playwright test` — the e2e suite needs a backend on port 8000 with a
  **throwaway** database, never `web/backend/data/rendercv_web.db`. See
  `web/README.md` for the exact commands.

## Known debt

None of it blocking, all of it recorded in the plan's Result section:

- Signing out is account-wide, not per-device: one account has one
  `session_token`, and per-device sessions need a `sessions` table. The
  safe direction of the two was chosen deliberately.
- The favicon is still the SvelteKit default.
- The photo field accepts a URL but not an upload; local paths 422 by
  design, with a clear message.
- Placeholder documents are defined twice — `web/backend/defaults.py` and
  the frontend's `createDefaultDocuments()` — with no shared source.
- The versions/history panel has no e2e coverage.
- Harness payload files (`.agents/`, `.harness-core/`,
  `docs/assets/rendercv_skill.zip`) and `graphify-out/` sit modified by
  hooks and uncommitted; commit as a chore or discard, the user's call.
- `full_repository/` and `image/` are the user's untracked scratch
  directories at the repository root — leave them alone.
