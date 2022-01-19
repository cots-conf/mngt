from datetime import datetime
from math import ceil

from flask import (
    Response, abort, current_app, redirect, render_template, request, url_for
)
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from mngt.db import get_engine
from mngt.forms import NewPanelForm
from mngt.models import Conference, Panel

from . import conference_views


@conference_views.route("/conferences/<slug>/panels/new", methods=["GET", "POST"])
def create_panel(slug: str) -> Response:
    """Create a panel for the conference `cid`."""
    conf_list_page = request.args.get("clp", 1, type=int)
    # page = request.args.get("page", 1, type=int)
    # TODO: Add param for stating panel after another panel.
    #       The start time of the next panel will then be used.

    engine = get_engine()
    with Session(engine, future=True) as session:
        # Get the conference by its slug.
        conf_get_stmt = select(Conference).where(Conference.slug == slug)
        conference = session.execute(conf_get_stmt).scalars().first()
        if conference is None:
            abort(404)

        form = NewPanelForm(request.form)

        if request.method == "POST" and form.validate():
            panel = Panel()
            form.populate_obj(panel)
            panel.conference_id = conference.id
            panel.created = datetime.utcnow()
            panel.modified = datetime.utcnow()

            # TODO: Couple checks
            # - Check if the gap is grater than the duration
            # - Check if the panel is overlaping with the others (may have to allow overlapping
            #   if that is want the user want.).
            # - The amount fo time for each presentation will be

            session.add(panel)
            session.commit()

            return redirect(url_for("conferences.panel_edit", slug=slug, pid=panel.id))

        return render_template(
            "conference/panel/create.html",
            conference=conference,
            cid=conference.id,
            slug=slug,
            conf_list_page=conf_list_page,
            utcnow=datetime.utcnow(),
            form=form,
        )


@conference_views.route("/conferences/<slug>/panels", methods=["GET", "POST"])
def list_panels(slug: str) -> Response:
    """Return list of panels."""
    conf_list_page = request.args.get("clp", 1, type=int)
    page = request.args.get("page", 1, type=int)

    # TODO: Allow panel to be moved around, and allow
    #       user to save the updated order.

    engine = get_engine()
    with Session(engine, future=True) as session:
        # Get the conference by its slug.
        conf_get_stmt = select(Conference).where(Conference.slug == slug)
        conference = session.execute(conf_get_stmt).scalars().first()
        if conference is None:
            abort(404)

        total_stmt = (
            select(func.count())
            .select_from(Panel)
            .where(Panel.conference_id == conference.id)
        )
        limit_stmt = (
            select(Panel)
            .where(Panel.conference_id == conference.id)
            .order_by(Panel.start.asc())
            .offset((page - 1) * current_app.config["ENTRY_PER_PAGE"])
            .limit(current_app.config["ENTRY_PER_PAGE"])
        )

        total = session.execute(total_stmt).scalars().first()
        panels = session.execute(limit_stmt).scalars().all()

        number_of_pages = int(ceil(total / current_app.config["ENTRY_PER_PAGE"] * 1.0))
        pagination = {
            "curr_page": page,
            "has_prev": page > 1,
            "has_next": page < number_of_pages,
            "prev_num": page - 1,  # has_prev should be checked before using this value.
            "next_num": page + 1,  # has_next should be checked before using this value.
        }
        prev_url = (
            url_for("conferences.list_panels", slug=slug, page=pagination["prev_num"])
            if pagination["has_prev"]
            else None
        )
        next_url = (
            url_for("conferences.list_panels", slug=slug, page=pagination["next_num"])
            if pagination["has_next"]
            else None
        )
        current_app.logger.debug(pagination)
        current_app.logger.debug(prev_url)
        current_app.logger.debug(next_url)

        return render_template(
            "conference/panel/list.html",
            conference=conference,
            cid=conference.id,
            slug=slug,
            conf_list_page=conf_list_page,
            items=panels,
            utcnow=datetime.utcnow(),
            pagination=pagination,
            prev_url=prev_url,
            next_url=next_url,
        )


@conference_views.route("/conferences/<slug>/panels/<int:pid>", methods=["GET", "POST"])
def panel_detail(slug: str, pid: int) -> Response:
    """Return panel detail.

    TODO: Separate the role for each participant?
    """
    return f"Conference {slug}: Panel #{pid}'s detail."


@conference_views.route(
    "/conferences/<slug>/panels/<int:pid>/edit", methods=["GET", "POST"]
)
def panel_edit(slug: str, pid: int) -> Response:
    """Return panel detail."""
    return f"Editing panel #{pid} in conference {slug}."
