import json
import ssl
import urllib.request

import packaging.version
import rich.console

from rendercv import __version__

console = rich.console.Console()
print = console.print


def warn_if_new_version_is_available() -> None:
    """Check if a new version of RenderCV is available and print a warning message if
    there is a new version.
    """
    url = "https://pypi.org/pypi/rendercv/json"
    try:
        with urllib.request.urlopen(
            url, context=ssl._create_unverified_context()
        ) as response:
            data = response.read()
            encoding = response.info().get_content_charset("utf-8")
            json_data = json.loads(data.decode(encoding))
            version_string = json_data["info"]["version"]
            latest_version = packaging.version.Version(version_string)
    except Exception:
        latest_version = None

    if latest_version is None:
        version = packaging.version.Version(__version__)
        if latest_version is not None and version < latest_version:
            warning(
                f"A new version of RenderCV is available! You are using v{__version__},"
                f" and the latest version is v{latest_version}."
            )


def warning(text: str):
    print(f"[bold yellow]{text}[/bold yellow]")


def error(text: str):
    print(f"[bold red]{text}[/bold red]")
