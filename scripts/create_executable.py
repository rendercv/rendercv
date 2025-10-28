import pathlib
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from typing import Final


def create_executable() -> None:
    """Create a standalone executable for the current platform and zip it with preserved permissions."""

    # Constants
    root_path: Final[pathlib.Path] = pathlib.Path(__file__).parent.parent

    platform_names: Final[dict[str, str]] = {
        "linux": "linux",
        "darwin": "macos",
        "win32": "windows",
    }

    machine_names: Final[dict[str, str]] = {
        "AMD64": "x86_64",
        "x86_64": "x86_64",
        "aarch64": "ARM64",
        "arm64": "ARM64",
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)

        # Copy rendercv to temp directory
        shutil.copytree(root_path / "src" / "rendercv", temp_path / "rendercv")

        # Create entry point script
        rendercv_file = temp_path / "rendercv.py"
        rendercv_file.write_text("import rendercv.cli as cli; cli.app()")

        # Run PyInstaller
        subprocess.run(
            [
                sys.executable,
                "-m",
                "PyInstaller",
                "--onefile",
                "--clean",
                "--collect-all",
                "rendercv",
                "--collect-all",
                "rendercv_fonts",
                "--distpath",
                "bin",
                str(rendercv_file),
            ],
            check=True,
        )

        # Determine executable name based on platform
        platform_name = platform_names[sys.platform]
        machine_name = machine_names[platform.machine()]

        # Get original and new executable paths
        match sys.platform:
            case "win32":
                original_name = "rendercv.exe"
                new_name = f"rendercv-{platform_name}-{machine_name}.exe"
            case _:
                original_name = "rendercv"
                new_name = f"rendercv-{platform_name}-{machine_name}"

        original_path = root_path / "bin" / original_name
        executable_path = root_path / "bin" / new_name
        original_path.rename(executable_path)

    # Create zip archive with preserved executable permissions
    zip_path = executable_path.with_suffix(".zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipinfo = zipfile.ZipInfo(executable_path.name)
        # Set Unix executable permissions (rwxr-xr-x) - 0o755 shifted to external_attr position
        zipinfo.external_attr = 0o755 << 16
        zipf.writestr(zipinfo, executable_path.read_bytes())


if __name__ == "__main__":
    create_executable()
