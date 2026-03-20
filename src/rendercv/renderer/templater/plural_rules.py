"""CLDR plural category resolution for localized time span labels.

Why:
    Languages like Polish have three plural forms (one/few/many) instead of
    English's two (one/other). This module maps counts to CLDR plural
    categories so time span strings use grammatically correct labels.

See: https://www.unicode.org/cldr/charts/48/supplemental/language_plural_rules.html
"""

from collections.abc import Callable

type PluralRule = Callable[[int], str]


def polish_plural_rule(count: int) -> str:
    """Return CLDR plural category for Polish.

    Args:
        count: The number to categorize.

    Returns:
        CLDR category: "one", "few", or "many".
    """
    if count == 1:
        return "one"
    if 2 <= count % 10 <= 4 and not (12 <= count % 100 <= 14):
        return "few"
    return "many"


def default_plural_rule(count: int) -> str:
    """Return CLDR plural category for simple singular/plural languages.

    Args:
        count: The number to categorize.

    Returns:
        CLDR category: "one" or "other".
    """
    return "one" if count == 1 else "other"


PLURAL_RULES: dict[str, PluralRule] = {
    "pl": polish_plural_rule,
}


def get_plural_category(count: int, language_code: str) -> str:
    """Return the CLDR plural category for a count in the given language.

    Why:
        Different languages have different plural rules — English has two forms
        (singular/plural), Polish has three, Arabic has six. This function
        selects the right rule set and returns the grammatical category needed
        to pick the correct localized label.

    Example:
        ```py
        >>> get_plural_category(1, "en")
        'one'
        >>> get_plural_category(5, "pl")
        'many'
        >>> get_plural_category(3, "pl")
        'few'
        ```

    Args:
        count: The number for which to determine the plural category.
        language_code: ISO 639-1 language code (e.g., "en", "pl").

    Returns:
        CLDR plural category: "one", "two", "few", "many", or "other".
    """
    rule = PLURAL_RULES.get(language_code, default_plural_rule)
    return rule(count)
