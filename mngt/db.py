"""Database stuff."""
from typing import Any

import click
from flask import Flask, current_app, g
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_engine() -> Engine:
    """Initialize engine."""
    if "engine" not in g:
        g.engine = create_engine(
            current_app.config["SQLALCHEMY_DATABASE_URI"], echo=False, future=True
        )
    return g.engine


def close_engine(e: Any = None) -> None:
    """Close the database connection."""
    engine = g.pop("engine", None)
    if engine is not None:
        engine.dispose()


def init_db() -> None:
    """Create table."""
    engine = get_engine()

    from mngt.models import Base

    Base.metadata.create_all(engine)


@click.command("init-db")
@with_appcontext
def init_db_comamnd() -> None:
    """Create tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app: Flask) -> None:
    """Initialize application."""
    app.teardown_appcontext(close_engine)
    app.cli.add_command(init_db_comamnd)
