#!/usr/bin/env python3
"""Emit one authenticated evidence bundle without materializing a draft file."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Callable

from render_patch import RenderError, render_patch, sha256_bytes


SCHEMA = "onboarding-evidence-capsule/v2"
BUNDLE_END = "<!-- ONBOARDING_EVIDENCE_BUNDLE_V2:END -->"
CAPSULE_BEGIN = "<!-- ONBOARDING_EVIDENCE_CAPSULE_V2:BEGIN -->"
CAPSULE_END = "<!-- ONBOARDING_EVIDENCE_CAPSULE_V2:END -->"
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
ID_RE = re.compile(r"^[A-Z][A-Z0-9_-]*$")
CLASSIFICATIONS = {"Authoritative", "Observed", "Derived"}
SOURCE_ROLES = {"authority", "implementation", "configuration", "test", "boundary"}
BOUNDARY_KINDS = {"git", "ignored_or_managed", "runtime", "temporary_paths"}
BOUNDARY_RESULTS = {"Pass", "Fail", "Unknown"}


class BundleError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BundleError(message)


def require_exact_keys(value: dict[str, Any], expected: set[str], context: str) -> None:
    missing = sorted(expected - value.keys())
    extra = sorted(value.keys() - expected)
    require(not missing, f"{context}: missing keys: {', '.join(missing)}")
    require(not extra, f"{context}: unsupported keys: {', '.join(extra)}")


def require_sha(value: Any, context: str, *, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    require(
        isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
        f"{context}: expected lowercase SHA-256",
    )


def require_relative_path(value: Any, context: str) -> None:
    require(isinstance(value, str) and value != "", f"{context}: expected path")
    candidate = PurePosixPath(value)
    require(not candidate.is_absolute(), f"{context}: path must be repository-relative")
    require(".." not in candidate.parts, f"{context}: path must not traverse parents")


def git_blob_reader(repository: Path) -> Callable[[str, str], bytes]:
    def read_blob(revision: str, path: str) -> bytes:
        result = subprocess.run(
            ["git", "-C", str(repository), "show", f"{revision}:{path}"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        require(
            result.returncode == 0,
            f"git show {revision}:{path} failed: "
            + result.stderr.decode("utf-8", errors="replace").strip(),
        )
        return result.stdout

    return read_blob


def exact_source_bytes(
    blob: bytes, start_line: int, end_line: int, context: str
) -> bytes:
    lines = blob.splitlines(keepends=True)
    require(start_line > 0, f"{context}.start_line must be positive")
    require(end_line >= start_line, f"{context}.end_line precedes start_line")
    require(end_line <= len(lines), f"{context}: source range exceeds file length")
    return b"".join(lines[start_line - 1 : end_line])


def validate_boundary(boundary: Any) -> list[dict[str, Any]]:
    require(
        isinstance(boundary, list) and boundary, "boundary must be a non-empty array"
    )
    kinds: set[str] = set()
    ids: set[str] = set()
    for index, row in enumerate(boundary):
        context = f"boundary[{index}]"
        require(isinstance(row, dict), f"{context}: expected object")
        require_exact_keys(
            row,
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
            isinstance(row["id"], str) and ID_RE.fullmatch(row["id"]) is not None,
            f"{context}.id is invalid",
        )
        require(row["id"] not in ids, f"{context}.id is duplicated")
        ids.add(row["id"])
        require(row["kind"] in BOUNDARY_KINDS, f"{context}.kind is unsupported")
        kinds.add(row["kind"])
        require(row["result"] in BOUNDARY_RESULTS, f"{context}.result is unsupported")
        require_sha(
            row["initial_evidence_sha256"],
            f"{context}.initial_evidence_sha256",
            nullable=True,
        )
        require_sha(
            row["final_evidence_sha256"],
            f"{context}.final_evidence_sha256",
            nullable=True,
        )
        require(
            isinstance(row["notes"], list)
            and all(isinstance(note, str) for note in row["notes"]),
            f"{context}.notes must be a string array",
        )
        if row["result"] == "Pass":
            require(
                row["initial_evidence_sha256"] is not None,
                f"{context}: Pass requires initial evidence",
            )
            require(
                row["initial_evidence_sha256"] == row["final_evidence_sha256"],
                f"{context}: Pass requires equal evidence hashes",
            )
        if row["result"] == "Fail":
            require(
                row["initial_evidence_sha256"] is not None
                and row["final_evidence_sha256"] is not None,
                f"{context}: Fail requires both evidence hashes",
            )
            require(
                row["initial_evidence_sha256"] != row["final_evidence_sha256"],
                f"{context}: Fail requires different evidence hashes",
            )
    require(kinds == BOUNDARY_KINDS, "boundary must cover all four required kinds")
    return boundary


def build_bundle(
    *,
    spec: dict[str, Any],
    root: str,
    revision: str,
    branch: str,
    producer_skill_path: str,
    read_blob: Callable[[str, str], bytes],
) -> tuple[str, str]:
    require_exact_keys(spec, {"boundary", "claims", "hunks", "limitations"}, "spec")
    require(root.startswith("/"), "repository root must be absolute")
    require(
        REVISION_RE.fullmatch(revision) is not None,
        "revision must be 40 lowercase hex characters",
    )
    require(branch != "", "branch must not be empty")
    require_relative_path(producer_skill_path, "producer_skill_path")
    producer_blob = read_blob(revision, producer_skill_path)

    claims_input = spec["claims"]
    require(
        isinstance(claims_input, list) and claims_input,
        "claims must be a non-empty array",
    )
    claims: list[dict[str, Any]] = []
    claim_ids: set[str] = set()
    claims_by_hunk: dict[str, list[str]] = {}
    for index, claim in enumerate(claims_input):
        context = f"claims[{index}]"
        require(isinstance(claim, dict), f"{context}: expected object")
        require_exact_keys(
            claim, {"id", "hunk_id", "text", "classification", "sources"}, context
        )
        claim_id = claim["id"]
        hunk_id = claim["hunk_id"]
        require(
            isinstance(claim_id, str) and ID_RE.fullmatch(claim_id) is not None,
            f"{context}.id is invalid",
        )
        require(claim_id not in claim_ids, f"{context}.id is duplicated")
        claim_ids.add(claim_id)
        require(
            isinstance(hunk_id, str) and ID_RE.fullmatch(hunk_id) is not None,
            f"{context}.hunk_id is invalid",
        )
        require(
            isinstance(claim["text"], str)
            and claim["text"].strip() == claim["text"]
            and claim["text"] != ""
            and "\n" not in claim["text"],
            f"{context}.text must be one trimmed non-empty line",
        )
        require(
            claim["classification"] in CLASSIFICATIONS,
            f"{context}.classification is unsupported",
        )
        sources_input = claim["sources"]
        require(
            isinstance(sources_input, list) and sources_input,
            f"{context}.sources must be a non-empty array",
        )
        sources: list[dict[str, Any]] = []
        for source_index, source in enumerate(sources_input):
            source_context = f"{context}.sources[{source_index}]"
            require(isinstance(source, dict), f"{source_context}: expected object")
            allowed = {"path", "start_line", "end_line", "role", "revision"}
            require(set(source) <= allowed, f"{source_context}: unsupported keys")
            require(
                {"path", "start_line", "end_line", "role"} <= set(source),
                f"{source_context}: missing required keys",
            )
            source_revision = source.get("revision", revision)
            require(
                isinstance(source_revision, str)
                and REVISION_RE.fullmatch(source_revision) is not None,
                f"{source_context}.revision is invalid",
            )
            require_relative_path(source["path"], f"{source_context}.path")
            require(
                isinstance(source["start_line"], int)
                and isinstance(source["end_line"], int),
                f"{source_context}: line bounds must be integers",
            )
            require(
                source["role"] in SOURCE_ROLES, f"{source_context}.role is unsupported"
            )
            source_bytes = exact_source_bytes(
                read_blob(source_revision, source["path"]),
                source["start_line"],
                source["end_line"],
                source_context,
            )
            sources.append(
                {
                    "revision": source_revision,
                    "path": source["path"],
                    "start_line": source["start_line"],
                    "end_line": source["end_line"],
                    "content_sha256": sha256_bytes(source_bytes),
                    "role": source["role"],
                }
            )
        claims.append(
            {
                "id": claim_id,
                "hunk_id": hunk_id,
                "text": claim["text"],
                "classification": claim["classification"],
                "sources": sources,
            }
        )
        claims_by_hunk.setdefault(hunk_id, []).append(claim_id)

    hunks_input = spec["hunks"]
    require(
        isinstance(hunks_input, list) and hunks_input, "hunks must be a non-empty array"
    )
    hunks: list[dict[str, Any]] = []
    patch_blocks: list[str] = []
    hunk_ids: set[str] = set()
    for index, hunk in enumerate(hunks_input):
        context = f"hunks[{index}]"
        require(isinstance(hunk, dict), f"{context}: expected object")
        require_exact_keys(
            hunk, {"id", "destination", "after_text", "unknowns"}, context
        )
        hunk_id = hunk["id"]
        require(
            isinstance(hunk_id, str) and ID_RE.fullmatch(hunk_id) is not None,
            f"{context}.id is invalid",
        )
        require(hunk_id not in hunk_ids, f"{context}.id is duplicated")
        hunk_ids.add(hunk_id)
        require_relative_path(hunk["destination"], f"{context}.destination")
        require(
            isinstance(hunk["after_text"], str),
            f"{context}.after_text must be a string",
        )
        require(
            isinstance(hunk["unknowns"], list)
            and all(isinstance(item, str) for item in hunk["unknowns"]),
            f"{context}.unknowns must be a string array",
        )
        require(hunk_id in claims_by_hunk, f"{context}: no claims reference this hunk")
        before = read_blob(revision, hunk["destination"])
        after = hunk["after_text"].encode("utf-8")
        patch = render_patch(before, after, hunk["destination"])
        patch_blocks.append(
            f"<!-- ONBOARDING_PATCH:{hunk_id}:BEGIN -->\n"
            f"```diff\n{patch}```\n"
            f"<!-- ONBOARDING_PATCH:{hunk_id}:END -->"
        )
        hunks.append(
            {
                "id": hunk_id,
                "destination": hunk["destination"],
                "destination_before_sha256": sha256_bytes(before),
                "destination_after_sha256": sha256_bytes(after),
                "patch_sha256": sha256_bytes(patch.encode("utf-8")),
                "claim_ids": claims_by_hunk[hunk_id],
                "unknowns": hunk["unknowns"],
            }
        )
    require(
        set(claims_by_hunk) == hunk_ids,
        "every claim hunk_id must identify an emitted hunk",
    )
    limitations = spec["limitations"]
    require(
        isinstance(limitations, list)
        and all(isinstance(item, str) for item in limitations),
        "limitations must be a string array",
    )

    capsule = {
        "schema": SCHEMA,
        "tested_repository": {"root": root, "revision": revision, "branch": branch},
        "producer_skill": {
            "path": producer_skill_path,
            "sha256": sha256_bytes(producer_blob),
        },
        "boundary": validate_boundary(spec["boundary"]),
        "claims": claims,
        "hunks": hunks,
        "limitations": limitations,
    }
    capsule_json = json.dumps(capsule, ensure_ascii=False, indent=2)
    inner = (
        "\n\n".join(patch_blocks)
        + "\n\n"
        + CAPSULE_BEGIN
        + "\n```json\n"
        + capsule_json
        + "\n```\n"
        + CAPSULE_END
        + "\n"
    )
    bundle_sha = sha256_bytes(inner.encode("utf-8"))
    bundle = (
        f"<!-- ONBOARDING_EVIDENCE_BUNDLE_V2:BEGIN sha256={bundle_sha} -->\n"
        + inner
        + BUNDLE_END
        + "\n"
    )
    return bundle, bundle_sha


def self_test() -> None:
    revision = "a" * 40
    zeros = "0" * 64
    blobs = {
        (revision, ".agents/skills/onboard-repository/SKILL.md"): b"skill\n",
        (revision, "docs/source.md"): b"authority\nsecond\n",
        (revision, "docs/test.md"): b"old\n",
    }

    def read_blob(test_revision: str, path: str) -> bytes:
        try:
            return blobs[(test_revision, path)]
        except KeyError as exc:
            raise BundleError(f"missing self-test blob: {path}") from exc

    boundary = [
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
            "initial_evidence_sha256": None,
            "final_evidence_sha256": None,
            "result": "Unknown",
            "notes": ["not observed"],
        },
        {
            "id": "B3",
            "kind": "runtime",
            "initial_evidence_sha256": None,
            "final_evidence_sha256": None,
            "result": "Unknown",
            "notes": ["not observable"],
        },
        {
            "id": "B4",
            "kind": "temporary_paths",
            "initial_evidence_sha256": zeros,
            "final_evidence_sha256": zeros,
            "result": "Pass",
            "notes": [],
        },
    ]
    spec = {
        "boundary": boundary,
        "claims": [
            {
                "id": "C1",
                "hunk_id": "H1",
                "text": "Use new guidance.",
                "classification": "Authoritative",
                "sources": [
                    {
                        "path": "docs/source.md",
                        "start_line": 1,
                        "end_line": 1,
                        "role": "authority",
                    }
                ],
            }
        ],
        "hunks": [
            {
                "id": "H1",
                "destination": "docs/test.md",
                "after_text": "new\n",
                "unknowns": [],
            }
        ],
        "limitations": ["self-test"],
    }
    bundle, digest = build_bundle(
        spec=spec,
        root="/tmp/repository",
        revision=revision,
        branch="test",
        producer_skill_path=".agents/skills/onboard-repository/SKILL.md",
        read_blob=read_blob,
    )
    header = f"<!-- ONBOARDING_EVIDENCE_BUNDLE_V2:BEGIN sha256={digest} -->\n"
    require(bundle.startswith(header), "self-test bundle header is invalid")
    inner = bundle[len(header) : -len(BUNDLE_END + "\n")]
    require(
        sha256_bytes(inner.encode("utf-8")) == digest,
        "self-test bundle digest is invalid",
    )
    require(
        sha256_bytes(b"authority\n") in bundle, "self-test source hash was not computed"
    )
    require(
        "<!-- ONBOARDING_PATCH:H1:BEGIN -->" in bundle, "self-test patch is missing"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path)
    parser.add_argument("--revision")
    parser.add_argument("--branch")
    parser.add_argument(
        "--producer-skill-path",
        default=".agents/skills/onboard-repository/SKILL.md",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
            print(json.dumps({"self_test": "passed", "valid": True}, sort_keys=True))
            return 0
        require(args.repository is not None, "--repository is required")
        require(isinstance(args.revision, str), "--revision is required")
        require(isinstance(args.branch, str), "--branch is required")
        spec = json.load(sys.stdin)
        require(isinstance(spec, dict), "stdin spec root must be an object")
        repository = args.repository.resolve()
        root_result = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "--show-toplevel"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        require(root_result.returncode == 0, "repository is not a Git worktree")
        require(
            Path(root_result.stdout.strip()).resolve() == repository,
            "repository must be the Git worktree root",
        )
        bundle, _ = build_bundle(
            spec=spec,
            root=str(repository),
            revision=args.revision,
            branch=args.branch,
            producer_skill_path=args.producer_skill_path,
            read_blob=git_blob_reader(repository),
        )
        sys.stdout.write(bundle)
        return 0
    except (BundleError, RenderError, json.JSONDecodeError, OSError) as exc:
        print(
            json.dumps({"error": str(exc), "valid": False}, sort_keys=True),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
