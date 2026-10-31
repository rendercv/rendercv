---
toc_depth: 2
---

# Contributing

Start with [Understanding RenderCV](understanding_rendercv.md) to see how the parts fit together, then read the code and tests of the part you want to change. [Setup](index.md) prepares your computer.

## Writing documentation

The developer guide teaches software engineering through RenderCV. Write for a reader who has never heard of the topic and may not be technical. After reading, they should have an intuitive picture of what the thing is and why we need it, and that picture must also be technically accurate. For each tool or idea:

1. Start with the problem it solves: what goes wrong without it.
2. Explain the idea in plain words, with a small example when it helps, and define each term where it first appears.
3. Show where RenderCV uses it: the file, the command, or the code.

Use the fewest words that keep the reasoning and the intuition. Cut repetition, filler, and claims you haven't checked.

## Code conventions

Use Python 3.12+ syntax. Write **type annotations**, which state what kind of value a function takes and returns (`def initials(name: str) -> str`), for functions, variables, and class attributes; the type checker uses them to catch mistakes. Prefer `type` aliases, `X | Y` unions, `X | None` for optional values, and type parameters such as `[T]`. Keep the code working on every supported Python version.

Write Google-style **docstrings**, the descriptions at the start of each function and class. Say what it does first; add why, or an example, when that tells the reader something new. Document the arguments, the return value, and the exceptions callers must handle. Don't write comments that repeat the code; explain the constraints and decisions behind it.

Keep validation in `schema/`. A model that passed validation is the renderer's contract: the renderer produces the requested files, and an unexpected failure propagates as a bug (see [the validation boundary](understanding_rendercv.md#validating-the-data)). Don't turn compiler errors or programming errors into input errors after validation. Put rules that involve several top-level fields on `RenderCVModel`, and rules about one field on the model that owns it.

Use `uv` for Python commands, and the `justfile` for routine work:

```bash
just format
just check
just test
```

All checks must pass before you commit. Fix the cause of a lint or type error. Silence a check only for a single line, only when the rule can't be satisfied otherwise, and say why next to it.

## Fixing an issue

An **issue** is a report on GitHub: a bug, a feature request, or a question. Read it with all its comments, the linked reports, and the related code. Decide whether it describes a bug you can reproduce, a feature request, or a usage question.

For a bug, first add a test that reproduces it and confirm that the test fails. Then fix the code, and run that test and the related tests again. [Testing](testing.md) covers reference files, generated files, and stress tests.

To propose a change, open a **pull request (PR)**. You make your commits on a **branch**, a separate line of history that leaves `main` untouched, and the PR asks for that branch to be merged into `main` after review. Keep each PR to one purpose and target `main`. Explain the problem, the new behavior, and the checks you ran, and credit the people whose work you used. Write `Closes #…` only when the change fully resolves the issue, because GitHub closes the issue when the PR is merged; otherwise say what remains.

## Reviewing a pull request

Read the linked issue, the complete changed files on the PR's branch, the code that calls them, and their tests. Compare with `main`, and check the results of the automated checks. Look at correctness, input validation, architecture, compatibility, and whether the tests would catch the reported bug.

Make each finding actionable: the file and line, the input that triggers the problem, its consequence, and the change needed. Separate problems that block merging from suggestions. Passing tests show that the tested behavior works; they don't prove that every case does.

## Triaging reports

**Triage** means sorting new reports: deciding what each one is and what should happen next. Search open and closed issues for duplicates. Reproduce the reported behavior when you have enough information; otherwise ask for the missing input, version, or steps. Answer usage questions directly. For a feature request, explain how it fits RenderCV's existing content and design model before proposing a new option.

A triage reply states the finding, the relevant code, and a concrete next step. Explain decisions about duplicates or out-of-scope requests and link the related discussion. Don't promise dates or effort estimates. In automated triage, invite the reporter to reply with `@claude` and instructions if they want a proposed fix. Apply labels or assignments only when a maintainer asks.
