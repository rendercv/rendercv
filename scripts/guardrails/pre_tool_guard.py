"""PreToolUse guardrail hook for Claude Code.

Why: enforces the repository's Mandatory Enforcement Rules (MER) from
docs/patterns/guardrails.md at the tool boundary — the `main` branch is
protected (no commits, merges, or file edits while on it) and destructive
git/shell commands are blocked before they run.

Reads the hook payload JSON from stdin and emits a PreToolUse
permissionDecision ("deny") with a reason when a rule is violated.
Silent exit 0 means "no objection" (the normal permission flow continues).
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROTECTED_BRANCHES: frozenset[str] = frozenset({"main", "master"})

# Patterns are matched case-insensitively anywhere in the command string.
# Conservative by design: a false positive costs one manual confirmation,
# a false negative costs history or the protected branch.
DENY_PATTERNS: list[tuple[str, str]] = [
    (
        r"git\s+push\b(?=[^|;&]*\b(main|master)\b)",
        (
            "Pushing to a protected branch (main/master) is blocked. Push to a feature"
            " branch (e.g. quan) and open a PR to develop."
        ),
    ),
    (
        r"git\s+push\b[^|;&]*(--force\b|-f\b|--mirror\b|--delete\b)",
        (
            "Force/mirror/delete pushes are blocked. Use --force-with-lease on a"
            " feature branch only after explicit user approval."
        ),
    ),
    (
        r"git\s+reset\s+--hard",
        (
            "git reset --hard discards local work and is blocked. Ask the user before"
            " running destructive resets."
        ),
    ),
    (
        r"git\s+clean\s+-[a-z]*f",
        (
            "git clean -f deletes untracked files and is blocked. Ask the user before"
            " running it."
        ),
    ),
    (
        r"git\s+branch\s+(-D|-d|--delete)\s+(main|master)\b",
        "Deleting a protected branch is blocked.",
    ),
    (
        r"git\s+checkout\s+(--\s+)?\.(?:\s|$)",
        (
            "git checkout -- . discards all local changes and is blocked. Ask the user"
            " first."
        ),
    ),
    (
        r"rm\s+-[a-z]*r[a-z]*f|rm\s+-[a-z]*f[a-z]*r",
        (
            "Recursive force deletion (rm -rf) is blocked. Ask the user and name the"
            " exact target first."
        ),
    ),
    (
        r"Remove-Item\b[^|;&]*-Recurse\b[^|;&]*-Force\b",
        (
            "Remove-Item -Recurse -Force is blocked. Ask the user and name the exact"
            " target first."
        ),
    ),
]

# Commands that write history and are therefore forbidden while on main.
HISTORY_WRITING = re.compile(
    r"git\s+(commit|merge|rebase|cherry-pick|revert|am)\b", re.IGNORECASE
)


def current_branch(cwd: str) -> str:
    """Return the current git branch name, or "" when it cannot be determined."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except OSError:
        return ""


def deny(reason: str) -> None:
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or str(
        Path(__file__).resolve().parent.parent.parent
    )

    if tool_name in ("Bash", "PowerShell"):
        command = tool_input.get("command", "")
        for pattern, reason in DENY_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                deny(f"[guardrail] {reason}")
        if HISTORY_WRITING.search(command):
            branch = current_branch(project_dir)
            if branch in PROTECTED_BRANCHES:
                deny(
                    "[guardrail] History-writing git command blocked on protected"
                    f" branch '{branch}'. Switch to a feature branch (e.g. quan) first."
                )

    elif tool_name in ("Edit", "Write", "NotebookEdit"):
        file_path = tool_input.get("file_path", "") or tool_input.get(
            "notebook_path", ""
        )
        # Only guard files inside the repository working tree.
        try:
            inside = (
                Path(file_path).resolve().is_relative_to(Path(project_dir).resolve())
            )
        except (ValueError, OSError):
            inside = False
        if inside:
            branch = current_branch(project_dir)
            if branch in PROTECTED_BRANCHES:
                deny(
                    "[guardrail] File edits are blocked while on protected branch"
                    f" '{branch}'. Switch to a feature branch (e.g. quan) first."
                )

    sys.exit(0)


if __name__ == "__main__":
    main()
