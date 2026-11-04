"""The documents a brand-new CV opens with.

All four are generated from the core's own sample rather than written out
here, so these assert on properties that must hold whatever the core
changes the sample to -- not on its exact text, which is the core's to
change and would make this suite fail for something that is not its
concern.

The shape they aim at was checked against rendercv.com on 2026-09-06: CV,
Design and Locale filled in, Settings holding only the three keys that mean
something in a browser.
"""

import pytest
import ruamel.yaml
from fastapi.testclient import TestClient
from rendercv_web.app import app
from rendercv_web.defaults import (
    CLI_ONLY_SETTINGS_KEY,
    MINIMAL_CV_YAML,
    MINIMAL_SETTINGS_YAML,
    default_cv_yaml,
    default_design_yaml,
    default_locale_yaml,
    default_settings_yaml,
    drop_subtree,
    top_level_block,
    uncomment,
)


def load_yaml(text: str) -> dict:
    """Parse a YAML document with the same library the core uses.

    Args:
        text: The document to parse.

    Returns:
        The parsed mapping.
    """
    return ruamel.yaml.YAML(typ="safe").load(text)


class TestTheStarterCv:
    """What someone sees the first time they open the editor."""

    def test_it_is_a_filled_in_cv_not_an_empty_one(self) -> None:
        # The failure this replaces: a new CV opened as three lines, a name
        # and an empty `sections` map, so the editor's whole point was
        # invisible and a beginner had to know the schema before typing.
        document = load_yaml(default_cv_yaml())

        assert set(document) == {"cv"}
        assert document["cv"]["sections"], "the starter CV has no sections"
        assert len(default_cv_yaml().splitlines()) > 50

    def test_it_shows_several_entry_types(self) -> None:
        sections = load_yaml(default_cv_yaml())["cv"]["sections"]

        assert len(sections) >= 3

    def test_it_carries_no_schema_hint_comment(self) -> None:
        # `# yaml-language-server: $schema=...` drives IDE autocompletion,
        # does nothing in a browser, and pins a version tag that goes stale.
        assert "yaml-language-server" not in default_cv_yaml()

    def test_the_sample_still_has_a_cv_block(self) -> None:
        # If the core restructures its sample, the fallback keeps "create
        # CV" working -- but silently, so this is what would say so.
        assert default_cv_yaml() != MINIMAL_CV_YAML


class TestDesignAndLocaleAreLiveNotCommented:
    """The distinction that makes these panes worth filling at all."""

    @pytest.mark.parametrize(
        ("builder", "key"),
        [(default_design_yaml, "design"), (default_locale_yaml, "locale")],
    )
    def test_every_option_is_a_real_value(self, builder, key: str) -> None:
        # The generator emits these blocks as one live key and ~130
        # commented-out options, which is right for a file opened in a text
        # editor and wrong for a pane with a form beside it. rendercv.com
        # shows them live; a commented block would look much like an empty
        # one at a glance, and could not be edited without first noticing
        # the `#`.
        text = builder()

        assert text, f"the {key} document is empty"
        assert not any(line.lstrip().startswith("#") for line in text.splitlines())

    def test_design_carries_the_options_a_user_would_reach_for(self) -> None:
        document = load_yaml(default_design_yaml())["design"]

        assert document["theme"]
        for section in ("page", "colors", "typography"):
            assert section in document, f"design is missing {section}"

    def test_locale_carries_the_translatable_strings(self) -> None:
        document = load_yaml(default_locale_yaml())["locale"]

        assert document["language"]
        assert len(document["month_abbreviations"]) == 12


class TestSettingsHoldsOnlyWhatABrowserUses:
    """The one block that is filtered rather than merely uncommented."""

    def test_the_command_line_options_are_gone(self) -> None:
        # `output_folder`, `typst_path`, `dont_generate_pdf` and the rest
        # configure the `rendercv` CLI. Seeding them would describe a
        # program the user is not running. rendercv.com omits them too.
        text = default_settings_yaml()

        assert CLI_ONLY_SETTINGS_KEY not in text
        for cli_only in ("output_folder", "typst_path", "png_path", "dont_generate"):
            assert cli_only not in text

    def test_what_remains_is_what_the_editor_can_act_on(self) -> None:
        document = load_yaml(default_settings_yaml())["settings"]

        assert set(document) == {"current_date", "bold_keywords", "pdf_title"}

    def test_the_sample_still_has_a_settings_block(self) -> None:
        assert default_settings_yaml() != MINIMAL_SETTINGS_YAML


class TestAllFourAreUsable:
    """The strongest property: they have to work, not merely parse."""

    def test_they_validate_against_the_real_schema(self) -> None:
        # A starter document that fails validation would greet every new
        # user with red error markers on content they did not write. The
        # generator is the core's, so this also catches the core changing
        # its sample into something the schema endpoint rejects.
        client = TestClient(app)

        response = client.post(
            "/api/validate",
            json={
                "cv_yaml": default_cv_yaml(),
                "design_yaml": default_design_yaml(),
                "locale_yaml": default_locale_yaml(),
                "settings_yaml": default_settings_yaml(),
            },
        )

        assert response.status_code == 200
        # A valid document answers `{"valid": true}` with no `errors` key at
        # all, so asserting on `errors` alone would pass on a shape change
        # that dropped the flag.
        assert response.json() == {"valid": True}

    def test_each_document_ends_in_exactly_one_newline(self) -> None:
        # They go straight into editor panes, where a missing trailing
        # newline shows as a cursor that cannot reach the last line.
        for builder in (
            default_cv_yaml,
            default_design_yaml,
            default_locale_yaml,
            default_settings_yaml,
        ):
            text = builder()
            assert text.endswith("\n")
            assert not text.endswith("\n\n")

    def test_building_them_twice_gives_the_same_objects(self) -> None:
        # Cached deliberately: the sample costs ~70 ms to generate and
        # cannot change within a process, so `POST /api/cvs` should not pay
        # for it on every call.
        assert default_cv_yaml() is default_cv_yaml()
        assert default_design_yaml() is default_design_yaml()


class TestSplittingTheSample:
    """The three helpers that turn one document into four."""

    def test_a_block_stops_at_the_next_top_level_key(self) -> None:
        sample = "cv:\n  name: A\ndesign:\n  theme: classic\n"

        assert top_level_block(sample, "cv") == ["cv:", "  name: A"]

    def test_a_block_running_to_the_end_is_kept_whole(self) -> None:
        sample = "cv:\n  name: A\n  sections: {}\n"

        assert len(top_level_block(sample, "cv")) == 3

    @pytest.mark.parametrize("key", ["cv", "design", "nonexistent"])
    def test_a_missing_key_yields_nothing(self, key: str) -> None:
        assert top_level_block("# only a comment\n", key) == []

    def test_uncomment_preserves_indentation(self) -> None:
        assert uncomment(["  # page:", "  #   size: a4"]) == ["  page:", "    size: a4"]

    def test_uncomment_leaves_a_hash_inside_a_value_alone(self) -> None:
        # The marker is only ever at the start of a line; a `#` in a value
        # is part of the value.
        assert uncomment(["  color: '#ff0000'"]) == ["  color: '#ff0000'"]

    def test_dropping_a_subtree_takes_its_children_with_it(self) -> None:
        lines = [
            "settings:",
            "  current_date: today",
            "  render_command:",
            "    output_folder: out",
            "    dont_generate_pdf: false",
            "  pdf_title: NAME - CV",
        ]

        assert drop_subtree(lines, "render_command") == [
            "settings:",
            "  current_date: today",
            "  pdf_title: NAME - CV",
        ]

    def test_dropping_a_subtree_that_runs_to_the_end(self) -> None:
        lines = ["settings:", "  render_command:", "    output_folder: out"]

        assert drop_subtree(lines, "render_command") == ["settings:"]

    def test_dropping_a_key_that_is_not_there_changes_nothing(self) -> None:
        lines = ["settings:", "  pdf_title: NAME - CV"]

        assert drop_subtree(lines, "render_command") == lines
