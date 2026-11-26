"""The web backend must compile with the same Typst as the core.

Why this is worth a test of its own:
    The core asks for `typst>=0.14.8` with no upper bound, and the two
    lockfiles resolve independently. They drifted -- the root to 0.14.8,
    the backend to 0.15.0 -- and the symptom was a CV that `rendercv
    render` set on one page and the web editor set on two. Same YAML, same
    fonts, byte-identical Typst source; only the compiler differed, and
    0.15 breaks lines differently.

    Nothing else would have caught it. Every test on both sides passed,
    because each side is self-consistent. The defect only exists in the
    comparison, so the comparison is what has to be asserted.
"""

import importlib.metadata
import pathlib
import tomllib

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[3]
ROOT_LOCK = REPOSITORY_ROOT / "uv.lock"


def locked_version(lock_path: pathlib.Path, package: str) -> str:
    """Read one package's version out of a `uv.lock`.

    Args:
        lock_path: The lockfile to read.
        package: The package name to look for.

    Returns:
        The locked version.

    Raises:
        AssertionError: If the lockfile has no such package, which means
            this test is asserting something that no longer exists.
    """
    locked = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    for entry in locked.get("package", []):
        if entry.get("name") == package:
            return str(entry["version"])
    message = f"{package} is not in {lock_path}"
    raise AssertionError(message)


def test_the_backend_compiles_with_the_core_s_typst() -> None:
    # `web/backend/pyproject.toml` pins `typst` for exactly this reason;
    # the pin and this assertion have to be raised together, and raising
    # them means re-rendering the core's reference files.
    core_version = locked_version(ROOT_LOCK, "typst")
    installed = importlib.metadata.version("typst")

    assert installed == core_version, (
        f"The web backend renders with typst {installed} while the core's"
        f" lockfile pins {core_version}. A CV would paginate differently in"
        f" the editor than in `rendercv render`."
    )
