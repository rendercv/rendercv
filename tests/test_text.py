import itertools
import re

import pytest
from hypothesis import given
from hypothesis import strategies as st

from rendercv.text import (
    Segment,
    keyword_pattern,
    literal_alternation,
    partition,
    rewrite,
    substitute_placeholders,
)

words = st.lists(
    st.text(alphabet="ab_+ ", min_size=1, max_size=4), min_size=1, max_size=4
)


class TestPartition:
    def test_splits_string_into_matches_and_gaps(self):
        segments = list(partition("a1b22", re.finditer(r"\d+", "a1b22")))

        assert segments == [
            Segment(0, 1, matched=False),
            Segment(1, 2, matched=True),
            Segment(2, 3, matched=False),
            Segment(3, 5, matched=True),
        ]

    def test_returns_nothing_for_empty_string(self):
        assert list(partition("", re.finditer("a", ""))) == []

    @given(string=st.text(alphabet="ab_+ \n", max_size=30), keywords=words)
    def test_segments_cover_the_string_exactly_once_in_order(
        self, string: str, keywords: list[str]
    ) -> None:
        pattern = literal_alternation(frozenset(keywords))
        segments = list(partition(string, pattern.finditer(string)))

        assert "".join(string[s.start : s.end] for s in segments) == string
        assert all(s.start < s.end for s in segments)
        assert all(a.end == b.start for a, b in itertools.pairwise(segments))
        # Gaps are maximal: two gaps are never adjacent.
        assert not any(
            not a.matched and not b.matched for a, b in itertools.pairwise(segments)
        )


class TestRewrite:
    @pytest.mark.parametrize(
        ("string", "pattern", "expected"),
        [
            ("a1b22", r"\d+", "a<1>b<22>"),
            ("no digits", r"\d+", "no digits"),
            ("1", r"\d", "<1>"),
        ],
    )
    def test_transforms_matches(self, string, pattern, expected):
        result = rewrite(string, re.compile(pattern), lambda match: f"<{match}>")

        assert result == expected

    def test_transforms_gaps_independently(self):
        result = rewrite("a1b", re.compile(r"\d"), str, str.upper)

        assert result == "A1B"

    def test_never_rescans_replacements(self):
        result = rewrite(
            "AB", re.compile("A|B"), lambda match: "B" if match == "A" else "A"
        )

        assert result == "BA"

    @given(string=st.text(alphabet="ab_+ ", max_size=30), keywords=words)
    def test_identity_transformations_reconstruct_the_string(
        self, string: str, keywords: list[str]
    ) -> None:
        pattern = literal_alternation(frozenset(keywords))

        assert rewrite(string, pattern, str) == string


class TestLiteralAlternation:
    def test_prefers_the_longest_string(self):
        pattern = literal_alternation(frozenset({"NAME", "NAME_IN_SNAKE_CASE"}))

        assert pattern.findall("NAME_IN_SNAKE_CASE NAME") == [
            "NAME_IN_SNAKE_CASE",
            "NAME",
        ]

    def test_matches_special_characters_literally(self):
        pattern = literal_alternation(frozenset({"C++", "a.b"}))

        assert pattern.findall("C++ axb a.b C") == ["C++", "a.b"]


class TestKeywordPattern:
    @pytest.mark.parametrize(
        ("keywords", "text", "expected"),
        [
            ({"Python"}, "Python and Pythonic", ["Python"]),
            ({"Python"}, "CPython", []),
            ({"C++"}, "C++ and C", ["C++"]),
            ({"C++"}, "C++17", []),
            ({"C", "C++"}, "C++ and C", ["C++", "C"]),
            ({"Tech stack:"}, "Tech stack: Python", ["Tech stack:"]),
            ({"ML", "ML Ops"}, "ML Ops and ML", ["ML Ops", "ML"]),
            ({".NET"}, "ASP.NET and .NET", [".NET"]),
            ({"Node"}, "Node.js", ["Node"]),
        ],
    )
    def test_matches_whole_words(self, keywords, text, expected):
        assert keyword_pattern(frozenset(keywords)).findall(text) == expected


class TestSubstitutePlaceholders:
    @pytest.mark.parametrize(
        ("string", "placeholders", "expected"),
        [
            ("NAME_CV_YEAR.pdf", {"NAME": "B", "YEAR": "2025"}, "B_CV_2025.pdf"),
            (
                "NAME_IN_SNAKE_CASE_CV",
                {"NAME": "John Doe", "NAME_IN_SNAKE_CASE": "John_Doe"},
                "John_Doe_CV",
            ),
            ("No placeholders", {"NAME": "John"}, "No placeholders"),
            ("NAME", {}, "NAME"),
        ],
    )
    def test_replaces_placeholders(self, string, placeholders, expected):
        assert substitute_placeholders(string, placeholders) == expected

    def test_inserts_values_verbatim(self):
        result = substitute_placeholders("NAME YEAR", {"NAME": "YEAR", "YEAR": "2025"})

        assert result == "YEAR 2025"
