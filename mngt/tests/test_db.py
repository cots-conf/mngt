import os
from pathlib import Path

import pytest

BASEDIR = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def cots2021_proposals_file() -> Path:
    """Return path to the COTS 2021 data file."""
    return Path(BASEDIR) / "cots2021-proposals.xlsx"
