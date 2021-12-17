"""Proposal views."""
from datetime import datetime
from math import ceil

from flask import (
    Blueprint, Response, current_app, render_template, request, url_for
)
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from .db import get_engine
from .models import Proposal

proposal_views = Blueprint("proposals", __name__, template_folder="templates")


@proposal_views.route("/proposals", methods=["GET"])
def list_proposals() -> Response:
    """List proposals."""
    page = request.args.get("page", 1, type=int)

    engine = get_engine()

    with Session(engine, future=True) as session:
        total_stmt = select(func.count()).select_from(Proposal)
        limit_stmt = (
            select(Proposal)
            .order_by(Proposal.created.desc())
            .offset((page - 1) * current_app.config["ENTRY_PER_PAGE"])
            .limit(current_app.config["ENTRY_PER_PAGE"])
        )

        total = session.execute(total_stmt).scalars().first()
        proposals = session.execute(limit_stmt).scalars().all()

        number_of_pages = int(ceil(total / current_app.config["ENTRY_PER_PAGE"] * 1.0))
        pagination = {
            "has_prev": page > 1,
            "has_next": page < number_of_pages,
            "prev_num": page - 1,  # has_prev should be checked before using this value.
            "next_num": page + 1,  # has_next should be checked before using this value.
        }
        prev_url = (
            url_for("proposals.list_proposals", page=pagination["prev_num"])
            if pagination["has_prev"]
            else None
        )
        next_url = (
            url_for("proposals.list_proposals", page=pagination["next_num"])
            if pagination["has_next"]
            else None
        )
        current_app.logger.debug(pagination)
        current_app.logger.debug(prev_url)
        current_app.logger.debug(next_url)

        return render_template(
            "proposal/list.html",
            items=proposals,
            utcnow=datetime.utcnow(),
            pagination=pagination,
            prev_url=prev_url,
            next_url=next_url,
        )


@proposal_views.route("/proposals/new", methods=["GET", "POST"])
def create_proposal() -> Response:
    """A view for creating new proposal."""
    if request.method == "GET":
        return
    return "New proposal."


@proposal_views.route("/proposals/<int:pid>")
def proposal_detail(pid: int) -> Response:
    """A view for proposal detail."""
    return "Proposal detail."
