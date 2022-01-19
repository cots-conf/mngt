"""Conference views."""
import re
from datetime import datetime
from math import ceil

import arrow
from flask import (
    Blueprint, Response, abort, current_app, flash, redirect, render_template,
    request, url_for
)
from flask_login import login_required
from sqlalchemy import and_, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from mngt.db import get_engine
from mngt.forms import NewConferenceForm
from mngt.models import Conference, Participant, Proposal

conference_views = Blueprint(
    "conferences", __name__, template_folder="../../templates/conference/"
)


@conference_views.route("/conferences/new", methods=["GET", "POST"])
def create() -> Response:
    """Create new conference view."""
    conf_list_page = request.args.get("clp", 1, type=int)

    form = NewConferenceForm(request.form)
    print(form.data)
    if request.method == "POST" and form.validate():
        engine = get_engine()
        with Session(engine, future=True) as session:
            conf = Conference()
            form.populate_obj(conf)
            conf.slug = re.sub(r"\s+", "-", conf.name.strip())[:60]
            conf.created = datetime.utcnow()
            conf.modified = datetime.utcnow()

            try:
                session.add(conf)
                session.commit()
            except IntegrityError:
                flash("The conference with the same name already exist.", "error")
                if form.name.errors is None:
                    form.name.errors = [
                        "The conference with the same name already exist."
                    ]
                else:
                    form.name.errors.append(
                        "The conference with the same name already exist."
                    )
                return render_template(
                    "create.html", form=form, conf_list_page=conf_list_page
                )

            flash(f"Conference #{conf.slug} was successfully created")
            return redirect(url_for("conferences.list"))
    return render_template("create.html", form=form, conf_list_page=conf_list_page)


@conference_views.route("/conferences", methods=["GET"])
@login_required
def list() -> Response:
    """List conferences."""
    page = request.args.get("page", 1, type=int)
    order_by = request.args.get("order_by", "start", type=str)

    engine = get_engine()

    with Session(engine, future=True) as session:
        total_stmt = select(func.count()).select_from(Conference)
        limit_stmt = select(Conference)
        if order_by == "start":
            limit_stmt = limit_stmt.order_by(Conference.begin.asc())
        elif order_by == "name":
            limit_stmt = limit_stmt.order_by(Conference.name.asc())
        elif order_by == "number-of-proposal":
            # limit_stmt = limit_stmt.order_by(func.count(Conference.proposals).dsc())
            pass
        elif order_by == "number-of-panels":
            # limit_stmt = limit_stmt.order_by(Conference.panels.dsc())
            pass
        else:
            order_by = "start"  # So we don't pass the user value to the template.
            limit_stmt = limit_stmt.order_by(Conference.begin.asc())
        limit_stmt = limit_stmt.offset(
            (page - 1) * current_app.config["ENTRY_PER_PAGE"]
        ).limit(current_app.config["ENTRY_PER_PAGE"])

        total = session.execute(total_stmt).scalars().first()
        conferences = session.execute(limit_stmt).scalars().all()

        number_of_pages = int(ceil(total / current_app.config["ENTRY_PER_PAGE"] * 1.0))
        pagination = {
            "curr_page": page,
            "has_prev": page > 1,
            "has_next": page < number_of_pages,
            "prev_num": page - 1,  # has_prev should be checked before using this value.
            "next_num": page + 1,  # has_next should be checked before using this value.
        }
        prev_url = (
            url_for("conferences.list", page=pagination["prev_num"])
            if pagination["has_prev"]
            else None
        )
        next_url = (
            url_for("conferences.list", page=pagination["next_num"])
            if pagination["has_next"]
            else None
        )
        current_app.logger.debug(pagination)
        current_app.logger.debug(prev_url)
        current_app.logger.debug(next_url)

        return render_template(
            "conference/list.html",
            items=conferences,
            utcnow=datetime.utcnow(),
            pagination=pagination,
            prev_url=prev_url,
            next_url=next_url,
            order_by=order_by,
        )


@conference_views.route("/conferences/<slug>/edit", methods=["GET", "POST"])
def edit(slug: str) -> Response:
    """Edit conference view."""
    conf_list_page = request.args.get("clp", 1, type=int)

    if request.method == "GET":
        engine = get_engine()
        with Session(engine, future=True) as session:
            conf = session.query(Conference).filter(Conference.slug == slug).first()
            if conf is None:
                abort(404)

            form = NewConferenceForm(obj=conf)
            return render_template(
                "edit.html", conference=conf, form=form, conf_list_page=conf_list_page
            )

    elif request.method == "POST":
        form = NewConferenceForm(request.form)
        if form.validate():
            engine = get_engine()
            with Session(engine, future=True) as session:
                conf = session.query(Conference).filter(Conference.slug == slug).first()
                if conf is None:
                    abort(404)

                form.populate_obj(conf)
                conf.modified = datetime.utcnow()
                session.commit()

                flash(f"Conference #{conf.slug} was successfully modified")
                return redirect(url_for("conferences.list"))


@conference_views.route("/conferences/<slug>")
def detail(slug: str) -> Response:
    """Show detail view of a conference."""
    conf_list_page = request.args.get("clp", 1, type=int)

    engine = get_engine()
    with Session(engine, future=True) as session:
        get_stmt = select(Conference).where(Conference.slug == slug)
        conference = session.execute(get_stmt).scalars().first()
        if conference is None:
            abort(404)

        begin = arrow.get(conference.begin).format("MMMM D, YYYY HH:m")
        end = arrow.get(conference.end).format("MMMM D, YYYY HH:mm")

        return render_template(
            "conference/detail.html",
            cid=conference.id,
            slug=conference.slug,
            conf_list_page=conf_list_page,
            item=conference,
            begin=begin,
            end=end,
            proposal_counts=len([c for c in conference.proposals if not c.is_deleted]),
            panel_counts=len(conference.panels),
        )


@conference_views.route("/conferences/<slug>/search_proposal", methods=["GET", "POST"])
def search_proposal(slug: str) -> Response:
    """Return panels matching the search keywords."""
    query = request.args.get("q")
    engine = get_engine()
    with Session(engine, future=True) as session:
        # Get the conference by its slug.
        conf_get_stmt = select(Conference).where(Conference.slug == slug)
        conference = session.execute(conf_get_stmt).scalars().first()
        if conference is None:
            abort(404)

        # search_proposal_stmt = select(Proposal).where(Proposal.title.contains(query))
        # proposals = session.execute(search_proposal_stmt).scalars().all()
        proposals = (
            session.query(Proposal)
            .join(Participant)
            .filter(
                and_(
                    Proposal.conference_id == conference.id,
                    or_(
                        Proposal.title.contains(query),
                        Participant.first_name.contains(query),
                        Participant.last_name.contains(query),
                    ),
                )
            )
            .all()
        )

        return render_template(
            "conference/search_proposal_results.html", items=proposals
        )


@conference_views.route("/conferences/<slug>/search_author", methods=["GET", "POST"])
def search_author(slug: str) -> Response:
    """Return panels matching the search keywords."""
    query = request.args.get("q")
    engine = get_engine()
    with Session(engine, future=True) as session:
        # Get the conference by its slug.
        conf_get_stmt = select(Conference).where(Conference.slug == slug)

        conference = session.execute(conf_get_stmt).scalars().first()
        if conference is None:
            abort(404)

        authors = (
            session.query(Participant)
            .filter(
                and_(
                    Participant.conference_id == conference.id,
                    or_(
                        Participant.first_name.contains(query),
                        Participant.last_name.contains(query),
                    ),
                )
            )
            .all()
        )
        print(authors)
        return render_template("conference/search_author_results.html", authors=authors)


@conference_views.route("/conferences/<slug>/_debug", methods=["GET"])
def debug(slug: str) -> Response:
    """Return a debugging/prototyping view."""
    return render_template("conference/debug.html", slug=slug)


from .panel import *  # noqa: F401, E402, F403
from .proposal import *  # noqa: F401, E402, F403
