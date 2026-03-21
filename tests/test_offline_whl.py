"""Test that rendercv works from a wheel in a non-networked environment."""

import os
import pathlib
import subprocess
import sys

PROJECT_ROOT = pathlib.Path(__file__).parent.parent

# Environment that poisons all HTTP/HTTPS so any network call fails immediately.
OFFLINE_ENV = {
    **os.environ,
    "http_proxy": "http://0.0.0.0:1",
    "https_proxy": "http://0.0.0.0:1",
    "no_proxy": "",
}


def run(args: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    """Run a subprocess with sensible defaults."""
    return subprocess.run(
        args, capture_output=True, text=True, timeout=120, check=True, **kwargs
    )


def test_rendercv_renders_pdf_offline(tmp_path: pathlib.Path) -> None:
    """Build wheel, install in isolated venv, render PDF without network."""
    dist_dir = tmp_path / "dist"
    run(["uv", "build", "--wheel", "--out-dir", str(dist_dir)], cwd=PROJECT_ROOT)

    wheel = next(dist_dir.glob("rendercv-*.whl"))
    venv_python = tmp_path / "venv" / "bin" / "python"

    run(["uv", "venv", str(venv_python.parent.parent), "--python", sys.executable])
    run(["uv", "pip", "install", "--python", str(venv_python), f"{wheel}[full]"])

    (tmp_path / "cv.yaml").write_text(
        "cv:\n  name: Test\n  sections:\n    S:\n      - bullet: hi\n",
        encoding="utf-8",
    )

    run(
        [str(venv_python), "-m", "rendercv", "render", "cv.yaml", "-nomd", "-nopng"],
        env=OFFLINE_ENV,
        cwd=tmp_path,
    )

    pdfs = list(tmp_path.glob("rendercv_output/*.pdf"))
    assert pdfs
    assert pdfs[0].stat().st_size > 0
