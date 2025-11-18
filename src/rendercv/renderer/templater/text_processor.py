import re


def make_keywords_bold(string: str, keywords: list[str]) -> str:
    """Make the given keywords bold in the given string, handling capitalization and substring issues.

    Examples:
        >>> make_keywords_bold("I know java and javascript", ["java"])
        'I know **java** and javascript'

        >>> make_keywords_bold("Experience with aws, Aws and AWS", ["aws"])
        'Experience with **aws**, **Aws** and **AWS**'
    """

    def bold_match(match):
        return f"**{match.group(0)}**"

    for keyword in keywords:
        # Use re.escape to ensure special characters in keywords are handled
        pattern = r"\b" + re.escape(keyword) + r"\b"
        string = re.sub(pattern, bold_match, string, flags=re.IGNORECASE)

    return string
