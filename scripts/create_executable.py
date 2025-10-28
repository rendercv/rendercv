import pathlib
import platform
import shutil
import subprocess
import sys
import tempfile


def create_executable():
    # Make sure the current working directory is the root of the project:
    root = pathlib.Path(__file__).parent.parent

    with tempfile.TemporaryDirectory() as temp_dir:
        # copy rendercv to temp directory
        shutil.copytree(root / "src" / "rendercv", pathlib.Path(temp_dir) / "rendercv")
        temp_directory = pathlib.Path(temp_dir)
        rendercv_file_path = temp_directory / "rendercv.py"
        rendercv_file_path.touch()
        rendercv_file_path.write_text("import rendercv.cli as cli; cli.app()")

        # Run pyinstaller:
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
                str(rendercv_file_path),
            ],
            check=True,
        )

        # Rename the executable:
        platform_name = {
            "linux": "linux",
            "darwin": "macos",
            "win32": "windows",
        }
        machine_name = {
            "AMD64": "x86_64",
            "x86_64": "x86_64",
            "aarch64": "ARM64",
            "arm64": "ARM64",
        }
        executable_path = {
            "linux": root / "bin" / "rendercv",
            "darwin": root / "bin" / "rendercv",
            "win32": root / "bin" / "rendercv.exe",
        }
        new_executable_path = (
            root
            / "bin"
            / f"rendercv-{platform_name[sys.platform]}-{machine_name[platform.machine()]}"
        )
        if sys.platform == "win32":
            new_executable_path = new_executable_path.with_suffix(".exe")
        executable_path[sys.platform].rename(new_executable_path)

    print('Executable created at "bin" folder.')  # NOQA: T201


if __name__ == "__main__":
    create_executable()
