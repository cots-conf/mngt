from logging.config import dictConfig
from typing import Optional

import flask_login
from authlib.integrations.flask_client import OAuth
from flask import Flask, Response, render_template
from flask_humanize import Humanize
from flask_restful import Api

from .db import _users
from .models import User

oauth = OAuth()
oauth.register(  # noqa: S106
    "azure",
    # server_metadata_url="https://login.microsoftonline.com/organizations/v2.0/.well-known/openid-configuration",
    api_base_url="https://graph.microsoft.com/",
    authorize_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    access_token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
    jwks_uri="https://login.microsoftonline.com/common/discovery/v2.0/keys",
    userinfo_endpoint="https://graph.microsoft.com/oidc/userinfo",
    client_kwargs={"scope": "openid profile email"},
)
login_manager = flask_login.LoginManager()

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
    from .blueprints.conference import conference_views
    from .login_views import login_views
    from .proposal_api import NewPanel, ProposalDetail, ProposalList

    api = Api(app, prefix="/api/v1/")
    db.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)

    # Views
    app.register_blueprint(login_views)
    app.register_blueprint(conference_views)

    # APIs
    api.add_resource(ProposalDetail, "/conferences/<slug>/proposals/<int:proposal_id>")
    api.add_resource(ProposalList, "/conferences/<slug>/proposals")
    api.add_resource(NewPanel, "/conferences/<slug>/panels/new")

    app.logger.debug("Finalize the app creation")

    login_manager.login_view = "login.login"

    @login_manager.user_loader
    def user_loader(user_id: str) -> User:
        """Load the user object."""
        app.logger.debug(f"attempt to load {user_id}")

        if user_id not in _users:
            return

        user = User()
        user.id = user_id
        return user

    return app


if __name__ == "__main__":
    pass
