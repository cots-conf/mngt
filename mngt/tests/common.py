import os
import tempfile

import pytest

from mngt import create_app
from mngt.db import init_db

@pytest.fixture
def client():
    """Return a fixture for client."""
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite+pysqlite:///{db_path}"})

    with app.test_client() as client:
        with app.app_context():
            init_db()

        yield client

    os.close(db_fd)
    os.unlink(db_path)