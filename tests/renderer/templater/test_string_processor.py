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
from tests.strategies import keyword_lists, placeholder_dicts, urls


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
    @given(placeholders=placeholder_dicts())
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
    @given(url=urls())
    def test_is_idempotent(self, url: str) -> None:
        assert clean_url(clean_url(url)) == clean_url(url)

    @settings(deadline=None)
    @given(url=urls())
    def test_removes_protocol(self, url: str) -> None:
        result = clean_url(url)
        assert "https://" not in result
        assert "http://" not in result

    @settings(deadline=None)
    @given(url=urls())
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
