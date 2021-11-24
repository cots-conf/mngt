from logging.config import dictConfig
from typing import Optional

from flask import Flask, Response, render_template
from flask_humanize import Humanize

dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(process)d] [%(levelname)s] in %(module)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S %z",
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                }
            },
            "root": {"level": "DEBUG", "handlers": ["wsgi"]},
        },
    }
)


def create_app(test_config: Optional[dict] = None) -> Flask:
    """Application creation."""
    app = Flask(__name__)

    if test_config is None:
        app.config.from_object("mngt.config.Config")
    else:
        app.config.from_mapping(test_config)

    app.secret_key = app.config["SECRET_KEY"]
    app.config["HUMANIZE_USE_UTC"] = True
    humanize = Humanize(app)  # noqa: F841

    @app.route("/")
    def index() -> Response:
        return render_template("index.html")

    from . import db
    from .login_views import login_views

    db.init_app(app)
    app.register_blueprint(login_views)
    app.logger.debug("Finalize the app creation")

    return app


if __name__ == "__main__":
    pass
