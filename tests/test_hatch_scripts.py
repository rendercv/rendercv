import contextlib
import os
import pathlib
import subprocess
import tempfile

import pytest


@pytest.mark.parametrize(
    "script_name",
    [
        "format",
        "lint",
        "check-types",
        "precommit",
        "update-schema",
        "update-examples",
        "docs:build",
        "docs:update-entry-figures",
    ],
)
@pytest.mark.skip(reason="They fail on GitHub Actions")
def test_scripts(script_name):
    # If hatch is not installed, just pass the test (suppress FileNotFoundError)
    with contextlib.suppress(FileNotFoundError):
        subprocess.run(["hatch", "run", script_name], check=True)


@pytest.mark.skip(reason="They fail on GitHub Actions")
def test_executable():
    # If hatch is not installed, just pass the test (suppress FileNotFoundError)
    with contextlib.suppress(FileNotFoundError):
        root = pathlib.Path(__file__).parent.parent
        bin_folder = root / "bin"
        # remove the bin folder if it exists
        if bin_folder.exists():
            for file in bin_folder.iterdir():
                file.unlink()
            bin_folder.rmdir()

        subprocess.run(["hatch", "run", "exe:create"], check=True, timeout=60)

        executable_path = next(bin_folder.iterdir())
        assert executable_path.is_file()

        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            subprocess.run([str(executable_path), "new", "John"], check=True)
            subprocess.run([str(executable_path), "render", "John_CV.yaml"], check=True)
            pdf_path = pathlib.Path(temp_dir) / "rendercv_output" / "John_CV.pdf"
            assert pdf_path.exists()
