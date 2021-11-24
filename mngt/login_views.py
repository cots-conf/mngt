from flask import Blueprint, Response, redirect

login_views = Blueprint("login", __name__, template_folder="templates")


@login_views.route("/login")
def login() -> Response:
    """Login view."""
    return "Logged in"


@login_views.route("/logout")
def logout() -> Response:
    """Log user out."""
    return redirect("/")
