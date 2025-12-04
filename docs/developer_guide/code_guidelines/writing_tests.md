# Writing Tests

## File Structure

Each test file tests all classes and functions in its corresponding source file. The structure mirrors `src/rendercv/`:

```
src/rendercv/renderer/templater/date.py
    → tests/renderer/templater/test_date.py
    (tests all functions and classes in date.py)

src/rendercv/schema/models/cv/section.py
    → tests/schema/models/cv/test_section.py
    (tests all functions and classes in section.py)
```

## Naming Conventions

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

## Use Parametrize for Variations

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

## Shared Fixtures with conftest.py

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

## Testing Principles

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

**Prefer real behavior over mocking.** Only mock when there's no practical alternative (external APIs, file system, etc.).

**Name tests by expected behavior, not by input:**

- Good: `test_returns_none_for_incomplete_data` - describes what should happen
- Bad: `test_function_with_none_input` - describes input but not behavior

**Keep tests simple:**

```python
def test_something(self, input, expected):
    result = function_under_test(input)
    assert result == expected
```

**What to test:**

- Input → expected output
- Input → expected error

**What to avoid:**

- Testing implementation details instead of behavior
- Complex test setup when simple values work
