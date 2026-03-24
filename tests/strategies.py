"""Reusable Hypothesis strategies for RenderCV property-based tests."""

import calendar

from hypothesis import strategies as st


@st.composite
def valid_date_strings(draw: st.DrawFn) -> str:
    """Generate date strings in YYYY-MM-DD, YYYY-MM, or YYYY format."""
    year = draw(st.integers(min_value=1, max_value=9999))
    fmt = draw(st.sampled_from(["year", "year_month", "year_month_day"]))
    if fmt == "year":
        return f"{year:04d}"
    month = draw(st.integers(min_value=1, max_value=12))
    if fmt == "year_month":
        return f"{year:04d}-{month:02d}"
    max_day = calendar.monthrange(year, month)[1]
    day = draw(st.integers(min_value=1, max_value=max_day))
    return f"{year:04d}-{month:02d}-{day:02d}"


@st.composite
def date_inputs(draw: st.DrawFn) -> str | int:
    """Generate inputs accepted by get_date_object (excluding 'present')."""
    return draw(
        st.one_of(
            valid_date_strings(),
            st.integers(min_value=1, max_value=9999),
        )
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


@st.composite
def typst_dimensions(draw: st.DrawFn) -> str:
    """Generate valid Typst dimension strings."""
    sign = draw(st.sampled_from(["", "-"]))
    integer_part = draw(st.integers(min_value=0, max_value=999))
    has_decimal = draw(st.booleans())
    decimal_part = ""
    if has_decimal:
        decimal_part = "." + str(draw(st.integers(min_value=0, max_value=99)))
    unit = draw(st.sampled_from(["cm", "in", "pt", "mm", "em"]))
    return f"{sign}{integer_part}{decimal_part}{unit}"
