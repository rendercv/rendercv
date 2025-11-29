# Writing Tests

This guide explains how to write tests for RenderCV. Follow these patterns to keep the test suite consistent and maintainable.

## Test Organization

Tests live in `tests/` and fall into two categories:

1. **Unit tests**: Mirror the `src/rendercv/` structure (e.g., `tests/renderer/`, `tests/schema/`, `tests/cli/`)
2. **Non-unit tests**: `tests/integration/`, `tests/scripts/`

## Unit Tests

### File Structure

One test file per source file, mirroring the folder structure:

```
src/rendercv/renderer/templater/date.py
    → tests/renderer/templater/test_date.py

src/rendercv/schema/models/cv/section.py
    → tests/schema/models/cv/test_section.py
```

### Naming Conventions

Test names must include the function being tested.

- **Single test**: `test_` + function name → `test_clean_url`
- **Multiple tests**: `Test` + PascalCase function name → `TestCleanUrl`

### When to Use Classes

Use a class when a function needs multiple test functions:

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

Skip the class when a function needs only one test:

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

**Add docstrings when something isn't self-explanatory.** This applies to both tests and fixtures. If a new developer would look at it and wonder "what is this doing?" or "why is it done this way?"—add a short docstring. Keep it to the minimum necessary: what it does, why it exists, why it's implemented that way if non-obvious.

### What to Test

- Inputs → expected outputs
- Inputs → expected errors

### Patterns to Avoid

- Testing implementation details rather than behavior
- Writing integration tests disguised as unit tests
- Creating complex fixtures when simple values work

## Non-Unit Tests

<!-- TODO -->