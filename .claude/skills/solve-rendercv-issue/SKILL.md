---
name: solve-rendercv-issue
description: Pick up a GitHub issue (or accept one), fully understand the RenderCV codebase, implement the fix/feature with tests, and open a PR to origin/main.
---

# Solve a RenderCV Issue

Pick a GitHub issue from the `rendercv` repository, implement a complete solution with tests, and open a pull request to `origin/main`.

**IMPORTANT:** This skill MUST be run inside a git worktree (`isolation: "worktree"`). All work happens in the worktree so the main working tree stays clean.

## Step 1: Select an issue

If an issue number or URL is provided, use it. Otherwise, pick the highest-priority open issue automatically:

```bash
gh issue list --repo rendercv/rendercv --state open --sort created --json number,title,labels,body --limit 10
```

Choose the most impactful issue that is not labeled `wontfix` or `question`. Prefer bugs over features, and smaller-scoped issues over vague ones.

Read the full issue body:

```bash
gh issue view <number> --repo rendercv/rendercv
```

## Step 2: Understand RenderCV

Before writing any code, build a deep understanding of the project by reading these files **in order**:

### 2a: Project metadata and dependencies

- @pyproject.toml

### 2b: Architecture and design

- @docs/developer_guide/understanding_rendercv.md

### 2c: Code guidelines

- @docs/developer_guide/code_guidelines/source_code.md

### 2d: Testing guidelines

- @docs/developer_guide/code_guidelines/tests.md
- @docs/developer_guide/testing.md

### 2e: Source structure

Explore the three top-level packages to understand the module layout:

- @src/rendercv/schema/
- @src/rendercv/renderer/
- @src/rendercv/cli/

For each, read the directory tree and skim key files relevant to the issue.

### 2f: Test structure

- @tests/

The test structure mirrors `src/rendercv/`. Read the test files in the area related to the issue.

### 2g: Available commands

- @justfile

## Step 3: Set up the branch

Always use the same branch name `fix-issues` so that fixes stack when the skill is invoked multiple times:

```bash
git fetch origin main
git checkout fix-issues 2>/dev/null || git checkout -b fix-issues origin/main
```

## Step 4: Reproduce the problem (bugs only)

For bug reports:

1. Write a **failing test** that demonstrates the bug. Place it in the correct test file following the mirror structure (`src/rendercv/renderer/foo.py` → `tests/renderer/test_foo.py`).
2. Run only that test to confirm it fails:
   ```bash
   uv run --frozen --all-extras pytest tests/path/to/test_file.py::test_name -x
   ```
3. Do NOT proceed to the fix until you have a red test.

## Step 5: Implement the solution

Write the fix or feature. Follow these principles strictly:

### Code quality

- **Lean and DRY**: No duplication. No dead code. No commented-out code.
- **Elegant architecture**: The simplest correct solution. No duct tape. No over-engineering.
- **Strict typing**: Every function, variable, and class attribute must have type annotations. Use Python 3.12+ syntax (`type` statements, `X | Y` unions, `X | None`).
- **No private API syntax**: Never use underscore-prefixed names (`_Foo`, `_bar`). All names are public.
- **Docstrings**: Google-style with Why/Args/Returns/Raises sections, only for new functions/classes.
- **No unnecessary changes**: Only touch code directly related to the issue. Don't refactor surrounding code, don't add comments to existing code, don't "improve" unrelated things.

### Testing

- **Every new code path must be tested.** If you add a function, test it. If you add a branch, cover it.
- **100% coverage must be maintained.** Run `just test-coverage` and verify no coverage is lost.
- **Test placement**: Mirror the source structure. Tests for `src/rendercv/renderer/foo.py` go in `tests/renderer/test_foo.py`.
- **Use existing fixtures**: Check `tests/conftest.py` and the relevant `conftest.py` files for existing fixtures before creating new ones.

## Step 6: Verify the solution

Run all checks and tests. Every single one must pass:

```bash
just format
just check
just test
just test-coverage
```

If `just check` or `just test` shows any errors, fix them before proceeding. If coverage dropped, add more tests.

If reference files changed intentionally, update them:

```bash
just update-testdata
```

## Step 7: Commit

Stage only the files you changed. Write a clear commit message:

```bash
git add <specific-files>
git commit -m "Fix #<number>: <concise description of what and why>"
```

## Step 8: Report results

Do NOT push or create a PR. The user will review the changes in the worktree first.

Tell the user:
1. What the issue was (root cause)
2. How it was fixed (approach)
3. What tests were added or modified
4. Coverage status (must remain 100%)
5. The worktree path so they can review the changes
