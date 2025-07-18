"""
`__main__.py` file is the file that gets executed when the RenderCV package itself is
invoked directly from the command line with `python -m rendercv`. That's why we have it
here so that we can invoke the CLI from the command line with `python -m rendercv`.
"""

from rendercv import cli

if __name__ == "__main__":
    # cli.cli_command_render("/home/panlab/Documents/rendercv/examples/John_Doe_EngineeringresumesTheme_CV.yaml")
    if hasattr(cli, "app"):
        cli.app()
