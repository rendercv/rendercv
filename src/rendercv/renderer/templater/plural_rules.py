# https://www.unicode.org/cldr/charts/48/supplemental/language_plural_rules.html


def polish_rule(count: int) -> str:
    if count == 1:
        return "one"
    if 2 <= count % 10 <= 4 and not (12 <= count % 100 <= 14):
        return "few"
    return "many"


# Registry mapping ISO codes to rule functions
PLURAL_RULES = {
    "pl": polish_rule,
    # add here new set of rules
}


def default_rule(n: int) -> str:
    """Fallback rule for simple singular/plural languages."""
    return "one" if n == 1 else "other"


def get_plural_rules(count: int, language_code: str):
    """Determine the appropriate CLDR (Unicode Common Locale Data Repository) plural category
    for a given count and language code.

    Why:
        This function returns the grammatical plural category that should be used for a specific number in a given language. Different languages have different plural rules - for example, English has two forms (singular/plural), while Polish has three, and Arabic has six.

    Example:
        ```py
        >>> get_plural_rules(1, "en")
        'one'
        >>> get_plural_rules(5, "en")
        'other'
        ```

    Args:
        count (int): The number for which to determine the plural category.
        language_code (str): The ISO language code (e.g., 'en', 'pl', 'ar') identifying
            which language's plural rules to apply.

    Returns:
        str: The CLDR plural category, typically one of: 'zero', 'one', 'two', 'few', 'many', or 'other'.
            The exact categories available depend on the language's plural rules.

    Note:
        - This function relies on a PLURAL_RULES dictionary that maps language codes to their
          respective plural rule functions.
        - If the language_code is not found in PLURAL_RULES, a default_rule function is used
          as a fallback.
        - CLDR plural categories are used for proper localization and internationalization (i18n) of text that contains numbers.

    """
    rule = PLURAL_RULES.get(language_code, default_rule)
    return rule(count)
