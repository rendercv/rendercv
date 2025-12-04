import runpy
import sys
from unittest.mock import patch

import pytest


def test_main_module_runs():
    """Test that running the module as __main__ executes the CLI app."""
    # Mock sys.argv to pass --help to avoid actually running the full CLI
    with patch.object(sys, "argv", ["rendercv", "--help"]):
        # Use runpy to execute the module, which will trigger the
        # if __name__ == "__main__" block --help causes a SystemExit(0), which is
        # expected
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_module("rendercv", run_name="__main__")
        assert exc_info.value.code == 0
