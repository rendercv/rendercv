---
name: onboard-repository
description: Inspect an unfamiliar or brownfield repository, trace one real operational path, and propose evidence-backed improvements that help future agents work independently. Use when explicitly asked to onboard, map, assess, or backfill agent-facing repository guidance; use again after the user approves exact proposal items. The first pass is read-only and must not edit files, install tools, start services, create state, or infer missing product policy.
---

# Onboard Repository

Turn an unfamiliar repository into a verified map for future work. Treat the
repository as the system of record. Separate facts from gaps and suggestions.

## Safety Contract

The first pass is always inspection and proposal only, even when the worktree
is writable.

- Read every applicable `AGENTS.md` before inspecting deeper files.
- Capture the initial Git root, revision, branch, status, and worktree list.
- Preserve all pre-existing tracked and untracked changes.
- In the initial boundary capture, before deeper repository inspection, record
  pre-state existence or safe hashes for relevant ignored state such as
  `.env.local`, dependency directories, and managed repository state. Never
  print secret contents. If an initial baseline was missed, report pre/post
  equivalence as **Unknown**; a later sample cannot reconstruct it.
- Treat ignore rules and managed-state manifests as part of the boundary, not
  deeper inspection. Read them before fixing the baseline, enumerate every
  relevant ignored database, sidecar, dependency, environment, build, and
  managed-state path they reveal, and record each one explicitly. For ignored
  directories, use a content-sensitive per-file hash inventory; a filenames-
  only hash does not prove that contents stayed unchanged.
- Use only read-only discovery commands. Do not install dependencies, start
  services, invoke migrations, create caches or state, or edit files.
- Use task-prefixed shell variable names. In zsh, never assign to special names
  such as `path`, `status`, `pipestatus`, `commands`, or their uppercase system
  counterparts; corrupting the inspection shell invalidates later baselines.
- Do not create temporary files inside or outside the repository. Compare via
  stdout and non-materializing pipelines; if a comparison requires a file,
  report that limitation instead of creating one.
- Do not use shell heredocs or here-strings; shells may materialize them as
  temporary files. Use quoted `python3 -c`/`node -e` programs, stdin pipes, or
  ordinary read-only commands instead.
- When a runtime manager is relevant, capture its observable project, service,
  volume, and process state in the initial boundary batch. If the manager is
  unavailable, state that runtime pre/post equivalence is **Unknown**. Proving
  that no runtime command was issued does not prove runtime state was unchanged.
- Before invoking a repository-local binary, verify that its path exists and is
  executable. If absent, record the command as unavailable; do not invoke,
  install, rebuild, or substitute it.
- Do not turn code, tests, configuration, conventions, or guesses into product
  intent. They can prove present behavior, not missing normative policy.
- Stop when authority is absent or materially different interpretations remain.
- End by comparing Git status and diff with the captured initial state.

An explicit later approval may authorize documentation changes. It never
authorizes application-code changes, invented product policy, hooks, databases,
or background automation unless the user separately requests them.

## First Pass: Inspect And Propose

### 1. Establish the boundary

Read applicable instructions and the smallest repository map available. Record
pre-existing dirt before doing anything else. If instructions conflict, follow
the narrower instruction and report the conflict.

When `.harness-core/manifest.json` exists and an installed managed file
conflicts with `.harness-core/base/<path>`, treat the installed file as active
instructions for the current run. For a correction proposal, verify the base
file against its manifest checksum and show the conflict. Propose replacing
only content inside managed markers and preserve all consumer-owned content
outside them. Do not treat the managed base as permission to edit.

A checksum-verified conflict in an active mandatory instruction that caused a
failed, unavailable, or unsafe command is the first proposal priority. Preview
that correction before proposing additive documentation elsewhere.

### 2. Find repository authority

Inspect only material needed to understand the requested path, normally:

- root overview and developer documentation;
- product and architecture sources;
- package/build manifests and task runners;
- CI workflows and deployment/runtime configuration;
- focused tests, fixtures, and operational scripts.

For every important claim, cite an exact repository path and classify it:

- **Authoritative:** an instruction, accepted decision, product contract, or
  explicitly documented operational procedure states what must happen.
- **Observed:** code, configuration, or tests show current behavior.
- **Derived:** a direct operational consequence of verified implementation or
  configuration. Phrase it as current behavior, not intended or durable policy.
- **Decision required:** a proposed normative, product, or safety policy has no
  existing authority and requires an explicit user choice.
- **Unknown:** the repository does not establish the answer.

Never silently promote **Observed**, **Derived**, **Decision required**, or
**Unknown** to **Authoritative**.

Treat operational authority as context-specific. A command or flag documented
for CI, a container build, release automation, or another runbook proves only
that context. Do not transplant it into a local developer procedure unless the
local owning document authorizes it or the user chooses it. When two viable
commands differ, do not select one as a **Derived** rule; classify the choice as
**Decision required**.

When evidence comes from a type, schema, or serializer, distinguish required
from optional fields. Say that optional fields appear only when present; a
field's existence in a schema does not prove that every emitted record has it.

Verify every clause and qualifier in a proposed sentence independently. Do not
generalize configurability, defaults, optionality, ownership, or lifecycle from
one field or resource to an adjacent one merely because they appear together.

For environment-derived behavior, trace each claimed key from every source to
its final consumer. Distinguish same-key merge precedence, fallback between
different keys, checked-in values that make later fallbacks unreachable on the
default path, and assignments performed after a merge. Never summarize this as
"the environment overrides the files" unless that is true for every named key.

List related identifiers separately and label each one **fixed**,
**defaulted**, or **configurable**, with its own source. Apply the same rule to
ports, paths, and resource names: state both configurability and fallback when
either exists. Assign each write to the stage where it actually occurs rather
than grouping later interface writes into setup or readiness.

The current task or frozen evaluation prompt defines run scope, not durable
repository authority. A new rule supported only by that prompt is **Decision
required** unless the user explicitly adopts it as repository policy.

### 2a. Compare documented invariants with executable checks

During the read-only proposal pass, compare accepted architecture, reliability,
security, and quality invariants with the repository's checked-in validation.
This is an inventory, not authority to edit or enforce.

Use one row per invariant or check:

| Documented invariant or executable check | Authority and source | Validation owner and command | Local coverage | CI discovery | Finding |
| --- | --- | --- | --- | --- | --- |

Classify findings precisely:

- **Enforced:** accepted authority and a mechanical check cover the same scope.
- **Partially enforced:** the check covers only part of the accepted scope.
- **Unenforced rule:** accepted authority exists, but no matching check was found.
- **Check lacking authority:** a check exists, but no accepted source establishes
  its policy. Code, tests, conventions, and defaults cannot fill this gap.
- **Unknown:** available evidence cannot establish the relationship.

Inspect the native validation owner and checked-in CI invocation separately. A
local command, an optional hook, CI configuration, and external branch
protection are different enforcement levels; do not infer one from another.

Do not add, edit, delete, enable, or execute a guard during onboarding. Do not
install hooks or mutate CI, merge, or branch-protection settings. Report the
mismatch with evidence and propose the smallest next step: encode an accepted
rule, obtain a missing decision, or investigate an unknown. Any later edit or
enforcement still requires exact user approval and the repository authority
gate.

### 3. Trace one complete operational path

Prefer one already-documented local happy path over a broad architecture
summary. Trace cause and effect through:

```text
prerequisites
-> start
-> readiness
-> deterministic setup
-> real interface exercise
-> evidence and correlation boundary
-> stop and cleanup
```

Use this exact operational-path table schema; do not merge columns:

| Stage or branch | Command/interface and expected result | Classification and source | Write at this stage | Process/container owner | Host and container ports | Evidence/log boundary and correlation | Cleanup at this stage | Unknowns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Include a value or **N/A**/**Unknown** in every cell. An omitted or implicit
cell fails the operational-path gate; prose elsewhere does not replace it.

Trace lifecycle flags as separate table rows. At minimum, include default
startup, each no-start mode, cleanup requested after success, and failure after
startup. For a no-start mode, continue tracing later schema, probe, interface,
and write behavior rather than assuming the flag makes the whole run read-only.
Verify whether cleanup is unconditional, after assertions, or in a
`finally`/trap path. "No teardown command is invoked" does not prove that every
service remains running, and a cleanup flag must not be described as guaranteed
when earlier failure bypasses it.

Classify cleanup mechanics separately from cleanup obligations. Existing code
or an authorized command may prove how cleanup can be performed; it does not
create a new instruction that an operator must perform cleanup after a specific
failure. Put that obligation in **Decision required** unless repository
authority already states it.

If a read-only inspection contacts a runtime manager such as Docker, capture
the relevant project/container identifiers and pre/post state. Never describe
logs as instance-local merely because they are container logs; identify the
actual project/container boundary and correlation identifiers.

Before the path table, add a resource-and-identifier ledger:

| Item | Kind | Exact behavior or value | Classification and source |
| --- | --- | --- | --- |

Use one row per identifier, port, project, service, volume, state path, and log
boundary. `Kind` must distinguish **fixed**, **defaulted**, **configurable**,
**generated**, **logical configuration name**, and **observed runtime name**.
For port mappings, list host and container sides separately. Never report a
logical Compose volume key as an observed engine-level volume name.

One row means one item: do not combine two identifiers or resources in a single
row even when their classification is identical. Record checked-in values that
make later fallbacks unreachable on the documented default path. For logs,
state which fields are guaranteed and which are optional; optional identity or
warning fields make evidence request-correlatable only when present. Keep
process-wide metrics separate from request- or instance-correlated evidence.

Source the entire causal chain for each effect. An HTTP controller does not by
itself prove persistence, and a runner call does not by itself prove provider,
logging, database, or runtime-manager consequences. Mark direct implementation
facts **Observed** and consequences of a called tool or protocol **Derived**.
Pre-existing resources under a no-start mode have **Unknown** creator/owner
unless the repository or runtime observation identifies it.

Do not execute the path during the first pass. The goal is to learn whether a
fresh agent could execute it without undocumented human help.

### 4. Propose the smallest useful backfill

Return a proposal; do not write it. Each item must include:

1. the concrete agent failure it prevents;
2. evidence and exact source paths;
3. the exact destination file or existing section;
4. the factual content to add or correct;
5. what remains unknown and must not be claimed;
6. how a fresh agent replay would prove improvement.

Show all six headings for every proposal, including `Unknowns: none` when no
unresolved factual claim affects that proposal. Do not infer completion of a
field from prose in another section.

Prepare an exact patch preview. Classify and cite every proposed sentence, not
merely the proposal containing it. The approval unit is the machine-emitted
hunk ID, destination, and patch digest, not a proposal number or an ambiguous
alternative.

Never handwrite unified-diff headers, line ranges, context, or patch hashes.
Construct the complete proposed destination image in memory from the pinned
destination, preserving every byte outside the intended edit. Pipe those
complete bytes to the bundled renderer:

```text
<non-materializing command that prints the complete after image> |
  python3 .agents/skills/onboard-repository/scripts/render_patch.py \
    --repository <tested-root> \
    --revision <full-tested-revision> \
    --destination <repository-relative-path> \
    --hunk-id H1
```

Use the standalone renderer only as a preflight when needed. Do not copy its
output into the final answer or manually repair it. Correct the complete after
image and rerun it. The final bundle emitter invokes the same renderer and
produces the canonical marked diff and digests. A renderer failure excludes
that proposal from the approval bundle. Rendering is read-only and creates no
draft file.

Give every emitted diff hunk a stable `H1`, `H2`, ... identifier. The emitter
wraps it exactly as follows:

````text
<!-- ONBOARDING_PATCH:H1:BEGIN -->
```diff
<one complete diff hunk>
```
<!-- ONBOARDING_PATCH:H1:END -->
````

The hunk digest is SHA-256 over the exact UTF-8 bytes inside the `diff` fence,
including one final newline and excluding the fence lines. Do not reuse an
identifier or place two hunks inside one marker pair.

For control-flow wording, cite every branch needed to prove the whole clause:
flag parsing, startup, checks, failure handling, and teardown as applicable. A
single line that initializes a flag or collection does not prove later
lifecycle behavior.

Treat temporal words as causal claims. Before writing `before`, `after`,
`successful`, `complete`, or `finally`, locate the exact success/failure signal
and every awaited operation around it. If teardown runs before the success
signal and can itself fail, say `after all preceding checks succeed, the runner
attempts teardown`; do not call it teardown `after a successful run`.

Do not promote a sentinel or partial probe into an aggregate claim. Wording
such as `the schema`, `the configuration`, `all required resources`, or `the
system is ready` requires an enumerated membership boundary and evidence for
every member. Otherwise name the exact object checked, such as `checks whether
processed_webhook_events exists`. One table probe does not prove that a
multi-table schema is present.

Phrase negative lifecycle evidence narrowly. Skipping or bypassing a teardown
call proves only that this runner does not invoke that teardown; it does not
prove resources remain running. Prefer `the runner does not invoke Compose
down` over `the runner leaves the stack running` unless runtime evidence proves
the stronger state.

Before displaying a command as new runbook guidance, require authority from the
same operational context. Code may prove that dependencies are required, but a
CI install command does not determine the approved local install command or
flags.

Order proposals by causal leverage:

1. correct a false, stale, or conflicting active instruction;
2. link to existing authoritative guidance;
3. add narrowly missing current operational mechanics;
4. request a new normative decision only when the observed task requires it.

Use the existing file that already owns the operational procedure. Do not add
current runbook guidance to a generic, historical, or future-contract document
when a maintained operations guide exists. Never put an **Unknown** sentence in
a patch preview; keep it in the gap report until authority or a user decision
exists.

When no maintained operational guide exists, use
`docs/templates/application-runbook.md` only to structure a proposed
consumer-owned guide. The template supplies headings, not commands or authority:
omit unsupported instructions from the patch and retain them as unknowns.

Prefer a correction to an existing repository-owned document over a new
framework. Do not propose generic adapters, hooks, state markers, databases, or
generated architecture unless the observed failure requires them.

### 5. Emit a machine-authenticated evidence bundle

Read `references/evidence-capsule-v2.md` completely before constructing the
capsule. Follow its exact field names, vocabularies, and hash definitions.

Do not manually copy source, patch, producer, or destination hashes into the
final answer. Build one compact JSON spec in memory and pipe it to
`scripts/emit_evidence_bundle.py`. The spec contains boundary rows, atomic
claims with unhashed source ranges, complete proposed destination images,
unknowns, and limitations. The emitter reads every pinned blob, computes every
digest, renders each patch, and writes one authenticated bundle to stdout
without creating a draft file.

```text
<non-materializing command that prints the JSON spec> |
  python3 .agents/skills/onboard-repository/scripts/emit_evidence_bundle.py \
    --repository <tested-root> \
    --revision <full-tested-revision> \
    --branch <tested-branch>
```

Run the emitter as the final tool call with an output budget large enough to
retain the complete result. Do not rerun it unless it fails. Do not reproduce
its patch or capsule bytes in the assistant message. The raw tool result is the
auditable artifact; the final answer reports its bundle digest, hunk IDs,
destinations, classifications, gate result, and exact approval instruction.

Use schema `onboarding-evidence-capsule/v2`. The emitted capsule is an
authenticated index, not authority. It contains exactly:

- `tested_repository`: absolute root, full 40-character revision, and branch;
- `producer_skill`: repository-relative skill path and file SHA-256;
- `boundary`: separate rows covering `git`, `ignored_or_managed`, `runtime`,
  and `temporary_paths`, with normalized initial/final evidence hashes and a
  `Pass`, `Fail`, or `Unknown` result;
- `claims`: one atomic, single-line proposed clause per ID, its hunk ID,
  `Authoritative`/`Observed`/`Derived` classification, and every exact source;
- `hunks`: destination, whole-file destination hashes before and after
  in-memory patch application, displayed patch hash, claim IDs, and unresolved
  unknowns;
- `limitations`: remaining audit or environment limitations.

For each source spec record the repository-relative path, inclusive start/end
lines, and role. Set `revision` only when it differs from the tested revision.
The emitter adds the pinned revision and SHA-256 of the exact LF-terminated
range. Never cite a working-tree line without a pinned revision. Split
conjunctions into atomic claim records even when they remain one
natural-language sentence.

Repeat each claim's complete causal chain inside its capsule `sources`; prose
citations elsewhere do not satisfy the capsule. For a command-controlled
effect, include the package/entry command mapping, flag-to-branch mapping,
branch ordering, and the called implementation that performs the effect.

Make each capsule claim one subject-condition-effect fact. Split sentinel
lookup, branch selection, named path, file read, subprocess call, failure
propagation, and cleanup absence into separate claims even when the patch uses
one natural-language sentence. When a claim names an exact constant, path, or
fallback, cite both its definition and its use. When a claim says a failure
bypasses later work, cite the awaited call, the callee or assertion that
rejects/throws, and the top-level handler; the callsite alone does not prove
propagation.

For a boundary row, `Pass` requires equal non-null initial and final hashes;
`Fail` requires two different hashes; use `Unknown` when either observation is
missing or cannot prove equivalence. Hash stable normalized observation output,
not terminal decoration or timestamps. The capsule must reflect Unknowns from
the prose gate rather than silently upgrading them.

When the sibling audit skill is installed, its read-only validator is:

```text
python3 .agents/skills/audit-onboarding-proposal/scripts/validate_evidence_capsule.py --transcript <raw-session.jsonl> --expected-transcript-sha256 <sha256> --repository <tested-worktree>
```

The validator can run only after the transcript exists. For new runs it
extracts the last complete machine bundle emitted before task completion and
verifies its bundle digest, pinned producer and source blobs, and whole-file
patch application. Legacy transcripts with capsules in the completed assistant
message remain readable. Do not create a local draft merely to prevalidate the
final answer.

### 6. Report the gate

End the first pass with:

- pinned revision and initial dirty state;
- operational-path table with evidence classifications;
- ranked proposal items;
- exact machine-emitted patch preview with a classification and source for each
  added or changed claim;
- the verified managed-marker replacement diff when active managed guidance is
  stale;
- one machine-emitted v2 evidence bundle whose marked patches, identifiers, and
  computed hashes cover every proposed clause;
- blockers and unsupported claims avoided;
- final Git status/diff comparison;
- pre/post ignored-state and runtime-ownership comparison where relevant,
  explicitly marking any missed or unobservable baseline **Unknown**;
- the exact patch wording that must be approved for any change.

The gate passes only when repository authority was read, the complete path table
contains every required field, every patch sentence passes clause-level
evidence review, the run stopped at suggestions, and all required no-mutation
comparisons are proven. Git cleanliness alone cannot satisfy the last gate.

Compute the no-mutation gate conjunctively. Git state, every relevant ignored
or managed path, runtime ownership, and every task-owned prohibited temporary
path must each have proven pre/post equivalence; any required **Unknown** makes
this gate fail. Do not convert an unknown into a pass because no mutating
command was observed. A discovered repository gap does not by itself fail a
methodological gate; score the five gate conditions, not repository readiness.

Before assigning scores, perform a contradiction scan:

- each resource/identifier has exactly one ledger row;
- every checked-in default and fallback-reachability qualifier is present;
- guaranteed and optional log fields are separated;
- process-wide evidence is not called instance-local;
- every write is in the stage where it occurs and cites its full causal chain;
- absence of cleanup is not promoted to runtime liveness;
- every **Unknown** is reflected in the conjunctive gate result; and
- intermediate mistakes corrected during inspection do not remain in the final
  map, patch, evidence ledger, or score.

If the final state differs from the initial state, disclose every difference
and treat the pass as failed. Do not repair or erase user-owned changes.

## Later Pass: Apply Approved Items

Apply only when the user approves the exact displayed patch wording.

1. Re-read applicable instructions and capture current Git state.
2. Recheck target-file hashes and recompute the proposal if they changed.
3. For normative product claims, require existing authority or an explicit user
   decision. For current operational mechanics, require direct observed
   evidence, preserve the evidence classification, and phrase them as current
   behavior. Keep unknowns explicit.
4. For verified managed-file drift, replace only approved managed-marker
   content and preserve consumer-owned content outside the markers.
5. Edit only the approved agent-facing documentation or knowledge files.
6. Match existing repository structure and terminology; keep the patch small.
7. Run relevant documentation checks and any repository-prescribed validation.
8. Inspect the complete diff for invented policy or unrelated changes.
9. Rerun this skill's inspection logic. It must not propose duplicate content.
10. Produce a documentation-only replay patch that can be applied to the
    baseline commit without carrying this skill or other experimental files.
11. Report changed files, validation evidence, remaining gaps, and the frozen
    prompt for a separate fresh-agent replay.

When new choices appear during application, stop and return them for approval.

## Concrete Example

Suppose a repository documents `pnpm local:e2e`, its test runner observes
`/health` and `/chat`, and the root onboarding guide points to a nonexistent
binary. A verified managed base contains newer instructions without that
binary.

The first pass follows the active root instructions, reports the unavailable
binary, verifies the managed-base checksum, and leaves Git unchanged. Its patch
preview replaces only the stale managed block and links the existing E2E
procedure. Any new cleanup rule is classified **Decision required**. It must not
claim a new chat contract or add a universal startup script. After the user
approves exact patch wording, the later pass applies it and produces a
skill-free documentation patch for a fresh replay. Success is fewer
undocumented hints and safer command ordering, not merely more documentation.
