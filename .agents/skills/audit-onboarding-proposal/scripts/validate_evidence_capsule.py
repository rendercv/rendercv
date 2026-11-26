#!/usr/bin/env python3
"""Extract and structurally validate an onboarding evidence capsule.

The validator is intentionally read-only and uses only the Python standard
library. It authenticates a Codex JSONL transcript when requested, extracts the
last completed assistant message, and validates the capsule schema. For v2 it
also verifies pinned Git blobs and applies each marked patch in memory to check
whole-destination before/after digests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA_V1 = "onboarding-evidence-capsule/v1"
SCHEMA_V2 = "onboarding-evidence-capsule/v2"
CAPSULE_MARKERS = {
    SCHEMA_V1: (
        "<!-- ONBOARDING_EVIDENCE_CAPSULE_V1:BEGIN -->",
        "<!-- ONBOARDING_EVIDENCE_CAPSULE_V1:END -->",
    ),
    SCHEMA_V2: (
        "<!-- ONBOARDING_EVIDENCE_CAPSULE_V2:BEGIN -->",
        "<!-- ONBOARDING_EVIDENCE_CAPSULE_V2:END -->",
    ),
}
BUNDLE_BEGIN_RE = re.compile(
    r"<!-- ONBOARDING_EVIDENCE_BUNDLE_V2:BEGIN sha256=([0-9a-f]{64}) -->"
)
BUNDLE_END = "<!-- ONBOARDING_EVIDENCE_BUNDLE_V2:END -->"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
ID_RE = re.compile(r"^[A-Z][A-Z0-9_-]*$")
CLASSIFICATIONS = {"Authoritative", "Observed", "Derived"}
SOURCE_ROLES = {"authority", "implementation", "configuration", "test", "boundary"}
BOUNDARY_KINDS = {"git", "ignored_or_managed", "runtime", "temporary_paths"}
BOUNDARY_RESULTS = {"Pass", "Fail", "Unknown"}


class CapsuleError(ValueError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CapsuleError(message)


def require_exact_keys(value: dict[str, Any], required: set[str], context: str) -> None:
    missing = sorted(required - value.keys())
    extra = sorted(value.keys() - required)
    require(not missing, f"{context}: missing keys: {', '.join(missing)}")
    require(not extra, f"{context}: unsupported keys: {', '.join(extra)}")


def require_sha(value: Any, context: str, *, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    require(
        isinstance(value, str) and SHA256_RE.fullmatch(value) is not None,
        f"{context}: expected lowercase SHA-256",
    )


def require_relative_path(value: Any, context: str) -> None:
    require(isinstance(value, str) and value != "", f"{context}: expected path")
    candidate = PurePosixPath(value)
    require(not candidate.is_absolute(), f"{context}: path must be repository-relative")
    require(".." not in candidate.parts, f"{context}: path must not traverse parents")


def extract_capsule(message: str) -> tuple[dict[str, Any], str]:
    present = [
        (schema, begin, end)
        for schema, (begin, end) in CAPSULE_MARKERS.items()
        if begin in message or end in message
    ]
    require(
        len(present) == 1, "expected exactly one supported evidence-capsule marker pair"
    )
    marker_schema, begin, end = present[0]
    require(message.count(begin) == 1, "expected exactly one capsule begin marker")
    require(message.count(end) == 1, "expected exactly one capsule end marker")
    before, remainder = message.split(begin, 1)
    body, after = remainder.split(end, 1)
    del before, after
    body = body.strip()
    require(
        body.startswith("```json\n") and body.endswith("\n```"),
        "capsule must be one fenced json block",
    )
    raw_json = body[len("```json\n") : -len("\n```")]
    try:
        capsule = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise CapsuleError(f"capsule JSON is invalid: {exc}") from exc
    require(isinstance(capsule, dict), "capsule root must be an object")
    require(
        capsule.get("schema") == marker_schema,
        f"capsule marker requires schema {marker_schema}",
    )
    return capsule, sha256_bytes(raw_json.encode("utf-8"))


def extract_machine_bundle(output: str) -> tuple[str, str]:
    matches = list(BUNDLE_BEGIN_RE.finditer(output))
    require(len(matches) == 1, "machine bundle must contain exactly one begin marker")
    require(
        output.count(BUNDLE_END) == 1,
        "machine bundle must contain exactly one end marker",
    )
    match = matches[0]
    remainder = output[match.end() :]
    require(
        remainder.startswith("\n"), "machine bundle content must start after one LF"
    )
    end_boundary = "\n" + BUNDLE_END
    require(end_boundary in remainder, "machine bundle end boundary is malformed")
    inner, after = remainder[1:].split(end_boundary, 1)
    inner += "\n"
    del after
    expected_sha = match.group(1)
    require(
        sha256_bytes(inner.encode("utf-8")) == expected_sha,
        "machine bundle SHA-256 does not match its exact inner bytes",
    )
    return inner, expected_sha


def extract_patch(message: str, hunk_id: str) -> str:
    begin = f"<!-- ONBOARDING_PATCH:{hunk_id}:BEGIN -->"
    end = f"<!-- ONBOARDING_PATCH:{hunk_id}:END -->"
    require(
        message.count(begin) == 1, f"{hunk_id}: expected exactly one patch begin marker"
    )
    require(
        message.count(end) == 1, f"{hunk_id}: expected exactly one patch end marker"
    )
    body = message.split(begin, 1)[1].split(end, 1)[0].strip()
    require(
        body.startswith("```diff\n") and body.endswith("\n```"),
        f"{hunk_id}: patch must be one fenced diff block",
    )
    patch = body[len("```diff\n") : -len("\n```")]
    return patch + "\n"


def git_blob(repository: Path, revision: str, path: str, context: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repository), "show", f"{revision}:{path}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    require(
        result.returncode == 0,
        f"{context}: git show failed: {result.stderr.decode('utf-8', errors='replace').strip()}",
    )
    return result.stdout


def source_range(blob: bytes, start_line: int, end_line: int, context: str) -> bytes:
    lines = blob.splitlines(keepends=True)
    require(end_line <= len(lines), f"{context}: source range exceeds file length")
    return b"".join(lines[start_line - 1 : end_line])


def diff_path(line: str, prefix: str, context: str) -> str:
    require(line.startswith(prefix), f"{context}: invalid diff path header")
    value = line[len(prefix) :].rstrip("\n").split("\t", 1)[0]
    require(
        value not in {"/dev/null", ""},
        f"{context}: file creation/deletion is unsupported",
    )
    if value.startswith(("a/", "b/")):
        value = value[2:]
    require_relative_path(value, context)
    return value


def apply_unified_diff(
    original: bytes, patch: str, destination: str, context: str
) -> bytes:
    try:
        original_text = original.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CapsuleError(f"{context}: destination is not UTF-8 text") from exc
    lines = patch.splitlines(keepends=True)
    old_headers = [index for index, line in enumerate(lines) if line.startswith("--- ")]
    new_headers = [index for index, line in enumerate(lines) if line.startswith("+++ ")]
    require(
        len(old_headers) == 1 and len(new_headers) == 1,
        f"{context}: patch must contain exactly one old/new file header",
    )
    old_header = old_headers[0]
    new_header = new_headers[0]
    require(
        new_header == old_header + 1,
        f"{context}: old/new file headers must be adjacent",
    )
    require(
        diff_path(lines[old_header], "--- ", f"{context}.old_path") == destination,
        f"{context}: old patch path does not match destination",
    )
    require(
        diff_path(lines[new_header], "+++ ", f"{context}.new_path") == destination,
        f"{context}: new patch path does not match destination",
    )

    original_lines = original_text.splitlines(keepends=True)
    output: list[str] = []
    old_cursor = 0
    index = new_header + 1
    hunk_count = 0
    hunk_re = re.compile(
        r"^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))? "
        r"\+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@(?:.*)\n?$"
    )
    while index < len(lines):
        if lines[index].startswith(("diff --git ", "--- ", "+++ ")):
            raise CapsuleError(f"{context}: multi-file patches are unsupported")
        match = hunk_re.match(lines[index])
        require(match is not None, f"{context}: unexpected diff line outside a hunk")
        hunk_count += 1
        old_start = int(match.group("old_start"))
        old_expected = int(match.group("old_count") or "1")
        new_expected = int(match.group("new_count") or "1")
        target = 0 if old_start == 0 else old_start - 1
        require(target >= old_cursor, f"{context}: overlapping or out-of-order hunks")
        require(
            target <= len(original_lines), f"{context}: hunk starts beyond destination"
        )
        output.extend(original_lines[old_cursor:target])
        old_cursor = target
        old_seen = 0
        new_seen = 0
        index += 1
        while index < len(lines) and not lines[index].startswith("@@ "):
            line = lines[index]
            require(
                not line.startswith("diff --git "),
                f"{context}: multi-file patches are unsupported",
            )
            require(
                line != "\\ No newline at end of file\n",
                f"{context}: no-newline markers are unsupported",
            )
            require(
                line and line[0] in {" ", "+", "-"},
                f"{context}: invalid unified-diff body line",
            )
            content = line[1:]
            if line[0] in {" ", "-"}:
                require(
                    old_cursor < len(original_lines),
                    f"{context}: patch consumes beyond destination",
                )
                require(
                    original_lines[old_cursor] == content,
                    f"{context}: patch preimage mismatch at destination line {old_cursor + 1}",
                )
                old_cursor += 1
                old_seen += 1
            if line[0] in {" ", "+"}:
                output.append(content)
                new_seen += 1
            index += 1
        require(
            old_seen == old_expected,
            f"{context}: hunk old-line count is {old_seen}, expected {old_expected}",
        )
        require(
            new_seen == new_expected,
            f"{context}: hunk new-line count is {new_seen}, expected {new_expected}",
        )
    require(hunk_count > 0, f"{context}: patch contains no hunks")
    output.extend(original_lines[old_cursor:])
    return "".join(output).encode("utf-8")


def validate_capsule(
    capsule: dict[str, Any],
    message: str,
    repository: Path | None = None,
) -> dict[str, Any]:
    require_exact_keys(
        capsule,
        {
            "schema",
            "tested_repository",
            "producer_skill",
            "boundary",
            "claims",
            "hunks",
            "limitations",
        },
        "capsule",
    )
    schema = capsule["schema"]
    require(schema in CAPSULE_MARKERS, f"capsule.schema is unsupported: {schema}")

    tested = capsule["tested_repository"]
    require(isinstance(tested, dict), "tested_repository must be an object")
    require_exact_keys(tested, {"root", "revision", "branch"}, "tested_repository")
    require(
        isinstance(tested["root"], str) and tested["root"].startswith("/"),
        "tested_repository.root must be absolute",
    )
    require(
        isinstance(tested["revision"], str)
        and REVISION_RE.fullmatch(tested["revision"]) is not None,
        "tested_repository.revision must be a lowercase 40-character Git revision",
    )
    require(
        isinstance(tested["branch"], str) and tested["branch"] != "",
        "tested_repository.branch must be non-empty",
    )
    if schema == SCHEMA_V2:
        repository = repository or Path(tested["root"])
        require(
            repository.is_dir(), "v2 validation requires an existing tested repository"
        )
        require(
            repository.resolve() == Path(tested["root"]).resolve(),
            "--repository must match tested_repository.root",
        )
        root_result = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "--show-toplevel"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        require(root_result.returncode == 0, "tested repository is not a Git worktree")
        require(
            Path(root_result.stdout.strip()).resolve() == repository.resolve(),
            "repository path must be the tested Git worktree root",
        )

    producer = capsule["producer_skill"]
    require(isinstance(producer, dict), "producer_skill must be an object")
    require_exact_keys(producer, {"path", "sha256"}, "producer_skill")
    require_relative_path(producer["path"], "producer_skill.path")
    require_sha(producer["sha256"], "producer_skill.sha256")
    if schema == SCHEMA_V2:
        producer_blob = git_blob(
            repository,
            tested["revision"],
            producer["path"],
            "producer_skill",
        )
        require(
            sha256_bytes(producer_blob) == producer["sha256"],
            "producer_skill.sha256 does not match the pinned repository blob",
        )

    boundary = capsule["boundary"]
    require(
        isinstance(boundary, list) and boundary, "boundary must be a non-empty array"
    )
    boundary_ids: set[str] = set()
    covered_kinds: set[str] = set()
    for index, entry in enumerate(boundary):
        context = f"boundary[{index}]"
        require(isinstance(entry, dict), f"{context}: expected object")
        require_exact_keys(
            entry,
            {
                "id",
                "kind",
                "initial_evidence_sha256",
                "final_evidence_sha256",
                "result",
                "notes",
            },
            context,
        )
        require(
            isinstance(entry["id"], str) and ID_RE.fullmatch(entry["id"]) is not None,
            f"{context}.id: invalid identifier",
        )
        require(entry["id"] not in boundary_ids, f"{context}.id: duplicate")
        boundary_ids.add(entry["id"])
        require(entry["kind"] in BOUNDARY_KINDS, f"{context}.kind: unsupported value")
        covered_kinds.add(entry["kind"])
        require(
            entry["result"] in BOUNDARY_RESULTS, f"{context}.result: unsupported value"
        )
        require_sha(
            entry["initial_evidence_sha256"],
            f"{context}.initial_evidence_sha256",
            nullable=True,
        )
        require_sha(
            entry["final_evidence_sha256"],
            f"{context}.final_evidence_sha256",
            nullable=True,
        )
        require(
            isinstance(entry["notes"], list)
            and all(isinstance(item, str) for item in entry["notes"]),
            f"{context}.notes: expected string array",
        )
        if entry["result"] == "Pass":
            require(
                entry["initial_evidence_sha256"] is not None,
                f"{context}: Pass requires initial evidence",
            )
            require(
                entry["initial_evidence_sha256"] == entry["final_evidence_sha256"],
                f"{context}: Pass requires equal initial/final evidence hashes",
            )
        if entry["result"] == "Fail":
            require(
                entry["initial_evidence_sha256"] is not None
                and entry["final_evidence_sha256"] is not None,
                f"{context}: Fail requires both evidence hashes",
            )
            require(
                entry["initial_evidence_sha256"] != entry["final_evidence_sha256"],
                f"{context}: Fail requires different initial/final evidence hashes",
            )
    require(
        covered_kinds == BOUNDARY_KINDS,
        "boundary must cover git, ignored_or_managed, runtime, and temporary_paths",
    )

    claims = capsule["claims"]
    require(isinstance(claims, list) and claims, "claims must be a non-empty array")
    claim_by_id: dict[str, dict[str, Any]] = {}
    for index, claim in enumerate(claims):
        context = f"claims[{index}]"
        require(isinstance(claim, dict), f"{context}: expected object")
        require_exact_keys(
            claim, {"id", "hunk_id", "text", "classification", "sources"}, context
        )
        require(
            isinstance(claim["id"], str) and ID_RE.fullmatch(claim["id"]) is not None,
            f"{context}.id: invalid identifier",
        )
        require(claim["id"] not in claim_by_id, f"{context}.id: duplicate")
        claim_by_id[claim["id"]] = claim
        require(
            isinstance(claim["hunk_id"], str)
            and ID_RE.fullmatch(claim["hunk_id"]) is not None,
            f"{context}.hunk_id: invalid identifier",
        )
        require(
            isinstance(claim["text"], str)
            and claim["text"].strip() == claim["text"]
            and claim["text"] != "",
            f"{context}.text: expected trimmed atomic clause",
        )
        require(
            "\n" not in claim["text"],
            f"{context}.text: atomic clauses must be one line",
        )
        require(
            claim["classification"] in CLASSIFICATIONS,
            f"{context}.classification: patch claims must be Authoritative, Observed, or Derived",
        )
        sources = claim["sources"]
        require(
            isinstance(sources, list) and sources,
            f"{context}.sources: expected non-empty array",
        )
        for source_index, source in enumerate(sources):
            source_context = f"{context}.sources[{source_index}]"
            require(isinstance(source, dict), f"{source_context}: expected object")
            require_exact_keys(
                source,
                {
                    "revision",
                    "path",
                    "start_line",
                    "end_line",
                    "content_sha256",
                    "role",
                },
                source_context,
            )
            require(
                isinstance(source["revision"], str)
                and REVISION_RE.fullmatch(source["revision"]) is not None,
                f"{source_context}.revision: invalid Git revision",
            )
            require_relative_path(source["path"], f"{source_context}.path")
            require(
                isinstance(source["start_line"], int) and source["start_line"] > 0,
                f"{source_context}.start_line: expected positive integer",
            )
            require(
                isinstance(source["end_line"], int)
                and source["end_line"] >= source["start_line"],
                f"{source_context}.end_line: expected integer at or after start_line",
            )
            require_sha(source["content_sha256"], f"{source_context}.content_sha256")
            require(
                source["role"] in SOURCE_ROLES,
                f"{source_context}.role: unsupported value",
            )
            if schema == SCHEMA_V2:
                blob = git_blob(
                    repository,
                    source["revision"],
                    source["path"],
                    source_context,
                )
                actual_source = source_range(
                    blob,
                    source["start_line"],
                    source["end_line"],
                    source_context,
                )
                require(
                    sha256_bytes(actual_source) == source["content_sha256"],
                    f"{source_context}.content_sha256 does not match pinned source bytes",
                )

    hunks = capsule["hunks"]
    require(isinstance(hunks, list) and hunks, "hunks must be a non-empty array")
    hunk_ids: set[str] = set()
    referenced_claims: list[str] = []
    patch_hashes: dict[str, str] = {}
    for index, hunk in enumerate(hunks):
        context = f"hunks[{index}]"
        require(isinstance(hunk, dict), f"{context}: expected object")
        hunk_keys = (
            {
                "id",
                "destination",
                "boundary",
                "before_sha256",
                "after_sha256",
                "patch_sha256",
                "claim_ids",
                "unknowns",
            }
            if schema == SCHEMA_V1
            else {
                "id",
                "destination",
                "destination_before_sha256",
                "destination_after_sha256",
                "patch_sha256",
                "claim_ids",
                "unknowns",
            }
        )
        require_exact_keys(hunk, hunk_keys, context)
        hunk_id = hunk["id"]
        require(
            isinstance(hunk_id, str) and ID_RE.fullmatch(hunk_id) is not None,
            f"{context}.id: invalid identifier",
        )
        require(hunk_id not in hunk_ids, f"{context}.id: duplicate")
        hunk_ids.add(hunk_id)
        require_relative_path(hunk["destination"], f"{context}.destination")
        if schema == SCHEMA_V1:
            require(
                isinstance(hunk["boundary"], str)
                and hunk["boundary"].strip() == hunk["boundary"]
                and hunk["boundary"] != "",
                f"{context}.boundary: expected trimmed description",
            )
            digest_fields = ("before_sha256", "after_sha256", "patch_sha256")
        else:
            digest_fields = (
                "destination_before_sha256",
                "destination_after_sha256",
                "patch_sha256",
            )
        for field in digest_fields:
            require_sha(hunk[field], f"{context}.{field}")
        require(
            isinstance(hunk["claim_ids"], list) and hunk["claim_ids"],
            f"{context}.claim_ids: expected non-empty array",
        )
        require(
            len(hunk["claim_ids"]) == len(set(hunk["claim_ids"])),
            f"{context}.claim_ids: duplicates are not allowed",
        )
        for claim_id in hunk["claim_ids"]:
            require(
                claim_id in claim_by_id,
                f"{context}.claim_ids: unknown claim {claim_id}",
            )
            require(
                claim_by_id[claim_id]["hunk_id"] == hunk_id,
                f"{context}.claim_ids: {claim_id} belongs to another hunk",
            )
            referenced_claims.append(claim_id)
        require(
            isinstance(hunk["unknowns"], list)
            and all(isinstance(item, str) for item in hunk["unknowns"]),
            f"{context}.unknowns: expected string array",
        )
        patch = extract_patch(message, hunk_id)
        actual_patch_sha = sha256_bytes(patch.encode("utf-8"))
        require(
            actual_patch_sha == hunk["patch_sha256"],
            f"{context}.patch_sha256: displayed patch hashes to {actual_patch_sha}",
        )
        if schema == SCHEMA_V2:
            destination_before = git_blob(
                repository,
                tested["revision"],
                hunk["destination"],
                context,
            )
            require(
                sha256_bytes(destination_before) == hunk["destination_before_sha256"],
                f"{context}.destination_before_sha256 does not match pinned destination",
            )
            destination_after = apply_unified_diff(
                destination_before,
                patch,
                hunk["destination"],
                context,
            )
            require(
                sha256_bytes(destination_after) == hunk["destination_after_sha256"],
                f"{context}.destination_after_sha256 does not match applied patch result",
            )
        patch_hashes[hunk_id] = actual_patch_sha

    require(
        set(referenced_claims) == set(claim_by_id),
        "every claim must be referenced by exactly one hunk",
    )
    require(
        len(referenced_claims) == len(set(referenced_claims)),
        "a claim may not be referenced by multiple hunks",
    )
    require(
        {claim["hunk_id"] for claim in claims} == hunk_ids,
        "claim hunk identifiers must exactly match displayed hunks",
    )

    limitations = capsule["limitations"]
    require(
        isinstance(limitations, list)
        and all(isinstance(item, str) for item in limitations),
        "limitations must be a string array",
    )

    return {
        "schema": schema,
        "tested_revision": tested["revision"],
        "boundary_count": len(boundary),
        "claim_count": len(claims),
        "hunk_count": len(hunks),
        "patch_sha256": patch_hashes,
    }


def transcript_message(
    path: Path,
    expected_sha256: str | None,
) -> tuple[str, str, str | None, str]:
    raw = path.read_bytes()
    actual_sha = sha256_bytes(raw)
    if expected_sha256 is not None:
        require_sha(expected_sha256, "expected transcript SHA-256")
        require(
            actual_sha == expected_sha256,
            f"transcript SHA-256 mismatch: expected {expected_sha256}, got {actual_sha}",
        )
    completed: list[tuple[int, str]] = []
    assistant_messages: list[str] = []
    machine_outputs: list[tuple[int, str]] = []
    for line_number, line in enumerate(raw.splitlines(), 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CapsuleError(
                f"transcript line {line_number} is invalid JSON: {exc}"
            ) from exc
        if (
            event.get("type") == "event_msg"
            and event.get("payload", {}).get("type") == "task_complete"
        ):
            message = event["payload"].get("last_agent_message")
            if isinstance(message, str):
                completed.append((line_number, message))
        payload = event.get("payload", {})
        if (
            event.get("type") == "response_item"
            and payload.get("type") == "message"
            and payload.get("role") == "assistant"
        ):
            text = "".join(
                item.get("text", "")
                for item in payload.get("content", [])
                if isinstance(item, dict)
            )
            if text:
                assistant_messages.append(text)
        if (
            event.get("type") == "response_item"
            and payload.get("type") == "custom_tool_call_output"
        ):
            output = payload.get("output")
            if isinstance(output, str):
                output_text = output
            elif isinstance(output, list):
                output_text = "".join(
                    item.get("text", "")
                    for item in output
                    if isinstance(item, dict)
                    and item.get("type") in {"input_text", "output_text"}
                )
            else:
                output_text = ""
            if BUNDLE_BEGIN_RE.search(output_text) or BUNDLE_END in output_text:
                machine_outputs.append((line_number, output_text))
    if completed:
        last_complete_line, completed_message = completed[-1]
        eligible_bundles = [
            output
            for line_number, output in machine_outputs
            if line_number < last_complete_line
        ]
        if eligible_bundles:
            message, bundle_sha = extract_machine_bundle(eligible_bundles[-1])
            return message, actual_sha, bundle_sha, "machine_tool_output"
        return completed_message, actual_sha, None, "completed_assistant_message"
    require(assistant_messages, "transcript contains no completed assistant message")
    return assistant_messages[-1], actual_sha, None, "incomplete_assistant_fallback"


def self_test() -> None:
    zeros = "0" * 64
    ones = "1" * 64
    revision = "a" * 40
    patch = "--- a/AGENTS.md\n+++ b/AGENTS.md\n@@\n-old\n+new\n"
    patch_sha = sha256_bytes(patch.encode())
    capsule = {
        "schema": SCHEMA_V1,
        "tested_repository": {
            "root": "/tmp/repo",
            "revision": revision,
            "branch": "test",
        },
        "producer_skill": {
            "path": ".agents/skills/onboard-repository/SKILL.md",
            "sha256": zeros,
        },
        "boundary": [
            {
                "id": "B1",
                "kind": "git",
                "initial_evidence_sha256": zeros,
                "final_evidence_sha256": zeros,
                "result": "Pass",
                "notes": [],
            },
            {
                "id": "B2",
                "kind": "ignored_or_managed",
                "initial_evidence_sha256": ones,
                "final_evidence_sha256": ones,
                "result": "Pass",
                "notes": [],
            },
            {
                "id": "B3",
                "kind": "runtime",
                "initial_evidence_sha256": None,
                "final_evidence_sha256": None,
                "result": "Unknown",
                "notes": ["unobservable"],
            },
            {
                "id": "B4",
                "kind": "temporary_paths",
                "initial_evidence_sha256": zeros,
                "final_evidence_sha256": zeros,
                "result": "Pass",
                "notes": [],
            },
        ],
        "claims": [
            {
                "id": "C1",
                "hunk_id": "H1",
                "text": "New guidance.",
                "classification": "Authoritative",
                "sources": [
                    {
                        "revision": revision,
                        "path": "docs/WORKFLOW.md",
                        "start_line": 1,
                        "end_line": 1,
                        "content_sha256": zeros,
                        "role": "authority",
                    }
                ],
            }
        ],
        "hunks": [
            {
                "id": "H1",
                "destination": "AGENTS.md",
                "boundary": "managed marker",
                "before_sha256": zeros,
                "after_sha256": ones,
                "patch_sha256": patch_sha,
                "claim_ids": ["C1"],
                "unknowns": [],
            }
        ],
        "limitations": ["runtime unobservable"],
    }
    raw_json = json.dumps(capsule, indent=2, sort_keys=True)
    capsule_begin, capsule_end = CAPSULE_MARKERS[SCHEMA_V1]
    message = (
        "<!-- ONBOARDING_PATCH:H1:BEGIN -->\n```diff\n"
        + patch
        + "```\n<!-- ONBOARDING_PATCH:H1:END -->\n"
        + capsule_begin
        + "\n```json\n"
        + raw_json
        + "\n```\n"
        + capsule_end
    )
    extracted, _ = extract_capsule(message)
    result = validate_capsule(extracted, message)
    require(result["hunk_count"] == 1, "self-test valid fixture failed")
    extracted["hunks"][0]["patch_sha256"] = zeros
    try:
        validate_capsule(extracted, message)
    except CapsuleError:
        pass
    else:
        raise CapsuleError("self-test invalid fixture was accepted")

    bundle_inner = message + "\n"
    bundle_sha = sha256_bytes(bundle_inner.encode("utf-8"))
    bundle_output = (
        "tool wrapper\n"
        f"<!-- ONBOARDING_EVIDENCE_BUNDLE_V2:BEGIN sha256={bundle_sha} -->\n"
        + bundle_inner
        + BUNDLE_END
        + "\n"
    )
    extracted_bundle, extracted_bundle_sha = extract_machine_bundle(bundle_output)
    require(extracted_bundle == bundle_inner, "machine-bundle extraction changed bytes")
    require(
        extracted_bundle_sha == bundle_sha, "machine-bundle extraction changed digest"
    )

    v2_original = b"one\ntwo\nthree\n"
    v2_patch = (
        "diff --git a/docs/test.md b/docs/test.md\n"
        "index 0000000..1111111 100644\n"
        "--- a/docs/test.md\n"
        "+++ b/docs/test.md\n"
        "@@ -1,3 +1,3 @@\n"
        " one\n"
        "-two\n"
        "+changed\n"
        " three\n"
    )
    v2_after = apply_unified_diff(v2_original, v2_patch, "docs/test.md", "self-test-v2")
    require(
        v2_after == b"one\nchanged\nthree\n", "v2 in-memory patch application failed"
    )
    try:
        apply_unified_diff(
            v2_original.replace(b"two", b"different"),
            v2_patch,
            "docs/test.md",
            "self-test-v2",
        )
    except CapsuleError:
        pass
    else:
        raise CapsuleError("v2 preimage mismatch was accepted")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcript", type=Path)
    parser.add_argument("--expected-transcript-sha256")
    parser.add_argument("--repository", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
            print(json.dumps({"valid": True, "self_test": "passed"}, sort_keys=True))
            return 0
        if args.transcript is not None:
            message, transcript_sha, bundle_sha, evidence_source = transcript_message(
                args.transcript,
                args.expected_transcript_sha256,
            )
        else:
            require(
                args.expected_transcript_sha256 is None,
                "--expected-transcript-sha256 requires --transcript",
            )
            stdin_message = sys.stdin.read()
            transcript_sha = None
            if BUNDLE_BEGIN_RE.search(stdin_message) or BUNDLE_END in stdin_message:
                message, bundle_sha = extract_machine_bundle(stdin_message)
                evidence_source = "stdin_machine_bundle"
            else:
                message = stdin_message
                bundle_sha = None
                evidence_source = "stdin"
        capsule, capsule_sha = extract_capsule(message)
        result = validate_capsule(capsule, message, args.repository)
        result.update({"valid": True, "capsule_sha256": capsule_sha})
        if transcript_sha is not None:
            result["transcript_sha256"] = transcript_sha
        result["evidence_source"] = evidence_source
        if bundle_sha is not None:
            result["bundle_sha256"] = bundle_sha
        print(json.dumps(result, sort_keys=True))
        return 0
    except (CapsuleError, OSError) as exc:
        print(
            json.dumps({"valid": False, "error": str(exc)}, sort_keys=True),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
