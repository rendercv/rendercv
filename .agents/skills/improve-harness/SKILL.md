---
name: improve-harness
description: Run one explicitly authorized, evidence-backed improvement to a repository's agent guidance, tools, runbooks, or validation. Use only when the user invokes `$improve-harness` or explicitly asks to improve the Harness after observed reusable agent friction. Do not use for ordinary product changes, speculative cleanup, one unexplained agent mistake, or automatic post-task reflection.
---

# Improve Harness

Improve one bounded future-agent behavior without turning every difficult task
into permanent process. Keep consumer truth with its owner and require a fresh
rerun before claiming improvement.

## Establish Authority

- Read `AGENTS.md`, `docs/WORKFLOW.md`, and applicable local instructions.
- Confirm the request authorizes changing Harness behavior. Inspection or a
  request to report friction does not authorize edits.
- Record the initial repository root, revision, branch, status, and unrelated
  changes. Preserve all existing work.
- Treat invocation as authority for this bounded experiment, not for changing
  product policy, weakening proof, adding credentials, or mutating external
  systems.

## 1. Preserve The Baseline

Use an observed task trajectory when available. Record:

- the representative job and accepted outcome;
- the concrete failure and evidence;
- human steering, relay, or recovery required;
- the worker, repository revision, relevant external state, tools, and
  authority; and
- existing proof and known limitations.

Do not diagnose a worker limitation from one run. If no observed baseline
exists, stop with an experiment proposal; do not manufacture one.

Copy `docs/templates/harness-improvement.md` to
`docs/plans/active/harness-improvement-<slug>.md`. Reuse an existing active
record for the same experiment.

## 2. Locate The Earliest Gap

Trace the failure upstream to the first owner that could have prevented or
exposed it:

- **Context:** knowledge was absent, stale, overloaded, or not retrieved.
- **Capability:** discovery, invocation, interpretation, repair, or real-system
  verification failed.
- **Domain ownership:** no canonical type, API, state machine, or source owned
  the invariant.
- **Authority:** permission, approval, audit, or recovery was unclear.
- **Proof:** checks established a proxy rather than the accepted outcome.
- **Environment:** an external prerequisite was unavailable.

Assign the correction to `repository-harness`, the consumer repository, the
external environment, or a human decision. Do not copy consumer commands or
policy into a generic upstream template.

## 3. State And Apply One Intervention

Before editing, write:

```text
If <smallest change> is added at <owner>, then a fresh agent will
<observable change> on <representative job>, because <mechanism>.
Evidence that would weaken this:
Maintenance owner and removal condition:
```

Make only the authorized intervention. Prefer an existing owner, a clearer
route, an actionable diagnostic, a runbook fact, a type or API, or
claim-matched proof over a parallel framework. Keep unknown policy unknown.
Run repository-native checks that protect the changed boundary.

## 4. Require A Fresh Rerun

Use a fresh agent session and an equivalent starting state. Hold the worker,
task class, authority, tools, and relevant external conditions materially
steady. Record separately whether the intervention was available, retrieved or
invoked, and relevant.

If a fresh rerun is not authorized or available, leave the record active with
`Decision: pending fresh rerun`. Report the exact next task; do not claim the
Harness improved.

## 5. Keep, Revise, Or Remove

Compare accepted outcome, claim-matched proof, human intervention, retries,
authority behavior, and maintenance cost.

- **Keep** when the rerun exercised the intervention and improved the bounded
  job enough to justify its cost.
- **Revise** when the owner is correct but the route or interface remains hard
  to use.
- **Remove** when it adds noise, duplicates a better owner, or does not improve
  the job.

Record the decision, evidence, owner, and removal condition. Move the record to
`docs/plans/completed/` only after native validation and the fresh-rerun
decision. Preserve a removed intervention's result in the completed record.

## Report

Return:

- representative job and baseline;
- earliest gap and owner;
- intervention and changed files;
- native validation;
- fresh-rerun status and comparison;
- `keep`, `revise`, `remove`, or `pending fresh rerun`; and
- remaining authority, risk, or follow-up.
