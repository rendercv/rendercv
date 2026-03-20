import pytest

from rendercv.renderer.templater.plural_rules import (
    default_plural_rule,
    get_plural_category,
    polish_plural_rule,
)


class TestPolishPluralRule:
    @pytest.mark.parametrize(
        ("count", "expected"),
        [
            (1, "one"),
            # "few" — ends in 2, 3, 4 (except 12, 13, 14)
            (2, "few"),
            (3, "few"),
            (4, "few"),
            (22, "few"),
            (23, "few"),
            (24, "few"),
            (102, "few"),
            (103, "few"),
            # "many" — ends in 0, 1, 5-9, or 12-14
            (0, "many"),
            (5, "many"),
            (6, "many"),
            (10, "many"),
            (11, "many"),
            (12, "many"),
            (13, "many"),
            (14, "many"),
            (15, "many"),
            (20, "many"),
            (21, "many"),
            (25, "many"),
            (100, "many"),
            (111, "many"),
            (112, "many"),
            (113, "many"),
            (114, "many"),
        ],
    )
    def test_returns_correct_category(self, count, expected):
        assert polish_plural_rule(count) == expected


class TestDefaultPluralRule:
    @pytest.mark.parametrize(
        ("count", "expected"),
        [
            (0, "other"),
            (1, "one"),
            (2, "other"),
            (5, "other"),
            (100, "other"),
        ],
    )
    def test_returns_correct_category(self, count, expected):
        assert default_plural_rule(count) == expected


class TestGetPluralCategory:
    def test_uses_polish_rule_for_pl(self):
        assert get_plural_category(2, "pl") == "few"
        assert get_plural_category(5, "pl") == "many"
        assert get_plural_category(1, "pl") == "one"

    def test_uses_default_rule_for_unknown_language(self):
        assert get_plural_category(1, "xx") == "one"
        assert get_plural_category(2, "xx") == "other"

    def test_uses_default_rule_for_english(self):
        assert get_plural_category(1, "en") == "one"
        assert get_plural_category(5, "en") == "other"
