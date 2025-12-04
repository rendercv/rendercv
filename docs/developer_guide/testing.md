# Testing

## What Are Tests?

Tests check if your code does what it's supposed to do. Every time you change something, you need to verify it still works. Instead of manually checking everything, you write test code once and rerun it automatically.

Here's a simple example:

```python
def sum(a, b):
    return a + b

def test_sum():
    assert sum(2, 3) == 5
    assert sum(-1, 1) == 0
    assert sum(0, 0) == 0
```

If you change something in `sum`, you can run `test_sum` again to see if it's still working.

## pytest

[pytest](https://github.com/pytest-dev/pytest) is a Python library that provides utilities to write and run tests. When you run the `pytest` command, it automatically finds and executes all functions starting with `test_` in files starting with `test_` inside the `tests/` directory.

### Key pytest Features

To understand RenderCV's tests, you need to know these pytest features:

**Fixtures**: Reusable setup code for tests. They're defined with the `@pytest.fixture` decorator and passed as function arguments:

```python
@pytest.fixture
def sample_data():
    return {"name": "John", "age": 30}

def test_something(sample_data):
    assert sample_data["name"] == "John"
```

**conftest.py**: Special files that define fixtures and configuration available to all tests in that directory and subdirectories. RenderCV uses `tests/conftest.py` to define common fixtures like `testdata_dir` and `update_testdata`.

**Parametrize**: Run the same test with different inputs using `@pytest.mark.parametrize`:

```python
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
])
def test_sum(a, b, expected):
    assert sum(a, b) == expected
```

**Mocking**: Replace parts of your code during testing. Useful for simulating external dependencies or controlling behavior. RenderCV uses the `unittest.mock` library.

### pytest Settings

pytest reads configuration from `pyproject.toml`. RenderCV's pytest settings are in the `[tool.pytest.ini_options]` section. These settings affect how pytest runs—for example, which directories to search for tests, how verbose the output should be, and whether to run tests in parallel. See `pyproject.toml` for details.

## Running RenderCV Tests

Whenever you make changes to RenderCV's source code, run the tests to ensure everything still works. If all tests pass, your changes didn't break anything.

Run all tests:

```bash
just test
```

## Reference File Comparison

Some tests in `tests/renderer/` (specifically `test_pdf_png.py`, `test_typst.py`, `test_markdown.py`, and `test_html.py`) use reference file comparison:

1. Tests generate output files by running RenderCV
2. Generated files are compared against reference files in `tests/renderer/testdata/`
3. If they match exactly, the test passes. Any difference fails the test.

The `testdata_dir` fixture from `tests/conftest.py` provides the path to each test module's testdata directory:

```python
@pytest.fixture
def testdata_dir(request: pytest.FixtureRequest) -> pathlib.Path:
    module_path = pathlib.Path(request.node.module.__file__)
    module_name = module_path.stem
    base_dir = module_path.parent
    return base_dir / "testdata" / module_name
```

### Updating Reference Files

When you intentionally change RenderCV's output (e.g., fixing typography), tests will fail because the new output differs from old reference files. Update them:

```bash
just update-testdata
```

!!! warning
    After updating testdata, manually verify the new files are correct. These become the source of truth for all future tests. If you commit broken reference files, tests will pass even when RenderCV produces bad output. Check generated PDFs and PNGs carefully before committing.

## Coverage

Coverage measures which lines of code are executed when tests run. If tests execute a line, it's included in coverage. If tests execute all lines in `src/rendercv/`, coverage is 100%.

High coverage means tests execute most of your code. Low coverage means parts of your code are never executed by tests—you have no automated verification those parts work.

Run tests with coverage:

```bash
just test-coverage
```

This generates:

- Terminal output showing coverage percentage
- HTML report in `htmlcov/index.html` showing which lines are covered (green) and which aren't (red)

Coverage settings are in `pyproject.toml` under `[tool.coverage.run]` and `[tool.coverage.report]`.

## Writing RenderCV Tests

### File Structure

Each test file tests all classes and functions in its corresponding source file. The structure mirrors `src/rendercv/`:

```
src/rendercv/renderer/templater/date.py
    → tests/renderer/templater/test_date.py
    (tests all functions and classes in date.py)

src/rendercv/schema/models/cv/section.py
    → tests/schema/models/cv/test_section.py
    (tests all functions and classes in section.py)
```

### Naming Conventions

Test names must include the name of the function or class being tested.

**When you need only one test**, use `test_` + the name:

- Testing `clean_url()` → `test_clean_url`
- Testing `Cv` → `test_cv`

**When you need multiple tests**, wrap them in a class using `Test` + PascalCase name:

- Testing `clean_url()` → `TestCleanUrl`
- Testing `Cv` → `TestCv`

Example with one test:

```python
@pytest.mark.parametrize(
    ("url", "expected_clean_url"),
    [
        ("https://example.com", "example.com"),
        ("https://example.com/", "example.com"),
        ("https://example.com/test", "example.com/test"),
    ],
)
def test_clean_url(url, expected_clean_url):
    assert clean_url(url) == expected_clean_url
```

Example with multiple tests:

```python
class TestComputeDateString:
    @pytest.mark.parametrize(...)
    def test_date_parameter_takes_precedence(self, ...):
        ...

    @pytest.mark.parametrize(...)
    def test_date_ranges(self, ...):
        ...

    @pytest.mark.parametrize(...)
    def test_returns_none_for_incomplete_data(self, ...):
        ...
```

### Use Parametrize for Variations

Instead of writing multiple similar tests, use `@pytest.mark.parametrize`:

```python
@pytest.mark.parametrize(
    ("input_a", "input_b", "expected"),
    [
        ("2020-01-01", "2021-01-01", "Jan 2020 – Jan 2021"),
        ("2020-01", "2021-02-01", "Jan 2020 – Feb 2021"),
        (2020, 2021, "2020 – 2021"),
    ],
)
def test_date_ranges(self, input_a, input_b, expected):
    result = compute_date_string(None, input_a, input_b, EnglishLocale())
    assert result == expected
```

### Shared Fixtures with conftest.py

Place shared fixtures in `conftest.py`. Use the closest one possible:

- Fixtures for one folder → that folder's `conftest.py`
- Fixtures for multiple folders → their closest common parent's `conftest.py`

```
tests/
├── conftest.py                    # Used across all tests
├── schema/
│   ├── conftest.py                # Used by schema tests only
│   └── models/
│       └── cv/
│           ├── conftest.py        # Used by CV model tests only
│           ├── test_section.py
│           └── test_cv.py
└── renderer/
    └── ...
```

### Guidelines

**Keep tests focused.** Test functions in isolation: input → output.

**Don't create unnecessary fixtures.** If setup is one clear line, inline it:

```python
# Don't:
@pytest.fixture
def locale(self):
    return EnglishLocale()

def test_something(self, locale):
    result = format_date(Date(2020, 1, 1), locale)

# Do:
def test_something(self):
    result = format_date(Date(2020, 1, 1), EnglishLocale())
```

**Prefer real behavior over mocking.** Only mock when there's no practical alternative.

**Name tests by what the function should do, not what you're passing in:**

- Good: `test_returns_none_for_incomplete_data` — tells you the expected behavior
- Unclear: `test_function_with_none_input` — tells you nothing about what should happen

**Keep tests simple:**

```python
def test_something(self, input, expected):
    result = function_under_test(input)
    assert result == expected
```

**Add docstrings when something isn't self-explanatory.** If a new developer would wonder "what is this doing?" or "why is it done this way?"—add a short docstring.

### What to Test

- Inputs → expected outputs
- Inputs → expected errors

### Patterns to Avoid

- Testing implementation details rather than behavior
- Writing integration tests disguised as unit tests
- Creating complex fixtures when simple values work

### Exceptions

Most tests follow the patterns above. A few exceptions exist:

- `tests/test_main.py`: Tests that the `__main__` module runs correctly
- `tests/test_tests.py`: Validates test directory structure matches source structure
