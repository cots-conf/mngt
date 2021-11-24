import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuration object."""

    DEBUG = True if os.getenv("WEBAPP_DEBUG", "False") == "True" else False
    SECRET_KEY = os.getenv("WEBAPP_SECRET_KEY", "super-secret")
    # "sqlite+pysqlite://" is for in-memory.
    # "sqlite+pysqlite:///" is for file.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI", "sqlite+pysqlite:///mngt-app.test.db"
    )
