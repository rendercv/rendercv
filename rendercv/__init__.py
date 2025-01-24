"""
RenderCV is a Typst-based Python package with a command-line interface (CLI) that allows
you to version-control your CV/resume as source code.
"""

__version__ = "2.0"

from .api import create_contents_of_a_typst_file

__all__ = ["create_contents_of_a_typst_file"]

_parial_install_error_message = (
    'Please install RenderCV with `pip install "rendercv[full]"` to be able to use'
    " all the features of RenderCV."
)
