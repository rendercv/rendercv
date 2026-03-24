"""Hypothesis property-based tests for RenderCV.

Why:
    Property-based testing verifies invariants across random inputs,
    catching edge cases that hand-picked parametrized tests miss.
    Focus areas: string processing, date arithmetic, Typst escaping,
    nested dictionary overrides, and Pydantic validators.
"""

import calendar
import copy
import pathlib
import re
import string
from datetime import date as Date

import pydantic
import pydantic_core
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from rendercv.exception import RenderCVUserError
from rendercv.renderer.path_resolver import (
    build_name_variants,
    resolve_output_folder_placeholder,
)
from rendercv.renderer.templater.date import (
    build_date_placeholders,
    compute_time_span_string,
)
from rendercv.renderer.templater.markdown_parser import (
    escape_typst_characters,
    markdown_to_typst,
)
from rendercv.renderer.templater.string_processor import (
    build_keyword_matcher_pattern,
    clean_url,
    make_keywords_bold,
    substitute_placeholders,
)
from rendercv.schema.models.cv.entries.bases.entry_with_complex_fields import (
    get_date_object,
)
from rendercv.schema.models.cv.social_network import SocialNetwork
from rendercv.schema.models.design.typst_dimension import validate_typst_dimension
from rendercv.schema.models.locale.english_locale import EnglishLocale
from rendercv.schema.override_dictionary import (
    apply_overrides_to_dictionary,
    update_value_by_location,
)

# ── Reusable strategies ──────────────────────────────────────────────────────


@st.composite
def valid_date_strings(draw: st.DrawFn) -> str:
    """Generate date strings in YYYY-MM-DD, YYYY-MM, or YYYY format."""
    year = draw(st.integers(min_value=1, max_value=9999))
    fmt = draw(st.sampled_from(["year", "year_month", "year_month_day"]))
    if fmt == "year":
        return f"{year:04d}"
    month = draw(st.integers(min_value=1, max_value=12))
    if fmt == "year_month":
        return f"{year:04d}-{month:02d}"
    max_day = calendar.monthrange(year, month)[1]
    day = draw(st.integers(min_value=1, max_value=max_day))
    return f"{year:04d}-{month:02d}-{day:02d}"


@st.composite
def date_inputs(draw: st.DrawFn) -> str | int:
    """Generate inputs accepted by get_date_object (excluding 'present')."""
    return draw(
        st.one_of(
            valid_date_strings(),
            st.integers(min_value=1, max_value=9999),
        )
    )


keyword_lists = st.lists(
    st.text(
        alphabet=st.characters(categories=("L", "N", "Zs")),
        min_size=1,
        max_size=30,
    ).filter(lambda s: s.strip()),
    min_size=0,
    max_size=10,
)


@st.composite
def placeholder_dicts(draw: st.DrawFn) -> dict[str, str]:
    """Generate placeholder dicts with UPPERCASE keys."""
    keys = draw(
        st.lists(
            st.from_regex(r"[A-Z]{1,15}", fullmatch=True),
            min_size=0,
            max_size=5,
            unique=True,
        )
    )
    values = draw(
        st.lists(
            st.text(
                alphabet=st.characters(categories=("L", "N", "Zs")),
                min_size=0,
                max_size=20,
            ),
            min_size=len(keys),
            max_size=len(keys),
        )
    )
    return dict(zip(keys, values, strict=True))


@st.composite
def urls(draw: st.DrawFn) -> str:
    """Generate realistic URL strings with http/https protocol."""
    protocol = draw(st.sampled_from(["https://", "http://"]))
    domain = draw(st.from_regex(r"[a-z]{2,10}\.[a-z]{2,4}", fullmatch=True))
    path = draw(st.from_regex(r"[a-z0-9_-]{0,20}", fullmatch=True))
    trailing_slash = draw(st.sampled_from(["", "/"]))
    if path:
        return f"{protocol}{domain}/{path}{trailing_slash}"
    return f"{protocol}{domain}{trailing_slash}"


@st.composite
def typst_dimensions(draw: st.DrawFn) -> str:
    """Generate valid Typst dimension strings."""
    sign = draw(st.sampled_from(["", "-"]))
    integer_part = draw(st.integers(min_value=0, max_value=999))
    has_decimal = draw(st.booleans())
    decimal_part = ""
    if has_decimal:
        decimal_part = "." + str(draw(st.integers(min_value=0, max_value=99)))
    unit = draw(st.sampled_from(["cm", "in", "pt", "mm", "em"]))
    return f"{sign}{integer_part}{decimal_part}{unit}"


# ── Module 1: string_processor ───────────────────────────────────────────────


class TestMakeKeywordsBoldProperties:
    @settings(deadline=None)
    @given(text=st.text(max_size=100))
    def test_empty_keywords_is_identity(self, text: str) -> None:
        assert make_keywords_bold(text, []) == text

    @settings(deadline=None)
    @given(text=st.text(max_size=100), keywords=keyword_lists)
    def test_no_double_bolding(self, text: str, keywords: list[str]) -> None:
        result = make_keywords_bold(text, keywords)
        assert "****" not in result

    @settings(deadline=None)
    @given(text=st.text(max_size=100), keywords=keyword_lists)
    def test_output_length_never_shrinks(self, text: str, keywords: list[str]) -> None:
        result = make_keywords_bold(text, keywords)
        assert len(result) >= len(text)

    @settings(deadline=None)
    @given(
        keyword=st.text(
            alphabet=st.characters(categories=("Lu",)),
            min_size=2,
            max_size=10,
        )
    )
    def test_case_sensitivity(self, keyword: str) -> None:
        text = f"before {keyword.lower()} after"
        result = make_keywords_bold(text, [keyword])
        assert f"**{keyword.lower()}**" not in result


class TestSubstitutePlaceholdersProperties:
    @settings(deadline=None)
    @given(text=st.text(max_size=100))
    def test_empty_placeholders_preserves_content(self, text: str) -> None:
        assert substitute_placeholders(text, {}) == text

    @settings(deadline=None)
    @given(placeholders=placeholder_dicts())
    def test_all_placeholder_keys_absent_from_output(
        self, placeholders: dict[str, str]
    ) -> None:
        assume(placeholders)
        # Filter out cases where values reintroduce keys
        keys = set(placeholders.keys())
        assume(not any(k in v for k in keys for v in placeholders.values()))

        template = " ".join(placeholders.keys())
        result = substitute_placeholders(template, placeholders)
        for key in placeholders:
            assert key not in result


class TestCleanUrlProperties:
    @settings(deadline=None)
    @given(url=urls())
    def test_idempotent(self, url: str) -> None:
        assert clean_url(clean_url(url)) == clean_url(url)

    @settings(deadline=None)
    @given(url=urls())
    def test_no_protocol_in_output(self, url: str) -> None:
        result = clean_url(url)
        assert "https://" not in result
        assert "http://" not in result

    @settings(deadline=None)
    @given(url=urls())
    def test_no_trailing_slash(self, url: str) -> None:
        result = clean_url(url)
        if result:
            assert not result.endswith("/")


class TestBuildKeywordMatcherPatternProperties:
    @settings(deadline=None)
    @given(
        keywords=st.frozensets(
            st.text(min_size=1, max_size=20).filter(lambda s: s.strip()),
            min_size=1,
            max_size=10,
        )
    )
    def test_pattern_matches_all_input_keywords(self, keywords: frozenset[str]) -> None:
        pattern = build_keyword_matcher_pattern(keywords)
        for keyword in keywords:
            assert pattern.search(keyword) is not None
        build_keyword_matcher_pattern.cache_clear()

    @settings(deadline=None)
    @given(
        base=st.from_regex(r"[a-zA-Z]{3,8}", fullmatch=True),
        extension=st.from_regex(r"[a-zA-Z]{1,5}", fullmatch=True),
    )
    def test_longest_first_ordering(self, base: str, extension: str) -> None:
        short = base
        long = base + extension
        pattern = build_keyword_matcher_pattern(frozenset({short, long}))
        match = pattern.search(long)
        assert match is not None
        assert match.group(0) == long
        build_keyword_matcher_pattern.cache_clear()


# ── Module 2: markdown_parser ────────────────────────────────────────────────


class TestEscapeTypstCharactersProperties:
    @settings(deadline=None)
    @given(text=st.text(max_size=200))
    def test_never_crashes(self, text: str) -> None:
        escape_typst_characters(text)

    @settings(deadline=None)
    @given(
        text=st.text(
            alphabet=st.characters(
                categories=(), include_characters=string.ascii_letters + " "
            ),
            min_size=1,
            max_size=50,
        )
    )
    def test_plain_ascii_letters_unchanged(self, text: str) -> None:
        # Plain letters and spaces need no escaping (unless they contain
        # sequences like "* " which get escaped)
        assume("*" not in text)
        assert escape_typst_characters(text) == text

    @settings(deadline=None)
    @given(
        name=st.from_regex(r"[a-zA-Z][a-zA-Z-]{0,10}", fullmatch=True),
        arg=st.from_regex(r"[a-zA-Z0-9 ]{0,10}", fullmatch=True),
    )
    def test_typst_commands_preserved(self, name: str, arg: str) -> None:
        command = f"#{name}[{arg}]"
        result = escape_typst_characters(command)
        assert command in result


class TestMarkdownToTypstProperties:
    @settings(deadline=None)
    @given(text=st.text(max_size=300))
    def test_never_crashes_on_arbitrary_input(self, text: str) -> None:
        markdown_to_typst(text)

    @settings(deadline=None)
    @given(
        text=st.text(
            alphabet=st.characters(
                categories=(),
                include_characters=string.ascii_letters + string.digits + " ",
            ),
            min_size=0,
            max_size=100,
        )
    )
    def test_plain_text_content_preserved(self, text: str) -> None:
        assume("*" not in text and "!" not in text)
        assume(text.strip())
        result = markdown_to_typst(text)
        # Markdown normalizes whitespace, so compare non-whitespace content
        assert result.split() == text.split()

    @settings(deadline=None)
    @given(
        text=st.text(max_size=200).filter(
            lambda s: (
                "!!!" not in s and "\t" not in s and "    " not in s and "\r" not in s
            )
        )
    )
    def test_line_count_preserved_for_non_admonition(self, text: str) -> None:
        result = markdown_to_typst(text)
        assert result.count("\n") == text.count("\n")

    @settings(deadline=None)
    @given(
        word=st.text(
            alphabet=st.characters(
                categories=(), include_characters=string.ascii_letters + string.digits
            ),
            min_size=1,
            max_size=20,
        )
    )
    def test_bold_produces_strong(self, word: str) -> None:
        result = markdown_to_typst(f"**{word}**")
        assert f"#strong[{word}]" in result

    @settings(deadline=None)
    @given(
        word=st.text(
            alphabet=st.characters(
                categories=(), include_characters=string.ascii_letters + string.digits
            ),
            min_size=1,
            max_size=20,
        )
    )
    def test_italic_produces_emph(self, word: str) -> None:
        result = markdown_to_typst(f"*{word}*")
        assert f"#emph[{word}]" in result


# ── Module 3: date + entry_with_complex_fields ───────────────────────────────


class TestGetDateObjectProperties:
    @settings(deadline=None)
    @given(date_str=valid_date_strings())
    def test_valid_strings_produce_date_objects(self, date_str: str) -> None:
        result = get_date_object(date_str)
        assert isinstance(result, Date)

    @settings(deadline=None)
    @given(year=st.integers(min_value=1, max_value=9999))
    def test_integer_years_produce_jan_first(self, year: int) -> None:
        result = get_date_object(year)
        assert result == Date(year, 1, 1)

    @settings(deadline=None)
    @given(current_date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_present_returns_current_date(self, current_date: Date) -> None:
        assert get_date_object("present", current_date) == current_date

    @settings(deadline=None)
    @given(
        year=st.integers(min_value=1, max_value=9999),
        month=st.integers(min_value=1, max_value=12),
    )
    def test_yyyy_mm_format_sets_day_to_first(self, year: int, month: int) -> None:
        result = get_date_object(f"{year:04d}-{month:02d}")
        assert result.day == 1


class TestBuildDatePlaceholdersProperties:
    @settings(deadline=None)
    @given(date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_always_returns_8_keys(self, date: Date) -> None:
        result = build_date_placeholders(date, locale=EnglishLocale())
        assert len(result) == 8
        expected_keys = {
            "MONTH_NAME",
            "MONTH_ABBREVIATION",
            "MONTH",
            "MONTH_IN_TWO_DIGITS",
            "DAY",
            "DAY_IN_TWO_DIGITS",
            "YEAR",
            "YEAR_IN_TWO_DIGITS",
        }
        assert set(result.keys()) == expected_keys

    @settings(deadline=None)
    @given(date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_month_in_range(self, date: Date) -> None:
        result = build_date_placeholders(date, locale=EnglishLocale())
        assert 1 <= int(result["MONTH"]) <= 12

    @settings(deadline=None)
    @given(date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_two_digit_variants_always_two_chars(self, date: Date) -> None:
        result = build_date_placeholders(date, locale=EnglishLocale())
        assert len(result["MONTH_IN_TWO_DIGITS"]) == 2
        assert len(result["DAY_IN_TWO_DIGITS"]) == 2

    @settings(deadline=None)
    @given(date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_year_in_two_digits_always_two_chars(self, date: Date) -> None:
        result = build_date_placeholders(date, locale=EnglishLocale())
        assert len(result["YEAR_IN_TWO_DIGITS"]) == 2

    @settings(deadline=None)
    @given(date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_month_name_from_locale(self, date: Date) -> None:
        locale = EnglishLocale()
        result = build_date_placeholders(date, locale=locale)
        assert result["MONTH_NAME"] == locale.month_names[date.month - 1]


class TestComputeTimeSpanStringProperties:
    @settings(deadline=None)
    @given(
        start_year=st.integers(min_value=1900, max_value=2100),
        delta_years=st.integers(min_value=0, max_value=50),
    )
    def test_year_only_inputs_produce_year_only_output(
        self, start_year: int, delta_years: int
    ) -> None:
        end_year = start_year + delta_years
        assume(end_year <= 9999)
        locale = EnglishLocale()
        result = compute_time_span_string(
            start_year,
            end_year,
            locale=locale,
            current_date=Date(2025, 1, 1),
            time_span_template="HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
        )
        assert locale.month not in result
        assert locale.months not in result

    @settings(deadline=None)
    @given(
        start=valid_date_strings(),
        delta_days=st.integers(min_value=0, max_value=36500),
    )
    def test_non_negative_duration(self, start: str, delta_days: int) -> None:
        start_date = get_date_object(start)
        end_date = Date.fromordinal(
            min(start_date.toordinal() + delta_days, Date(9999, 12, 31).toordinal())
        )
        assume(end_date >= start_date)
        end_str = end_date.isoformat()
        locale = EnglishLocale()
        result = compute_time_span_string(
            start,
            end_str,
            locale=locale,
            current_date=Date(2025, 1, 1),
            time_span_template="HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
        )
        # Extract numeric parts: should all be non-negative
        numbers = re.findall(r"\d+", result)
        for n in numbers:
            assert int(n) >= 0

    @settings(deadline=None)
    @given(
        start_year=st.integers(min_value=1900, max_value=2050),
        delta_years=st.integers(min_value=1, max_value=50),
    )
    def test_singular_plural_correctness(
        self, start_year: int, delta_years: int
    ) -> None:
        end_year = start_year + delta_years
        assume(end_year <= 9999)
        locale = EnglishLocale()
        result = compute_time_span_string(
            start_year,
            end_year,
            locale=locale,
            current_date=Date(2025, 1, 1),
            time_span_template="HOW_MANY_YEARS YEARS",
        )
        if delta_years == 1:
            assert locale.year in result
            assert locale.years not in result
        elif delta_years > 1:
            assert locale.years in result


# ── Module 4: override_dictionary ────────────────────────────────────────────


class TestApplyOverridesProperties:
    @settings(deadline=None)
    @given(
        value=st.text(min_size=1, max_size=20),
    )
    def test_original_never_mutated(self, value: str) -> None:
        original = {"a": {"b": "old"}}
        frozen = copy.deepcopy(original)
        apply_overrides_to_dictionary(original, {"a.b": value})
        assert original == frozen

    @settings(deadline=None)
    @given(
        value=st.text(min_size=1, max_size=20),
    )
    def test_applied_value_retrievable(self, value: str) -> None:
        original = {"a": {"b": "old"}}
        result = apply_overrides_to_dictionary(original, {"a.b": value})
        assert result["a"]["b"] == value

    def test_empty_overrides_deep_copies(self) -> None:
        original = {"a": {"b": "c"}}
        result = apply_overrides_to_dictionary(original, {})
        assert result == original
        assert result is not original


class TestUpdateValueByLocationProperties:
    @settings(deadline=None)
    @given(
        items=st.lists(st.text(max_size=10), min_size=1, max_size=5),
    )
    def test_list_index_out_of_bounds_raises(self, items: list[str]) -> None:
        bad_index = len(items)
        with pytest.raises(RenderCVUserError):
            update_value_by_location(items, str(bad_index), "val", str(bad_index))

    @settings(deadline=None)
    @given(
        key=st.from_regex(r"[a-z]{2,8}", fullmatch=True),
    )
    def test_non_integer_key_for_list_raises(self, key: str) -> None:
        with pytest.raises(RenderCVUserError):
            update_value_by_location(["a", "b"], key, "val", key)

    @settings(deadline=None)
    @given(
        value=st.text(min_size=1, max_size=20),
    )
    def test_missing_dict_keys_auto_created(self, value: str) -> None:
        result = update_value_by_location({}, "a.b.c", value, "a.b.c")
        assert result["a"]["b"]["c"] == value


# ── Module 5: path_resolver ──────────────────────────────────────────────────


class TestBuildNameVariantsProperties:
    def test_none_returns_empty_dict(self) -> None:
        assert build_name_variants(None) == {}

    @settings(deadline=None)
    @given(name=st.text(min_size=1, max_size=50))
    def test_always_7_keys(self, name: str) -> None:
        result = build_name_variants(name)
        assert len(result) == 7

    @settings(deadline=None)
    @given(name=st.text(min_size=1, max_size=50))
    def test_snake_case_has_no_spaces(self, name: str) -> None:
        result = build_name_variants(name)
        assert " " not in result["NAME_IN_SNAKE_CASE"]
        assert " " not in result["NAME_IN_LOWER_SNAKE_CASE"]
        assert " " not in result["NAME_IN_UPPER_SNAKE_CASE"]

    @settings(deadline=None)
    @given(name=st.text(min_size=1, max_size=50))
    def test_kebab_case_has_no_spaces(self, name: str) -> None:
        result = build_name_variants(name)
        assert " " not in result["NAME_IN_KEBAB_CASE"]
        assert " " not in result["NAME_IN_LOWER_KEBAB_CASE"]
        assert " " not in result["NAME_IN_UPPER_KEBAB_CASE"]

    @settings(deadline=None)
    @given(name=st.text(min_size=1, max_size=50))
    def test_lower_variants_are_lowercase(self, name: str) -> None:
        result = build_name_variants(name)
        assert (
            result["NAME_IN_LOWER_SNAKE_CASE"]
            == result["NAME_IN_LOWER_SNAKE_CASE"].lower()
        )
        assert (
            result["NAME_IN_LOWER_KEBAB_CASE"]
            == result["NAME_IN_LOWER_KEBAB_CASE"].lower()
        )

    @settings(deadline=None)
    @given(name=st.text(min_size=1, max_size=50))
    def test_upper_variants_are_uppercase(self, name: str) -> None:
        result = build_name_variants(name)
        assert (
            result["NAME_IN_UPPER_SNAKE_CASE"]
            == result["NAME_IN_UPPER_SNAKE_CASE"].upper()
        )
        assert (
            result["NAME_IN_UPPER_KEBAB_CASE"]
            == result["NAME_IN_UPPER_KEBAB_CASE"].upper()
        )

    @settings(deadline=None)
    @given(name=st.text(min_size=1, max_size=50))
    def test_original_name_preserved(self, name: str) -> None:
        result = build_name_variants(name)
        assert result["NAME"] == name


class TestResolveOutputFolderPlaceholderProperties:
    @settings(deadline=None)
    @given(
        suffix=st.from_regex(r"[a-z_]{1,10}", fullmatch=True),
        folder=st.from_regex(r"[a-z_]{1,10}", fullmatch=True),
    )
    def test_idempotent(self, suffix: str, folder: str) -> None:
        path = pathlib.PurePosixPath(f"/base/OUTPUT_FOLDER/{suffix}")
        output_folder = pathlib.PurePosixPath(f"/base/{folder}")
        first = resolve_output_folder_placeholder(
            pathlib.Path(path), pathlib.Path(output_folder)
        )
        second = resolve_output_folder_placeholder(first, pathlib.Path(output_folder))
        assert first == second

    @settings(deadline=None)
    @given(
        suffix=st.from_regex(r"[a-z_]{1,10}", fullmatch=True),
        folder=st.from_regex(r"[a-z_]{1,10}", fullmatch=True),
    )
    def test_output_folder_absent_in_result(self, suffix: str, folder: str) -> None:
        path = pathlib.PurePosixPath(f"/base/OUTPUT_FOLDER/{suffix}")
        output_folder = pathlib.PurePosixPath(f"/base/{folder}")
        result = resolve_output_folder_placeholder(
            pathlib.Path(path), pathlib.Path(output_folder)
        )
        assert "OUTPUT_FOLDER" not in result.parts


# ── Module 6: Pydantic validators ───────────────────────────────────────────


class TestTypstDimensionProperties:
    @settings(deadline=None)
    @given(dim=typst_dimensions())
    def test_valid_dimensions_accepted(self, dim: str) -> None:
        assert validate_typst_dimension(dim) == dim

    @settings(deadline=None)
    @given(
        number=st.from_regex(r"-?\d+(\.\d+)?", fullmatch=True),
    )
    def test_missing_unit_rejected(self, number: str) -> None:
        with pytest.raises(pydantic_core.PydanticCustomError):
            validate_typst_dimension(number)

    @settings(deadline=None)
    @given(
        number=st.from_regex(r"\d+", fullmatch=True),
        unit=st.sampled_from(["px", "rem", "ex", "vh", "vw", "%"]),
    )
    def test_invalid_unit_rejected(self, number: str, unit: str) -> None:
        with pytest.raises(pydantic_core.PydanticCustomError):
            validate_typst_dimension(f"{number}{unit}")

    @settings(deadline=None)
    @given(
        number=st.integers(min_value=1, max_value=999),
        unit=st.sampled_from(["cm", "in", "pt", "mm", "em"]),
    )
    def test_negative_dimensions_allowed(self, number: int, unit: str) -> None:
        dim = f"-{number}{unit}"
        assert validate_typst_dimension(dim) == dim


class TestSocialNetworkUsernameProperties:
    @settings(deadline=None)
    @given(
        username=st.from_regex(
            r"@[a-zA-Z0-9_]{1,15}@[a-z]{2,10}\.[a-z]{2,4}", fullmatch=True
        )
    )
    def test_mastodon_valid_format_accepted(self, username: str) -> None:
        sn = SocialNetwork(network="Mastodon", username=username)
        assert sn.username == username

    @settings(deadline=None)
    @given(username=st.from_regex(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", fullmatch=True))
    def test_orcid_valid_format_accepted(self, username: str) -> None:
        sn = SocialNetwork(network="ORCID", username=username)
        assert sn.username == username

    @settings(deadline=None)
    @given(username=st.from_regex(r"\d{1,8}/[a-zA-Z0-9_-]+", fullmatch=True))
    def test_stackoverflow_valid_format_accepted(self, username: str) -> None:
        sn = SocialNetwork(network="StackOverflow", username=username)
        assert sn.username == username

    @settings(deadline=None)
    @given(username=st.from_regex(r"[a-zA-Z0-9_-]{3,23}", fullmatch=True))
    def test_reddit_valid_format_accepted(self, username: str) -> None:
        sn = SocialNetwork(network="Reddit", username=username)
        assert sn.username == username

    @settings(deadline=None)
    @given(
        network=st.sampled_from(["LinkedIn", "GitHub", "GitLab", "X"]),
        username=st.from_regex(r"[a-zA-Z0-9_-]{1,20}", fullmatch=True),
    )
    def test_valid_network_url_is_valid_http_url(
        self, network: str, username: str
    ) -> None:
        sn = SocialNetwork(network=network, username=username)
        pydantic.TypeAdapter(pydantic.HttpUrl).validate_strings(sn.url)
