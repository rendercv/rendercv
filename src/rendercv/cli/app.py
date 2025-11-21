import typer

app = typer.Typer(
    rich_markup_mode="rich",
    add_completion=False,
    # to make `rendercv --version` work:
    invoke_without_command=True,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    # don't show local variables in unhandled exceptions:
    pretty_exceptions_show_locals=False,
)
