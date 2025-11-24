# Writing Tests

Welcome! This guide explains how we write tests in RenderCV. Following these patterns helps keep our test suite consistent, maintainable, and easy to contribute to.

## Test Types

Tests in `tests/` fall into two categories:

1. **Unit tests**: Folders that mirror `src/rendercv/` structure (e.g., `tests/renderer/`, `tests/schema/`, `tests/cli/`)
2. **Non-unit tests**: `tests/integration/`, `tests/scripts/`

## Unit Tests

### Philosophy

Our testing philosophy is simple:

1. **Unit focused**: Test functions in isolation. Input → output. Nothing more.
2. **DRY**: Use `pytest.mark.parametrize` for variations instead of repeating test logic.
3. **High coverage**: Cover edge cases through parameterization, not more test functions.

### File structure

Create one test file per source file, mirroring the folder structure:

```
src/rendercv/renderer/templater/date.py
    → tests/renderer/templater/test_date.py

src/rendercv/schema/models/cv/section.py
    → tests/schema/models/cv/test_section.py
```

### When to use classes

**Use a class** when a function needs multiple test functions:

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

**Skip the class** when a function needs only one test:

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


def test_make_keywords_bold():
    assert make_keywords_bold("test string", ["test"]) == "**test** string"
```

### Use parametrize for variations

This is one of the most important patterns. Instead of writing multiple similar tests, use `@pytest.mark.parametrize`:

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

### Using conftest.py for shared fixtures

When fixtures need to be shared across multiple test files, place them in a `conftest.py` file. The key principle is: **use the closest conftest.py possible**.

- If fixtures are used by multiple files **in the same folder**, put them in that folder's `conftest.py`
- If fixtures are used by files **in different folders**, put them in the `conftest.py` of their closest common parent

For example:

```
tests/
├── conftest.py                    # Fixtures used across all tests
├── schema/
│   ├── conftest.py                # Fixtures used by schema tests only
│   └── models/
│       └── cv/
│           ├── conftest.py        # Fixtures used by CV model tests only
│           ├── test_section.py
│           └── test_cv.py
└── renderer/
    └── ...
```

This keeps fixtures close to where they're used and makes it clear which tests depend on them.

### Guidelines

1. **One assertion per logical check**. Multiple asserts are fine if they're testing the same behavior.

2. **Prefer real behavior over mocking**. Only mock when there's no practical alternative.

3. **Only create fixtures when truly needed**. If something can be created in one self-explanatory line, just inline it:

   ```python
   # Don't do this:
   @pytest.fixture
   def locale(self):
       return EnglishLocale()

   def test_something(self, locale):
       result = format_date(Date(2020, 1, 1), locale)
       ...

   # Do this instead:
   def test_something(self):
       result = format_date(Date(2020, 1, 1), EnglishLocale())
       ...
   ```

   Fixtures are useful when setup is complex, expensive, or needs to be shared across many tests.

4. **Test names should describe behavior**, not implementation:
   - Good: `test_returns_none_for_incomplete_data`
   - Less clear: `test_function_with_none_input`

5. **Keep tests simple**:
   ```python
   def test_something(self, input, expected):
       result = function_under_test(input)
       assert result == expected
   ```

6. **Add docstrings only when the test name isn't self-explanatory**.

### What to test

- Happy paths (valid inputs → expected outputs)
- Edge cases (empty strings, None, boundary values)
- Error cases (invalid inputs → None or exceptions)
- Configuration variations through parameterization

### Patterns to avoid

- Testing implementation details rather than behavior
- Writing integration tests disguised as unit tests
- Repeating the same assertion logic across multiple test functions
- Creating complex fixtures when simple values would work

## Non-Unit Tests

<!-- TODO -->
