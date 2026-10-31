import importlib
import importlib.metadata
import warnings

import rendercv


def test_import_preserves_host_pydantic_warnings() -> None:
    """Importing RenderCV must not silence a host application's warnings."""
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        importlib.reload(rendercv)
        warnings.warn_explicit(
            "Host warning", UserWarning, "pydantic/host.py", 1, module="pydantic.host"
        )
    assert [str(warning.message) for warning in captured] == ["Host warning"]


def test_version_matches_distribution() -> None:
    assert rendercv.__version__ == importlib.metadata.version("rendercv")
