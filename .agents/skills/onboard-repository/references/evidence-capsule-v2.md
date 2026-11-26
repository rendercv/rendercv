# Evidence Capsule v2

Use v2 for every new onboarding run. V1 remains readable only for legacy
transcripts.

V2 replaces prose-defined hunk boundary hashes with hashes of the complete
destination file before and after an in-memory patch application. The
repository-aware validator also verifies every pinned source range and the
producer-skill blob.

## Patch markers

Wrap each hunk separately. One marker may patch one existing UTF-8 text file.
Hash the exact bytes represented by `<diff bytes>`, including one final LF:

````text
<!-- ONBOARDING_PATCH:H1:BEGIN -->
```diff
<one complete unified diff for one file>
```
<!-- ONBOARDING_PATCH:H1:END -->
````

The diff must contain adjacent `--- a/<destination>` and
`+++ b/<destination>` headers plus complete numbered `@@` hunks. File
creation, deletion, rename, binary patches, multi-file patches, and
`No newline at end of file` markers are unsupported.

Generate every marked diff with
`scripts/render_patch.py` from the complete proposed destination image. Never
write the `@@` ranges or destination digests manually. The renderer reads the
pinned destination through Git, preserves consumer-owned context present in the
complete after image, and emits the exact marked patch and capsule digest
fields without writing a draft file.

## Machine bundle route

For new runs, pass a JSON spec to
`scripts/emit_evidence_bundle.py`. The spec omits all producer, source, patch,
and destination hashes. It supplies:

- `boundary`: the four normalized observation rows;
- `claims`: `id`, `hunk_id`, atomic text, classification, and source
  `path`/`start_line`/`end_line`/`role` descriptors;
- `hunks`: `id`, destination, complete UTF-8 `after_text`, and unknowns; and
- `limitations`: unresolved evidence limits.

The emitter computes the capsule and patch blocks and wraps them in:

```text
<!-- ONBOARDING_EVIDENCE_BUNDLE_V2:BEGIN sha256=<inner-bundle-sha256> -->
...
<!-- ONBOARDING_EVIDENCE_BUNDLE_V2:END -->
```

The raw tool output is the canonical evidence artifact. Do not duplicate the
bundle in the assistant answer. The transcript-aware validator authenticates
the last complete bundle emitted before task completion. This avoids
model-mediated copying of hashes while preserving legacy final-message
capsules.

Minimal input shape:

```json
{
  "boundary": [
    {
      "id": "B1",
      "kind": "git",
      "initial_evidence_sha256": "64 lowercase hexadecimal characters",
      "final_evidence_sha256": "the same digest for Pass",
      "result": "Pass",
      "notes": []
    }
  ],
  "claims": [
    {
      "id": "C1",
      "hunk_id": "H1",
      "text": "One atomic proposed clause.",
      "classification": "Authoritative",
      "sources": [
        {
          "path": "docs/source.md",
          "start_line": 10,
          "end_line": 12,
          "role": "authority"
        }
      ]
    }
  ],
  "hunks": [
    {
      "id": "H1",
      "destination": "AGENTS.md",
      "after_text": "the complete proposed UTF-8 destination, ending with LF\n",
      "unknowns": []
    }
  ],
  "limitations": []
}
```

Supply all four required boundary kinds, not only the illustrative row. Source
`revision` is optional and defaults to the tested revision. Generate
`after_text` from the complete pinned destination in memory; do not type a
partial replacement as though it were a complete file.

## Capsule shape

````json
{
  "schema": "onboarding-evidence-capsule/v2",
  "tested_repository": {
    "root": "/absolute/repository/path",
    "revision": "40 lowercase hexadecimal characters",
    "branch": "branch-name"
  },
  "producer_skill": {
    "path": ".agents/skills/onboard-repository/SKILL.md",
    "sha256": "SHA-256 of the complete pinned skill blob"
  },
  "boundary": [
    {
      "id": "B1",
      "kind": "git",
      "initial_evidence_sha256": "64 lowercase hexadecimal characters",
      "final_evidence_sha256": "the same digest for Pass",
      "result": "Pass",
      "notes": []
    },
    {
      "id": "B2",
      "kind": "ignored_or_managed",
      "initial_evidence_sha256": null,
      "final_evidence_sha256": null,
      "result": "Unknown",
      "notes": ["One concrete limitation per string."]
    },
    {
      "id": "B3",
      "kind": "runtime",
      "initial_evidence_sha256": null,
      "final_evidence_sha256": null,
      "result": "Unknown",
      "notes": ["Runtime manager state was not observable."]
    },
    {
      "id": "B4",
      "kind": "temporary_paths",
      "initial_evidence_sha256": "64 lowercase hexadecimal characters",
      "final_evidence_sha256": "the same digest for Pass",
      "result": "Pass",
      "notes": []
    }
  ],
  "claims": [
    {
      "id": "C1",
      "hunk_id": "H1",
      "text": "One trimmed atomic proposed clause on one line.",
      "classification": "Authoritative",
      "sources": [
        {
          "revision": "40 lowercase hexadecimal characters",
          "path": "repository/relative/path.md",
          "start_line": 10,
          "end_line": 12,
          "content_sha256": "SHA-256 of the exact LF-terminated range",
          "role": "authority"
        }
      ]
    }
  ],
  "hunks": [
    {
      "id": "H1",
      "destination": "AGENTS.md",
      "destination_before_sha256": "SHA-256 of the complete pinned file",
      "destination_after_sha256": "SHA-256 of the complete in-memory patched file",
      "patch_sha256": "SHA-256 of the marked diff bytes plus final LF",
      "claim_ids": ["C1"],
      "unknowns": []
    }
  ],
  "limitations": [
    "Facts that remain unproven or require semantic audit."
  ]
}
````

## Closed vocabularies

- Claim `classification`: `Authoritative`, `Observed`, or `Derived`.
- Source `role`: `authority`, `implementation`, `configuration`, `test`, or
  `boundary`.
- Boundary `kind`: `git`, `ignored_or_managed`, `runtime`, or
  `temporary_paths`. Cover every kind.
- Boundary `result`: `Pass`, `Fail`, or `Unknown`.
- IDs: uppercase ASCII letter followed by uppercase letters, digits,
  underscores, or hyphens.

Patch claims must not be `Decision required` or `Unknown`. Keep those outside
the displayed patch and list relevant gaps in `unknowns` or `limitations`.

## Hash definitions

- Source digest: exact LF-terminated bytes printed by
  `git show <revision>:<path> | sed -n '<start>,<end>p'`.
- Producer-skill digest: complete bytes returned by
  `git show <revision>:<producer-skill-path>`.
- Destination-before digest: complete bytes returned by
  `git show <revision>:<destination>`.
- Destination-after digest: complete destination bytes after applying the
  displayed unified diff in memory to the pinned destination.
- Patch digest: bytes inside its `diff` fence, plus one final LF.
- Boundary-observation digest: stable normalized output for that component.
  Exclude timestamps, spinners, color sequences, and presentation labels.

Do not hash a visually selected subsection as a destination digest. Do not
guess a destination-after digest from changed lines alone. Use a
non-materializing in-memory transformation.

For `Pass`, initial and final boundary-observation digests must both exist and
be equal. For `Fail`, both must exist and differ. Use `Unknown` whenever either
observation was missed, incomplete, or could not establish equivalence.

## Referential rules

- Every hunk has at least one claim.
- Every claim belongs to and is referenced by exactly one hunk.
- Every claim has at least one pinned source.
- Every causal claim includes its complete command-to-effect source chain.
- Hunk IDs exactly match their patch-marker IDs.
- Every repository path is relative and contains no `..` component.
- The capsule has no fields beyond those shown above.

The repository-aware validator proves transcript identity, schema and links,
source-range hashes, producer-skill hash, patch hashes, exact patch
applicability, and complete destination before/after hashes. It does not prove
that a source semantically supports a claim or that the cited source chain is
complete; an independent patch-admissibility audit still checks those facts.
