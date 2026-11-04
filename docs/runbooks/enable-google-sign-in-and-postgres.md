# Application Runbook: Enabling Google sign-in and Postgres

## Scope

The two configuration jobs the web editor still needs from an operator before
it can be deployed: turning on Google sign-in, and moving off the local SQLite
file onto managed Postgres.

Both are configuration, not code. The application runs correctly without
either — anonymous sessions and a SQLite file are a supported mode, and the
sign-in UI stays hidden when no provider is configured.

Both have now been run for real, and both turned up something the tests could
not. The Postgres path failed outright on a first attempt -- migrations
bypassed the driver rewrite entirely (fixed; see **Deterministic State**).
Google sign-in completed end to end against a real client, and the resulting
database showed the promote-in-place path working: one row, carrying the
account identity, still owning the CV written before signing in.

What the automated tests still cannot cover stays true: they patch
`oauth.fetch_google_identity` because the real flow ends at a consent screen
a test cannot drive. So re-run the **Interface** section by hand after any
change to the sign-in flow.

## Prerequisites

- `uv` (Python 3.12+) and Node.js 20+, per `web/README.md`.
- A Google account able to create a project in Google Cloud Console.
- A Postgres provider account (Neon, Railway and Supabase all work; their
  connection strings are all accepted, see **Deterministic State**).
- Nothing is committed: `.env`, `.env.local` and `.env.production` are all
  gitignored. `.env.example` is deliberately still committable, for a template
  carrying names but no values.

**Never paste a client secret into a chat, an issue, or a commit.** It belongs
in `.env` locally and in the deployment's own secret store in production.

## Start

### Google OAuth client

In [Google Cloud Console](https://console.cloud.google.com):

1. Create or select a project.
2. **Google Auth Platform → Branding**: fill in the app name and the two
   email fields (*User support email* and *Developer contact information*).
   Leave the logo and every *App domain* field empty — a logo forces the app
   through verification, and the domain fields need a domain you have
   registered under *Authorized domains*. Under **Data Access**, nothing
   needs adding: `openid email profile` are requested by the application at
   run time and are all non-sensitive.

   The Console section is named *Google Auth Platform* and splits Branding,
   Audience and Clients into separate pages; older documentation (including
   earlier revisions of this file) calls it *APIs & Services → OAuth consent
   screen*, which no longer exists.
3. **Google Auth Platform → Clients → Create client**, type **Web
   application**, and add the redirect URI for the environment:

   | Environment | Authorized redirect URI |
   | --- | --- |
   | Local | `http://localhost:5173/api/auth/google/callback` |
   | Deployment | `https://<your-domain>/api/auth/google/callback` |

   The match is exact: scheme, host, port and path, with no trailing slash.
   Port `5173` is the frontend dev server, not the backend's `8000`, because
   the browser must land back on the origin that holds the session cookie. A
   mismatch fails with `redirect_uri_mismatch` before the application is ever
   reached.

   Both environments need their own entry; adding the production URI does
   not cover localhost.

4. Let other people in by adding their addresses under **Audience → Test
   users**. Left in Testing, Google refuses everyone outside that list *on
   Google's own screen* -- the request never reaches this server, so no
   amount of application code can soften it, and since the editor requires
   an account that is a locked door. The project owner is the exception and
   signs in even with an empty list, which is why verifying this needs a
   second Google account. The list holds 100 addresses and takes effect
   immediately.

5. **Publishing to production is a separate job that needs a deployment, so
   it is not part of this local setup.** Google refuses to switch an app out
   of Testing until *Branding* carries a valid **homepage url** and
   **privacy policy url**, and those must live on a domain registered under
   *Authorized domains* -- `localhost` cannot satisfy either. The button
   stays greyed out with a tooltip saying exactly that. Come back to this
   after the app is deployed, and **remove the logo from *Branding* first**:
   a logo forces the app through Google's verification review, which the
   three scopes it requests (`openid email profile`, all non-sensitive)
   would otherwise not require.

### Local run with sign-in enabled

Write the credentials to `web/backend/.env`:

```
GOOGLE_OAUTH_CLIENT_ID=<client id>
GOOGLE_OAUTH_CLIENT_SECRET=<client secret>
```

Then, in two terminals:

```
cd web/backend
uv run --env-file .env uvicorn rendercv_web.app:app --port 8000
```

```
cd web/frontend
npm run dev
```

`GOOGLE_OAUTH_REDIRECT_URI` can be left unset locally: it defaults to
`http://localhost:5173/api/auth/google/callback`, the same value registered
above. A deployment must set it explicitly.

## Readiness

Sign-in is configured when the server says so, rather than when the file
exists:

```
curl -s http://localhost:8000/api/auth/me
```

`"provider_available": true` means the credentials were read. It stays
`false` when either variable is missing, and the UI then renders no sign-in
control at all — that is the supported unconfigured mode, not a failure.

## Deterministic State

### Postgres

Install the driver. This step is easy to miss and the failure is at startup,
not at first query:

```
cd web/backend
uv sync --extra postgres
```

Postgres is an optional extra because development and the whole test suite run
on SQLite and need no driver.

Run the migration against the new database **before** pointing the application
at it, so a schema problem surfaces on its own rather than inside a failing
request:

```
cd web/backend
RENDERCV_WEB_DATABASE_URL="<connection string>" uv run alembic upgrade head
```

Two `Running upgrade` lines are expected: the baseline schema, then the OAuth
identity columns. Alembic also prints `Context impl PostgresqlImpl`, which is
worth reading -- it confirms the migration really ran against Postgres rather
than falling back to the SQLite default.

This path has now been exercised against a real PostgreSQL 16 server, not
only reasoned about: `alembic upgrade head` from a bare `postgresql://` URL,
the resulting schema inspected (all four tables, the four nullable auth
columns, the `uq_users_auth_provider_identity` constraint), a downgrade and
re-upgrade round trip, and the application started against an empty database
so its own startup migration ran unattended.

The connection string can be pasted exactly as the provider gives it.
`postgres://` (Railway, Heroku), `postgresql://` (Neon, Supabase) and
`postgresql+psycopg://` are all accepted — the first two are rewritten to the
installed driver, because SQLAlchemy has no `postgres` dialect and defaults
`postgresql` to psycopg2, which is not what the extra installs.

The application also migrates on startup, so no manual step is needed
afterwards.

### Supabase (the production database since 2026-10-19)

Replaced Render's managed Postgres after its free instance expired.

1. In Supabase, create a project in **West US (Oregon)**, the service's
   region. Keep the database password out of chat and commits.
2. **Connect → Session pooler**, copy the URI and fill in the password
   (URL-encoded if it has `@`, `#`, `/` or `:`):
   `postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres`
   - Not *Direct connection*: on the free plan it is IPv6-only, and Render
     cannot reach it -- the failure is the same `failed to resolve host` or
     `Network is unreachable` at startup.
   - Not *Transaction pooler* (port 6543): it does not keep prepared
     statements, and psycopg 3 prepares a query after its fifth run, so the
     app works for a few requests and then fails with
     `prepared statement ... does not exist`.
3. Optionally run `alembic upgrade head` against it from a laptop first
   (see above) to see `Context impl PostgresqlImpl` before the service does.
4. Render → `rendercv-web` → **Environment** → set
   `RENDERCV_WEB_DATABASE_URL` to that string → **Save**. Saving deploys;
   the startup migration creates the schema in the empty database.
5. Sign in, write a CV, restart the service, check the CV is still there
   (see **Unknowns** for why this check and not a lighter one).

Done on 2026-10-19 against project `pljtgdmrbjiiguymfhjj` (East US, Ohio --
the free plan offers only continent-level regions). The deploy at 7:30 PM
went live, a CV written after signing in survived a service restart, and
its rows were visible in Supabase's Table Editor. Getting there took four
failed deploys, each with a distinct log line worth recognizing:

| Log line | Cause |
| --- | --- |
| `failed to resolve host 'dpg-...'` | The variable still held the old Render URL -- not saved, or saved on another service |
| `password authentication failed for user "postgres"` | `[YOUR-PASSWORD]`'s brackets left in, or a password reset not yet in the URL |
| `failed to resolve host '<text>@aws-0-...pooler.supabase.com'` | An unencoded `@` in the password |

Separately, two deploys sat on *Deploying...* for 13-18 minutes without a
single log line from the app, before Render timed them out. That is
Render's free plan scheduling the container, not the application; deploy
once and wait rather than re-triggering, which cancels the one in flight.

A free Supabase project **pauses after 7 days without activity**. Unlike
Render's expiry nothing is deleted -- *Restore project* in the Supabase
dashboard brings it back -- but while paused the web service fails every
start exactly as it did when the Render database disappeared.

### Rotating the database password on Render

Done once, on 2026-09-07, after the password leaked. It took the deployment
down for about ten minutes, entirely because of the two surprises below.

The order that works:

1. Database → **Info** → **Credential Rotation** → `+ New default credential`.
2. Copy the new **Internal Database URL** (the service runs inside Render's
   network; External is for `psql` from a laptop).
3. Service → **Environment** → edit `RENDERCV_WEB_DATABASE_URL` → **Save**.
   Saving triggers its own deploy.
4. Sign in to the app and open a CV.
5. Only then delete the old credential.

**Surprise one: creating the new default revokes the old one immediately.**
Render's wording -- "Create new default credentials and delete the old ones
when ready" -- reads as though the old pair keeps working until deleted. It
does not. From the moment the new default exists, the old role answers
`FATAL: role "..." is not permitted to log in`, and because the application
migrates on startup it does not degrade, it exits: `Application startup
failed. Exiting.`, and every URL stops answering. Steps 1 and 3 therefore
belong back to back.

**Surprise two: `Manual Deploy` does not fix it.** `render.yaml` declares

```yaml
- key: RENDERCV_WEB_DATABASE_URL
  fromDatabase:
    name: rendercv-web-db
    property: connectionString
```

but Render resolves that once and stores the result as an ordinary variable
on the service. A redeploy rebuilds the image with the variables that are
already there; it does not re-resolve `fromDatabase`. So a deploy after a
rotation fails with the *old* username -- which is confusing to read, because
that username no longer appears anywhere in the Credential Rotation table.
Step 3 is what actually repairs the service.

Two things worth knowing while diagnosing this:

- A running deployment is proof the database connection works. Startup runs
  `upgrade_to_head`, so the service cannot serve a single byte without it.
  The reverse does not hold: `/api/themes`, `/privacy` and `/api/auth/me`
  (with no cookie) all answer without touching the database, so a `200` from
  them says nothing while the service is starting.
- Read the deploy id in the log header before believing a failure is the
  current one. A stale failed deploy and a live healthy one sit next to each
  other in the dashboard.

### Isolation

The e2e suite must never run against a database anyone cares about — see
`web/README.md`. The same applies here: run these steps against a fresh
database, not one holding real CVs.

## Interface

Local sign-in, end to end:

1. Open <http://localhost:5173>. A **Sign in** link appears in the nav only
   when the server reported `provider_available: true`.
2. Follow it to Google's account chooser and pick an account.
3. You return to `/app`, and the sidebar footer shows the account's name or
   email with a **Sign out** control.

## Runtime Evidence

- `provider_available` from `GET /api/auth/me` is the single source of truth
  for whether the server sees credentials.
- With `GOOGLE_OAUTH_CLIENT_ID` or `GOOGLE_OAUTH_CLIENT_SECRET` missing,
  `GET /api/auth/google/start` returns **503** with a message naming both
  variables, rather than an opaque failure.
- `redirect_uri_mismatch` comes from Google, before any application code runs:
  compare the registered URI against `GOOGLE_OAUTH_REDIRECT_URI` character for
  character.
- The backend logs a warning on every start while `RENDERCV_WEB_SECRET` is
  unset. Nothing enforces it.
- A deployment that serves anything at all has a working database
  connection: the application runs `upgrade_to_head` on startup and exits if
  it cannot. The reverse does not hold -- `/api/themes`, `/privacy` and an
  anonymous `/api/auth/me` all answer without touching the database, so a
  `200` from them proves nothing while a service is starting.
- Render's deploy list shows a failed deploy directly beside a healthy live
  one. Read the deploy id in the log header before believing a failure is
  the current one.

### After every deploy

```
cd web/backend
uv run python scripts/smoke_production.py
```

Twenty-four checks over HTTP against the running deployment, exiting
non-zero if any fails. `--host` points it somewhere else. It signs in to
nothing, so it can be run by anyone at any time; the endpoints that must
stay shut answering **401** is one of the things it asserts.

It exists because two defects reached production while every test on both
sides passed, and neither was visible from inside a test suite:

- **`typst` drifted between the two lockfiles.** The root pinned 0.14.8 and
  `web/backend` had resolved 0.15.0, so a CV that `rendercv render` set on
  one page came out on two in the editor -- same YAML, same fonts,
  byte-identical Typst source. `web/backend/pyproject.toml` now pins
  `typst==0.14.8` and `tests/test_typst_version.py` asserts it against the
  root `uv.lock`. **Raising one means raising both in the same commit**, and
  expecting `just update-testdata` to have something to say.
- **`schema.json` was missing from the image.** `GET /api/schema` answered
  500, and the four form editors are generated from that response, so form
  mode was dead from the day it shipped -- unnoticed, because the editor
  opens in YAML mode and everything else worked. `web/Dockerfile` now copies
  it and calls `load_schema()` at build time, so the build fails rather than
  the first person who switches to the form.

Both live in the gaps between components rather than in any component, which
is the class of defect a smoke test is for.

### Who is using the deployment

```
cd web/backend
uv run --extra postgres python scripts/db_report.py
uv run --extra postgres python scripts/db_report.py --cv <name fragment>
```

Answers how many people have signed in, and which account holds a given CV.
It asks for the connection string through a hidden prompt rather than taking
it as an argument, and masks email addresses unless `--full-emails` is
given -- the database holds other people's CVs, and the published privacy
policy says the data is not used for anything else.

Paste Render's **External Database URL**, using the copy button beside the
row. Selecting the text in that field copies the row of dots the dashboard
displays, not the value behind them; the script recognises that and says so.

## Ownership And Cleanup

- `web/backend/.env` is local and gitignored; delete it to return the machine
  to the unconfigured state.
- Deleting the OAuth client in Google Cloud Console revokes it everywhere.
- A throwaway Postgres database can be dropped at the provider. Do not point
  these steps at a database holding real CVs.

## Validation

Before deployment, all of the following must hold:

| Environment variable | Required | Purpose |
| --- | --- | --- |
| `RENDERCV_WEB_SECRET` | Yes | Signs session cookies. |
| `RENDERCV_WEB_HTTPS` | Yes, over HTTPS | Marks the cookie `Secure`. |
| `RENDERCV_WEB_DATABASE_URL` | Effectively yes | Without it, SQLite in the container, lost on restart. |
| `RENDERCV_WEB_ALLOWED_ORIGINS` | Only across origins | Frontend origins allowed to call the API. |
| `GOOGLE_OAUTH_CLIENT_ID` / `_SECRET` / `_REDIRECT_URI` | Yes | The editor opens only for a signed-in account, so without these nobody can get in. |

Generate a secret with:

```
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

**`RENDERCV_WEB_SECRET` is the one that matters most and is easiest to
forget.** The fallback is a hardcoded string in a public repository, so anyone
can forge a validly signed session cookie and read other people's CVs. The
backend only logs a warning.

If the frontend and API are served from the same origin, CORS needs no
configuration. Across origins, an unlisted origin makes the browser refuse
credentialed requests: the page loads, sign-in and saving silently fail, and
the only clue is a CORS error in the console.

The journey that proves the outcome is the **Interface** section run against
the deployment, not against localhost. **It has now been run there**, on
2026-09-06, against `https://rendercv-web-uk68.onrender.com`.

It was run as a listed test user rather than as the project owner, which is
the only version of it that proves anything. Google lets a project's owner
through in every configuration -- with the *Test users* list empty, with the
allowlist misconfigured -- so the owner signing in successfully is
compatible with the deployment being broken for everyone else. An account
with no privileges gets in only because the configuration is right.

Checked from outside before that, in this order, each answering a question
the next depends on:

| Check | Answer |
| --- | --- |
| `GET /openapi.json` | `RenderCV Web Editor API` -- the deployment is this app |
| `GET /api/auth/me` | `provider_available: true` -- the server read both credentials |
| `GET /api/auth/google/start` | sends `redirect_uri=https://<host>/api/auth/google/callback` |
| Following that to Google | Google's sign-in page, not `redirect_uri_mismatch` -- the URI is registered |

The first version of `GOOGLE_OAUTH_REDIRECT_URI` on the deployment was the
bare host, with no path. Worth naming because of how it fails: Google would
send the user to the landing page, no callback handler would run, no cookie
would be set, and the browser would show a page that looks fine. There is no
error anywhere in that sequence.

## Unknowns

Most of what stood here was answered by the deployment on 2026-09-06, and
the publish gate on 2026-09-08. One entry is left, and it is not about
whether the thing runs.

- **Where the deployment stores secrets.** They are Render environment
  variables now, which is where this runbook assumed they would be; it
  still does not choose a secret manager, and `RENDERCV_WEB_SECRET` being
  generated by `render.yaml` rather than by a person is the only reason it
  cannot be forgotten.

Answered, and recorded here so the next reader does not re-open them:

- **The app is published and strangers can sign in.** Audience reports
  `Publishing status: In production`, `User type: External`, and the
  Verification Center says outright: *"Verification is not required since
  your app is not requesting any sensitive or restricted scopes."*
  Confirmed 2026-09-08 by someone outside the test-user list signing in
  successfully. So the non-sensitive scopes do skip verification, as hoped.
- **The branding will not verify, and that was accepted.** Google refuses
  the home-page URL with *"the website ... is not registered to you"*, and
  it keeps refusing after the domain is verified in Search Console -- the
  property is verified, owned by the same account that owns the Cloud
  project, and the verification file is served -- it lives at
  `web/frontend/static/googlecdc32a5d8f95119a.html` and is guarded by an
  e2e test, because nothing in the application reads it and deleting it
  would show no symptom here at all. The remaining explanation is that `onrender.com` is Render's
  shared domain and the check wants the registrable domain, which will
  never belong to this project. The consequence is cosmetic: the consent
  screen does not show the app name, home page or privacy link. **Do not
  re-run this investigation** -- reopen it only if a custom domain is
  bought, which would also mean changing the Render custom domain,
  `GOOGLE_OAUTH_REDIRECT_URI`, the OAuth client's redirect URI, the three
  Branding URLs, and creating a DNS-verified Search Console property.
- **Uploading an app logo forces verification.** The Branding page says so
  itself. It is left empty deliberately.

- **The deployment really is on Postgres**, confirmed 2026-09-06 by
  restarting the service and signing in again: the CVs were still there.
  That test is the one worth repeating on any new deployment, because the
  failure it rules out is invisible until it happens. The code falls back
  to a SQLite file when `RENDERCV_WEB_DATABASE_URL` is missing, and a
  container on SQLite behaves exactly like one on Postgres -- until it
  restarts with a fresh filesystem and every CV is gone. A successful
  sign-in proves only that *a* database accepted a write; it does not say
  which. On Render's free plan the service sleeps after fifteen minutes of
  no traffic, so on SQLite that loss would happen several times a day.
- The Postgres provider was Render's managed database until 2026-10-19,
  connected by `render.yaml` rather than by a pasted connection string. It
  is now Supabase, by a pasted string -- see **Supabase** above. The
  password-rotation section above describes the Render database and no
  longer applies as written.
- **Render's free Postgres expires.** It did, about a month after
  creation: by 2026-10-19 the dashboard showed *"Free database expired"*,
  the database was suspended with deletion due within a day, and the web
  service failed every start with `failed to resolve host
  'dpg-daen9if40ujc73fumqn0-a'`. It was deleted by hand on 2026-10-20,
  after the move to Supabase reached `main`. The web service's own deploy history stays
  green throughout, so the deploy list is not where this shows -- the
  database page and the application logs are. `plan: free` on the database
  in `render.yaml` is only fit for a demo; anything holding real users' CVs
  needs a paid plan or a provider without an expiry.
- The production domain is `rendercv-web-uk68.onrender.com`, and the
  redirect URI is that host plus `/api/auth/google/callback`.
