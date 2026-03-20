---
name: solve-rendercv-issue
description: Pick up a GitHub issue (or accept one), fully understand the RenderCV codebase, implement the fix/feature with tests, and open a PR to origin/main.
---

# Solve a RenderCV Issue

Pick a GitHub issue from the `rendercv` repository, implement a complete solution with tests, and open a pull request to `origin/main`.

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

Before writing any code, build a deep understanding of the project:

- @.claude/skills/rendercv-development-context/SKILL.md
- @.claude/skills/rendercv-testing-context/SKILL.md

Read the referenced files, focusing on modules relevant to the issue.

## Step 3: Set up the branch

Create a branch from `origin/main` named after the issue:

```bash
git fetch origin main
git checkout -b claude/issue-<number> origin/main
```

## Step 4: Reproduce the problem (bugs only)

For bug reports:

1. Write a **failing test** that demonstrates the bug. Place it in the correct test file per the testing standards in the development context.
2. Run only that test to confirm it fails:
   ```bash
   uv run --frozen --all-extras pytest tests/path/to/test_file.py::test_name -x
   ```
3. Do NOT proceed to the fix until you have a red test.

## Step 5: Implement the solution

Write the fix or feature following @.claude/skills/rendercv-development-context/SKILL.md and @.claude/skills/rendercv-testing-context/SKILL.md.

## Step 6: Verify the solution

Run all verification commands from the development context (`just format`, `just check`, `just test`, `just test-coverage`). Every single one must pass before proceeding.

## Step 7: Commit and push

Stage only the files you changed. Write a clear commit message and push:

```bash
git add <specific-files>
git commit -m "Fix #<number>: <concise description of what and why>"
git push origin claude/issue-<number>
```

## Step 8: Open a pull request

Create a PR targeting `main`:

```bash
gh pr create \
  --repo rendercv/rendercv \
  --base main \
  --head claude/issue-<number> \
  --title "Fix #<number>: <concise description>" \
  --body "$(cat <<'EOF'
## Summary

<1-3 bullet points explaining what was done and why>

Closes #<number>

## Changes

<list of files changed and why>

## Test plan

<what tests were added or modified>
EOF
)"
```

Tell the user:
1. What the issue was (root cause)
2. How it was fixed (approach)
3. What tests were added or modified
4. Coverage status (must remain 100%)
5. Link to the PR
