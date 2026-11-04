# Session Handoff — RenderCV Web Editor

Last updated: 2026-10-20, after the Supabase move reached `main`. Read this
together with [cv-editor-web-app.md](cv-editor-web-app.md), whose Progress
section carries the per-phase verification evidence.

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
