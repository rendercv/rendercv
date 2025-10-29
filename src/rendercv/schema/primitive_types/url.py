import pydantic

# Create a URL validator:
url_validator = pydantic.TypeAdapter(pydantic.HttpUrl)


def validate_url(url: str) -> str:
    """Validate a URL.

    Args:
        url: The URL to validate.

    Returns:
        The validated URL.
    """
    url_validator.validate_strings(url)
    return url
