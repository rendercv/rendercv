import pytest
from hypothesis import given
from hypothesis import strategies as st

from rendercv.renderer.templater.markup import (
    Break,
    Emph,
    Node,
    Placeholder,
    Raw,
    Strong,
    Summary,
    Text,
    emit,
    normalize,
    parse_content,
)
from rendercv.renderer.templater.template import (
    Group,
    compile_template,
    fill_template,
    flatten,
    group_brackets,
    is_blank,
    placeholder_pattern,
    remove_missing,
    remove_words,
    split_lines,
    strip_line,
)

entry_names = frozenset(
    {
        "NAME",
        "LOCATION",
        "DATE",
        "START_DATE",
        "END_DATE",
        "INSTITUTION",
        "DEGREE",
        "AREA",
        "URL",
        "JOURNAL",
        "SUMMARY",
        "HIGHLIGHTS",
    }
)

composed_values = st.lists(
    st.sampled_from(
        [
            "NAME",
            "LOCATION",
            "NASA",
            "**C++**&#49;7",
            "*italic*",
            "`NAME`",
            "``a`b``",
            "[NAME](https://example.com/a(b))",
            r"\*literal\*",
            "#emph[NAME]",
            "$$x^2$$",
            "\nsecond line",
            "\n- first\n  - nested",
            "中文",
            "&amp;",
            "(missing?)",
            " | ",
            "_identifier_",
        ]
    ),
    max_size=8,
).map(lambda fragments: parse_content("start " + " ".join(fragments) + " end"))


def fill(source: str, values: dict[str, str], **kwargs) -> str:
    """Fill an entry-like template with string values and emit it as Markdown."""
    template = compile_template(
        source, entry_names | frozenset(values), open_vocabulary=True, **kwargs
    )
    contents = {name: parse_content(value) for name, value in values.items()}
    return emit(fill_template(template, contents, "markdown"), "markdown")


class TestPlaceholderPattern:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("NAME_IN_SNAKE_CASE_CV", ["NAME_IN_SNAKE_CASE"]),
            ("DAYth", ["DAY"]),
            ("בAREA", ["AREA"]),
            ("UNNAMED NAME", ["NAME"]),
            ("NAMES", []),
            ("name", []),
            ("NAME_CV_DAY", ["NAME", "DAY"]),
        ],
    )
    def test_finds_known_names_at_the_start_of_words(self, text, expected):
        names = frozenset({"NAME", "NAME_IN_SNAKE_CASE", "DAY", "AREA"})
        pattern = placeholder_pattern(names, open_vocabulary=False)

        assert pattern.findall(text) == expected

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("ADVISOR and NAME", ["ADVISOR", "NAME"]),
            # An arbitrary key that ends with a known name is still one key:
            ("CO_NAME", ["CO_NAME"]),
            ("A NASA mission", ["NASA"]),
            ("Mixed Case", []),
            ("I", []),
        ],
    )
    def test_finds_unknown_uppercase_words_with_open_vocabulary(self, text, expected):
        pattern = placeholder_pattern(frozenset({"NAME"}), open_vocabulary=True)

        assert pattern.findall(text) == expected

    def test_matches_nothing_without_names(self):
        pattern = placeholder_pattern(frozenset(), open_vocabulary=False)

        assert pattern.findall("NAME") == []


class TestCompileTemplate:
    def test_turns_placeholders_into_nodes(self):
        template = compile_template(
            "**NAME**, LOCATION", frozenset({"NAME", "LOCATION"})
        )

        assert template.nodes == (
            Strong((Placeholder("NAME"),)),
            Text(", "),
            Placeholder("LOCATION"),
        )

    def test_splices_phrases(self):
        template = compile_template(
            "*DEGREE_WITH_AREA*",
            frozenset({"DEGREE", "AREA"}),
            phrases={"DEGREE_WITH_AREA": "DEGREE in AREA"},
        )

        assert template.nodes == (
            Emph((Placeholder("DEGREE"), Text(" in "), Placeholder("AREA"))),
        )

    def test_keeps_typst_code(self):
        template = compile_template("#h(1fr) NAME", frozenset({"NAME"}))

        assert template.nodes == (Raw("#h(1fr)"), Text(" "), Placeholder("NAME"))


class TestFillTemplate:
    @given(value=composed_values)
    def test_substitution_does_not_reinterpret_composed_values(self, value):
        template = compile_template("NAME (LOCATION)", entry_names)
        for target in ("markdown", "typst"):
            assert fill_template(template, {"NAME": value}, target) == value

    @given(
        values=st.dictionaries(
            st.sampled_from(["NAME", "LOCATION", "DATE"]), composed_values
        )
    )
    def test_missing_fields_do_not_change_other_values(self, values):
        template = compile_template("**NAME** | *LOCATION* | DATE", entry_names)
        expected: list[Node] = []
        for name, wrapper in [("NAME", Strong), ("LOCATION", Emph), ("DATE", None)]:
            if name not in values:
                continue
            if expected:
                expected.append(Text(" | "))
            if wrapper:
                expected.append(wrapper(values[name]))
            else:
                expected.extend(values[name])
        for target in ("markdown", "typst"):
            assert fill_template(template, values, target) == normalize(expected)

    @pytest.mark.parametrize(
        ("source", "values", "expected"),
        [
            ("NAME - LOCATION", {"NAME": "John", "LOCATION": "NYC"}, "John - NYC"),
            ("NAME - LOCATION", {"NAME": "John"}, "John"),
            ("LOCATION - NAME", {"NAME": "John"}, "John"),
            ("NAME (LOCATION)", {"NAME": "John"}, "John"),
            ("NAME, LOCATION, DATE", {"NAME": "John"}, "John"),
            ("NAME | LOCATION | DATE", {"NAME": "John", "DATE": "2024"}, "John | 2024"),
            ("NAME LOCATION DATE", {"NAME": "John", "DATE": "2024"}, "John 2024"),
            ("NAME LOCATION DATE", {}, ""),
            (
                "NAME Location DATE",
                {"NAME": "John", "DATE": "2024"},
                "John Location 2024",
            ),
            ("Just plain text", {"NAME": "John"}, "Just plain text"),
            ("", {"NAME": "John"}, ""),
            ("**NAME** - [LOCATION] (DATE)", {"NAME": "John"}, "**John**"),
            (
                "NAME (ADVISOR) | START_DATE",
                {"NAME": "J", "START_DATE": "2020"},
                "J | 2020",
            ),
            (
                "**POSITION** at COMPANY (LOCATION)",
                {"POSITION": "Engineer"},
                "**Engineer**",
            ),
            (
                "**INSTITUTION**, DEGREE in AREA -- LOCATION",
                {"INSTITUTION": "MIT", "AREA": "CS"},
                "**MIT**, CS",
            ),
            (
                "**INSTITUTION**, DEGREE in AREA -- LOCATION",
                {"AREA": "CS", "LOCATION": "Boston"},
                "CS -- Boston",
            ),
            ("*DEGREE in AREA*", {"AREA": "CS"}, "*CS*"),
            ("URL (JOURNAL)", {"URL": "x.com"}, "x.com"),
            ("URL (JOURNAL)", {"JOURNAL": "Nature"}, "(Nature)"),
            ("(URL JOURNAL)", {"JOURNAL": "Nature"}, "(Nature)"),
            ("DAYth of MONTH", {"DAY": "5", "MONTH": "May"}, "5th of May"),
            ("NAME\nLOCATION\nDATE", {"NAME": "J", "DATE": "2024"}, "J\n2024"),
            ("NAME", {"NAME": "   "}, ""),
        ],
    )
    def test_removes_missing_placeholders_with_what_only_existed_for_them(
        self, source, values, expected
    ):
        assert fill(source, values) == expected

    def test_never_parses_values(self):
        assert (
            fill("NAME", {"NAME": "LOCATION *not italic*"}) == "LOCATION *not italic*"
        )

    def test_splices_phrases_into_the_removal(self):
        phrases = {"DEGREE_WITH_AREA": "DEGREE en AREA"}

        assert fill("*DEGREE_WITH_AREA*", {"AREA": "CS"}, phrases=phrases) == "*CS*"
        assert (
            fill("*DEGREE_WITH_AREA*", {"DEGREE": "BS", "AREA": "CS"}, phrases=phrases)
            == "*BS en CS*"
        )

    def test_turns_a_line_with_only_summary_into_a_summary(self):
        template = compile_template("NAME\nSUMMARY", frozenset({"NAME", "SUMMARY"}))
        values = {"NAME": parse_content("X"), "SUMMARY": parse_content("a\nb")}

        assert fill_template(template, values, "typst") == (
            Text("X"),
            Break(),
            Summary((Text("a"), Break(), Text("b"))),
        )

    def test_fills_placeholders_inside_typst_code(self):
        template = compile_template(
            "#text(fill: red)[NAME] LOCATION", frozenset({"NAME", "LOCATION"})
        )
        values = {"NAME": parse_content("**J**")}

        assert fill_template(template, values, "typst") == (
            Raw("#text(fill: red)[#strong[J]]"),
        )

    def test_removes_typst_code_whose_placeholders_are_all_missing(self):
        template = compile_template(
            "NAME #text(fill: red)[LOCATION]", frozenset({"NAME", "LOCATION"})
        )

        assert fill_template(template, {"NAME": (Text("J"),)}, "typst") == (Text("J"),)

    @given(
        present=st.lists(
            st.sampled_from(["NAME", "LOCATION", "DATE"]), unique=True, min_size=1
        )
    )
    def test_never_changes_templates_without_missing_placeholders(self, present):
        source = " -- ".join(present)
        values = {name: f"value of {name.lower()}" for name in present}

        assert fill(source, values) == " -- ".join(values.values())


class TestSplitLines:
    def test_splits_at_top_level_breaks(self):
        nodes = (Text("a"), Break(), Strong((Text("b"),)))

        assert split_lines(nodes) == [(Text("a"),), (Strong((Text("b"),)),)]


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ((Text("  a "),), (Text("a"),)),
        ((Text(" "), Strong((Text("a"),)), Text(" ")), (Strong((Text("a"),)),)),
        ((), ()),
    ],
)
def test_strip_line(line, expected):
    assert strip_line(line) == expected


@pytest.mark.parametrize(
    ("nodes", "expected"),
    [
        ((), True),
        ((Text("  "),), True),
        ((Text(" a"),), False),
        ((Raw("#h(1fr)"),), False),
    ],
)
def test_is_blank(nodes, expected):
    assert is_blank(nodes) == expected


class TestGroupBrackets:
    def test_groups_balanced_brackets(self):
        nodes = (Text("a (b [c] d) e"),)

        assert group_brackets(nodes) == [
            Text("a "),
            Group("(", (Text("b "), Group("[", (Text("c"),), "]"), Text(" d")), ")"),
            Text(" e"),
        ]

    def test_keeps_unbalanced_brackets_as_text(self):
        assert flatten(group_brackets((Text("a (b"),))) == (Text("a (b"),)

    def test_groups_brackets_around_other_nodes(self):
        nodes = (Text("("), Placeholder("JOURNAL"), Text(")"))

        assert group_brackets(nodes) == [Group("(", (Placeholder("JOURNAL"),), ")")]


@pytest.mark.parametrize(
    ("separator", "expected"),
    [
        (" in ", ""),
        (", ", ", "),
        (" -- ", " -- "),
        (" at ", ""),
        (" en ", ""),
        (" | ", " | "),
        (" 2 ", " 2 "),
    ],
)
def test_remove_words(separator, expected):
    assert remove_words(separator) == expected


class TestRemoveMissing:
    def test_returns_content_without_missing_placeholders_unchanged(self):
        nodes = (Placeholder("A"), Text(" and "), Placeholder("B"))

        assert (
            remove_missing(
                nodes,
                lambda name: name in {"A", "B"},
                placeholder_pattern(frozenset({"A", "B"}), open_vocabulary=False),
            )
            == nodes
        )

    def test_returns_none_when_only_missing_placeholders_remain(self):
        nodes = (Text("("), Placeholder("A"), Text(")"))

        assert (
            remove_missing(
                nodes,
                lambda name: name != "A",
                placeholder_pattern(frozenset({"A"}), open_vocabulary=False),
            )
            is None
        )


def test_flatten():
    items = [Text("a"), Group("(", (Text("b"),), ")")]

    assert flatten(items) == (Text("a(b)"),)
