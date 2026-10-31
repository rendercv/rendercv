---
toc_depth: 2
---

# Testing

A change in one place of a program can break something somewhere else. Checking everything by hand after each change is slow, and things get missed. A **test** is a small program that runs a piece of RenderCV and checks the result against what it should be. Thousands of them run in under a minute, so every change gets checked against everything RenderCV is supposed to do.

RenderCV uses [pytest](https://docs.pytest.org/), which finds the functions named `test_...` in the `tests/` folder and runs them. That folder mirrors `src/rendercv/`, so the tests for a module are easy to find. This test checks that an overlay replaces a whole list:

```python
from rendercv.schema.override_dictionary import merge_overlay


def test_overlay_replaces_a_list():
    data = {"items": ["first", "second"]}
    merge_overlay(data, {"items": ["replacement"]})
    assert data["items"] == ["replacement"]
```

`assert` states what must be true. If it isn't, the test fails and pytest shows the actual value next to the expected one.

When fixing a bug, write the test first and watch it fail on the reported input; that proves the test can detect the bug. Once the fix makes it pass, the test stops the bug from coming back unnoticed. A bug that comes back is called a **regression**.

## Running the tests

```bash
just test
just test-coverage
```

**Coverage** shows which lines of code ran during the tests. Open `htmlcov/index.html` to find lines that no test reached. A line that ran wasn't necessarily checked, so coverage finds gaps but can't prove that code is correct.

While working on one area, run only its tests, and stop at the first failure with `-x`:

```bash
uv run --frozen --all-extras pytest tests/renderer/templater/test_date.py -x
```

## Writing tests

Test what the code does, not how it does it: check the result or the error, not which internal functions ran. Then the code can be reorganized without rewriting its tests. Use the real parsing, validation, and rendering rather than imitations. A **mock** is a stand-in for a real dependency; use one only where the real thing doesn't belong in a test, such as a website that would otherwise be contacted. Test file handling with real temporary files.

A pytest **fixture** prepares something a test needs and passes it in as an argument. A test that asks for `tmp_path`, for example, receives a fresh empty folder. Fixtures shared by several test files go in the nearest `conftest.py`, which pytest loads automatically. Keep simple values inside the test itself.

Name a single test after the function or class it checks. Group several tests in a class named `TestFunctionName` or `TestClassName`, with method names that describe the expected behavior. To check one behavior with several inputs, list the input and expected-result pairs with `pytest.mark.parametrize` instead of copying the test.

Choose the edge cases that matter for the change: missing fields, empty lists, non-English characters, multi-line text, nested entries, paths outside the current folder. Tests of the whole pipeline should confirm that invalid input fails during validation and that unexpected failures in the renderer aren't hidden.

## Comparing rendered output

A handful of assertions can't describe a whole page. Renderer tests therefore compare generated files with saved **reference files** in `tests/renderer/testdata/`: output that someone inspected and accepted. Any difference on any page fails the test, which catches layout changes that individual assertions would miss.

PDF and PNG tests use only the fonts that ship with RenderCV, so the fonts installed on your computer can't change the result.

When output changes on purpose, run:

```bash
just update-testdata
```

Then look at every changed Typst, Markdown, HTML, PDF, and image file before committing. Updating the references declares the new output correct; doing it without looking could accept a bug as the new standard. Keep focused assertions for the specific behavior next to these broad comparisons.

Other tests check that generated files, such as the schema and the examples, match the code that generates them. Regenerate the ones your change affects.

## Testing rules across many inputs

An ordinary test checks a few chosen examples. A **property-based test** checks a rule that must hold for every input, for example "bolding the keywords twice gives the same result as bolding them once". A tool invents the inputs, including odd combinations a person wouldn't think of.

[Hypothesis](https://hypothesis.readthedocs.io/) is that tool. You describe what the inputs look like with **strategies**, and Hypothesis generates many of them. When an input breaks the rule, Hypothesis shrinks it to the smallest input that still fails, which makes the cause easy to see. RenderCV's strategies mix formatting, links, code, Typst code, lists, multi-line text, and missing fields.

`just test` generates 100 inputs per rule, and the automated checks on GitHub generate 200; named **profiles** in `tests/conftest.py` set these amounts. After changing how content is processed, run the `stress` profile:

```bash
HYPOTHESIS_PROFILE=stress uv run --frozen --all-extras pytest tests/renderer/templater
```

It asks for 1,500 inputs per rule; rules with fewer possible inputs finish sooner. When Hypothesis finds a failure, fix the bug and keep the shrunk input as an ordinary regression test.
