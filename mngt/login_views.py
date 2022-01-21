import flask_login
from flask import (
    Blueprint, Response, current_app, flash, redirect, request, url_for
)

from . import oauth
from .db import _users
from .models import User

login_views = Blueprint("login", __name__, template_folder="templates")


@login_views.route("/login")
def login() -> Response:
    """Login view."""
    proto = request.headers["X-Forwarded-Proto"]
    redirect_uri = url_for("login.authorize", _external=True, _scheme=proto)
    current_app.logger.debug(f"oauth redirect uri: {redirect_uri}")
    return oauth.azure.authorize_redirect(redirect_uri)


@login_views.route("/authorize")
def authorize() -> Response:
    """Callback endpoint for oauth."""
    token = oauth.azure.authorize_access_token()
    userinfo = oauth.azure.parse_id_token(token)

    if userinfo["email"] not in _users:
        flash("You does not have permission to access the application.")
        return redirect("/")

    user = User()
    user.id = userinfo["email"]

    flask_login.login_user(user)

    return redirect("/")


@login_views.route("/logout")
def logout() -> Response:
    """Log user out."""
    flask_login.logout_user()
    return redirect("/")
