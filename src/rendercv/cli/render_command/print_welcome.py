import rich
import rich.panel

from rendercv import __version__

from .. import printer


def print_welcome():
    printer.warn_if_new_version_is_available()

    printer.print(
        f"\nWelcome to [dodger_blue3]RenderCV v{__version__}[/dodger_blue3]!\n"
    )
    links = {
        "RenderCV App": "https://rendercv.com",
        "Documentation": "https://docs.rendercv.com",
        "Source code": "https://github.com/rendercv/rendercv/",
        "Bug reports": "https://github.com/rendercv/rendercv/issues/",
    }
    link_strings = [
        f"[bold cyan]{title + ':':<15}[/bold cyan] [link={link}]{link}[/link]"
        for title, link in links.items()
    ]
    link_panel = rich.panel.Panel(
        "\n".join(link_strings),
        title="Useful Links",
        title_align="left",
        border_style="bright_black",
    )

    printer.print(link_panel)
