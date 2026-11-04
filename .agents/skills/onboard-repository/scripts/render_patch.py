#!/usr/bin/env python3
"""Render one authenticated read-only patch from a complete destination image."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath


ID_RE = re.compile(r"^[A-Z][A-Z0-9_-]*$")
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")


class RenderError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RenderError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def require_relative_path(value: str) -> None:
    candidate = PurePosixPath(value)
    require(value != "", "destination must not be empty")
    require(not candidate.is_absolute(), "destination must be repository-relative")
    require(".." not in candidate.parts, "destination must not traverse parents")


def render_patch(before: bytes, after: bytes, destination: str) -> str:
    require(
        before != after, "complete after image is identical to the pinned destination"
    )
    require(before.endswith(b"\n"), "destinations without a final LF are unsupported")
    require(after.endswith(b"\n"), "complete after image must end with LF")
    try:
        before_text = before.decode("utf-8")
        after_text = after.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RenderError("destination and complete after image must be UTF-8") from exc
    patch = "".join(
        difflib.unified_diff(
            before_text.splitlines(keepends=True),
            after_text.splitlines(keepends=True),
            fromfile=f"a/{destination}",
            tofile=f"b/{destination}",
            lineterm="\n",
        )
    )
    require(
        patch.startswith(f"--- a/{destination}\n+++ b/{destination}\n"),
        "renderer did not produce the expected file headers",
    )
    require("@@ " in patch, "renderer did not produce a numbered patch hunk")
    require(patch.endswith("\n"), "rendered patch must end with LF")
    return patch


def pinned_blob(repository: Path, revision: str, destination: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repository), "show", f"{revision}:{destination}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    require(
        result.returncode == 0,
        "git show failed: " + result.stderr.decode("utf-8", errors="replace").strip(),
    )
    return result.stdout


def self_test() -> None:
    before = b"# Agent Instructions\n\nConsumer-owned line.\n\n<!-- HARNESS:BEGIN -->\nold\n<!-- HARNESS:END -->\n"
    after = b"# Agent Instructions\n\nConsumer-owned line.\n\n<!-- HARNESS:BEGIN -->\nnew\n<!-- HARNESS:END -->\n"
    patch = render_patch(before, after, "AGENTS.md")
    require(" Consumer-owned line.\n" in patch, "self-test lost consumer-owned context")
    require("-old\n+new\n" in patch, "self-test did not render the replacement")
    require(
        sha256_bytes(patch.encode("utf-8"))
        == "04e91cfec8e7a2c0b2658c1c7d39f89cc55ebf288ee6c279c578990b89991899",
        "self-test patch digest changed",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, default=Path("."))
    parser.add_argument("--revision")
    parser.add_argument("--destination")
    parser.add_argument("--hunk-id")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
            print(json.dumps({"self_test": "passed", "valid": True}, sort_keys=True))
            return 0
        require(
            isinstance(args.revision, str)
            and REVISION_RE.fullmatch(args.revision) is not None,
            "--revision must be a full lowercase 40-character Git revision",
        )
        require(isinstance(args.destination, str), "--destination is required")
        require_relative_path(args.destination)
        require(
            isinstance(args.hunk_id, str) and ID_RE.fullmatch(args.hunk_id) is not None,
            "--hunk-id must start with an uppercase letter and use uppercase letters, digits, _ or -",
        )
        before = pinned_blob(args.repository, args.revision, args.destination)
        after = sys.stdin.buffer.read()
        patch = render_patch(before, after, args.destination)
        metadata = {
            "destination": args.destination,
            "destination_after_sha256": sha256_bytes(after),
            "destination_before_sha256": sha256_bytes(before),
            "id": args.hunk_id,
            "patch_sha256": sha256_bytes(patch.encode("utf-8")),
        }
        print(json.dumps(metadata, sort_keys=True))
        print(f"<!-- ONBOARDING_PATCH:{args.hunk_id}:BEGIN -->")
        print("```diff")
        sys.stdout.write(patch)
        print("```")
        print(f"<!-- ONBOARDING_PATCH:{args.hunk_id}:END -->")
        return 0
    except (OSError, RenderError) as exc:
        print(
            json.dumps({"error": str(exc), "valid": False}, sort_keys=True),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
