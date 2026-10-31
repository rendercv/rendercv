"""Test that rendercv works from a wheel in a non-networked environment."""

import os
import pathlib
import subprocess
import sys

import typst

PROJECT_ROOT = pathlib.Path(__file__).parent.parent

# Environment that poisons all HTTP/HTTPS so any network call fails immediately.
OFFLINE_ENV = {
    **os.environ,
    "http_proxy": "http://0.0.0.0:1",
    "https_proxy": "http://0.0.0.0:1",
    "no_proxy": "",
    # Prevent UnicodeEncodeError on Windows where the default console encoding
    # (cp1252) cannot handle Unicode characters like ✓ used by rich output.
    "PYTHONIOENCODING": "utf-8",
}


def run(args: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    """Run a subprocess with sensible defaults."""
    result = subprocess.run(
        args, capture_output=True, encoding="utf-8", timeout=120, check=False, **kwargs
    )
    if result.returncode != 0:
        message = (
            f"Command {args} failed with exit code {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
        raise AssertionError(message)
    return result


def test_rendercv_renders_pdf_offline(tmp_path: pathlib.Path) -> None:
    """Build wheel, install in isolated venv, render PDF without network."""
    # Prepare the same build inputs as release.yaml. This test must also work
    # alone in a fresh checkout, before the icon-coverage test downloads packages.
    renderer = PROJECT_ROOT / "src" / "rendercv" / "renderer"
    typst.compile(
        renderer / "rendercv_typst" / "lib.typ",
        package_cache_path=renderer / "typst_packages",
    )
    dist_dir = tmp_path / "dist"
    run(
        ["uv", "build", "--all-packages", "--wheel", "--out-dir", str(dist_dir)],
        cwd=PROJECT_ROOT,
    )

    wheel = next(dist_dir.glob("rendercv-*.whl"))
    fonts_wheel = next(dist_dir.glob("rendercv_fonts-*.whl"))
    venv_dir = tmp_path / "venv"
    if sys.platform == "win32":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python"

    run(["uv", "venv", str(venv_dir), "--python", sys.executable])
    run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(venv_python),
            f"{wheel}[full]",
            str(fonts_wheel),
        ]
    )

    (tmp_path / "cv.yaml").write_text(
        "cv:\n"
        "  name: Test\n"
        "  email: test@example.com\n"
        "  custom_connections:\n"
        "    - placeholder: Codeberg\n"
        "      url: https://codeberg.org/rendercv\n"
        "      fontawesome_icon: codeberg\n"
        "  sections:\n"
        "    S:\n"
        "      - bullet: hi\n",
        encoding="utf-8",
    )

    run(
        [str(venv_python), "-m", "rendercv", "render", "cv.yaml", "-nomd", "-nopng"],
        env={
            **OFFLINE_ENV,
            "XDG_CACHE_HOME": str(tmp_path / "cache"),
            "XDG_DATA_HOME": str(tmp_path / "data"),
        },
        cwd=tmp_path,
    )

    pdfs = list(tmp_path.glob("rendercv_output/*.pdf"))
    assert pdfs
    assert pdfs[0].stat().st_size > 0
