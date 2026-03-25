import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from rendercv.exception import RenderCVInternalError
from rendercv.renderer.templater.string_processor import (
    build_keyword_matcher_pattern,
    clean_url,
    make_keywords_bold,
    substitute_placeholders,
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


class TestMakeKeywordsBold:
    @pytest.mark.parametrize(
        ("text", "keywords", "expected"),
        [
            (
                "This is a test string with some keywords.",
                ["test", "keywords"],
                "This is a **test** string with some **keywords**.",
            ),
            ("No matches here.", ["test", "keywords"], "No matches here."),
            ("Python and python", ["Python"], "**Python** and python"),
            ("", ["test"], ""),
            ("Test word", [], "Test word"),
            ("I can read well", ["re"], "I can read well"),
            # Issue #706: keywords with non-word boundary characters
            (
                "Tech stack: Python, Java",
                ["Tech stack:"],
                "**Tech stack:** Python, Java",
            ),
            ("Use C++ and C#", ["C++", "C#"], "Use **C++** and **C#**"),
        ],
    )
    def test_returns_expected_output(self, text, keywords, expected):
        assert make_keywords_bold(text, keywords) == expected

    @settings(deadline=None)
    @given(text=st.text(max_size=100))
    def test_empty_keywords_is_identity(self, text: str) -> None:
        assert make_keywords_bold(text, []) == text

    @settings(deadline=None)
    @given(text=st.text(max_size=100), keywords=keyword_lists)
    def test_never_produces_double_bolding(
        self, text: str, keywords: list[str]
    ) -> None:
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
    def test_is_case_sensitive(self, keyword: str) -> None:
        text = f"before {keyword.lower()} after"
        result = make_keywords_bold(text, [keyword])
        assert f"**{keyword.lower()}**" not in result

    @settings(deadline=None)
    @given(
        keyword=st.text(min_size=1, max_size=20).filter(lambda s: s.strip()),
    )
    def test_keyword_in_text_always_gets_bolded(self, keyword: str) -> None:
        text = f"before {keyword} after"
        result = make_keywords_bold(text, [keyword])
        assert f"**{keyword}**" in result


class TestSubstitutePlaceholders:
    @pytest.mark.parametrize(
        ("string", "placeholders", "expected_string"),
        [
            ("Hello, NAME!", {"NAME": "World"}, "Hello, World!"),
            ("Hello, NAME!", {"NAME": None}, "Hello, !"),
            ("No placeholders here.", {}, "No placeholders here."),
        ],
    )
    def test_returns_expected_output(self, string, placeholders, expected_string):
        assert substitute_placeholders(string, placeholders) == expected_string

    @settings(deadline=None)
    @given(text=st.text(max_size=100))
    def test_empty_placeholders_preserves_content(self, text: str) -> None:
        assert substitute_placeholders(text, {}) == text

    @settings(deadline=None)
    @given(placeholders=placeholder_dicts())  # ty: ignore[missing-argument]
    def test_all_keys_absent_from_output(self, placeholders: dict[str, str]) -> None:
        assume(placeholders)
        keys = set(placeholders.keys())
        assume(not any(k in v for k in keys for v in placeholders.values()))

        template = " ".join(placeholders.keys())
        result = substitute_placeholders(template, placeholders)
        for key in placeholders:
            assert key not in result


class TestCleanUrl:
    @pytest.mark.parametrize(
        ("url", "expected_clean_url"),
        [
            ("https://example.com", "example.com"),
            ("https://example.com/", "example.com"),
            ("https://example.com/test", "example.com/test"),
            ("https://example.com/test/", "example.com/test"),
            ("https://www.example.com/test/", "www.example.com/test"),
        ],
    )
    def test_returns_expected_output(self, url, expected_clean_url):
        assert clean_url(url) == expected_clean_url

    @settings(deadline=None)
    @given(url=urls())  # ty: ignore[missing-argument]
    def test_is_idempotent(self, url: str) -> None:
        assert clean_url(clean_url(url)) == clean_url(url)

    @settings(deadline=None)
    @given(url=urls())  # ty: ignore[missing-argument]
    def test_removes_protocol(self, url: str) -> None:
        result = clean_url(url)
        assert "https://" not in result
        assert "http://" not in result

    @settings(deadline=None)
    @given(url=urls())  # ty: ignore[missing-argument]
    def test_removes_trailing_slashes(self, url: str) -> None:
        result = clean_url(url)
        if result:
            assert not result.endswith("/")


class TestBuildKeywordMatcherPattern:
    def test_raises_error_for_empty_keywords(self):
        with pytest.raises(RenderCVInternalError) as exc_info:
            build_keyword_matcher_pattern(frozenset())

        assert "Keywords cannot be empty" in str(exc_info.value)

    @settings(deadline=None)
    @given(
        keywords=st.frozensets(
            st.text(min_size=1, max_size=20).filter(lambda s: s.strip()),
            min_size=1,
            max_size=10,
        )
    )
    def test_matches_all_input_keywords(self, keywords: frozenset[str]) -> None:
        pattern = build_keyword_matcher_pattern(keywords)
        for keyword in keywords:
            assert pattern.search(keyword) is not None
        build_keyword_matcher_pattern.cache_clear()

    @settings(deadline=None)
    @given(
        base=st.from_regex(r"[a-zA-Z]{3,8}", fullmatch=True),
        extension=st.from_regex(r"[a-zA-Z]{1,5}", fullmatch=True),
    )
    def test_matches_longest_keyword_first(self, base: str, extension: str) -> None:
        short = base
        long = base + extension
        pattern = build_keyword_matcher_pattern(frozenset({short, long}))
        match = pattern.search(long)
        assert match is not None
        assert match.group(0) == long
        build_keyword_matcher_pattern.cache_clear()
