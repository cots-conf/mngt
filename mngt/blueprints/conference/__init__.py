"""Conference views."""
import re
from datetime import datetime
from math import ceil

import arrow
from flask import (
    Blueprint, Response, abort, current_app, redirect, render_template,
    request, url_for
)
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from mngt.db import get_engine, get_short_title
from mngt.forms import NewConferenceForm
from mngt.models import Conference, Panel, Participant, Proposal

conference_views = Blueprint(
    "conferences", __name__, template_folder="../../templates/conference/"
)


@conference_views.route("/conferences", methods=["GET"])
def list() -> Response:
    """List conferences."""
    page = request.args.get("page", 1, type=int)

    engine = get_engine()

    with Session(engine, future=True) as session:
        total_stmt = select(func.count()).select_from(Conference)
        limit_stmt = (
            select(Conference)
            .order_by(Conference.begin.asc())
            .offset((page - 1) * current_app.config["ENTRY_PER_PAGE"])
            .limit(current_app.config["ENTRY_PER_PAGE"])
        )

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
        )


@conference_views.route("/conferences/new", methods=["GET", "POST"])
def create() -> Response:
    """A view for creating new conference."""
    conf_list_page = request.args.get("clp", 1, type=int)

    form = NewConferenceForm(request.form)
    print(form.data)
    if request.method == "POST" and form.validate():
        engine = get_engine()
        with Session(engine, future=True) as session:
            conf = Conference()
            form.populate_obj(conf)
            conf.slug = re.sub(r"\s+", "-", conf.name)[:60]
            session.add(conf)
            session.commit()
            return redirect(url_for("conferences.list"))
    return render_template("create.html", form=form, conf_list_page=conf_list_page)


@conference_views.route("/conferences/<slug>")
def detail(slug: str) -> Response:
    """A view for conference detail."""
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
            proposal_counts=len(conference.proposals),
            panel_counts=len(conference.panels),
        )


@conference_views.route("/conferences/<slug>/proposals", methods=["GET"])
def list_proposals(slug: str) -> Response:
    """List proposals."""
    conf_list_page = request.args.get("clp", 1, type=int)
    page = request.args.get("page", 1, type=int)

    engine = get_engine()
    with Session(engine, future=True) as session:
        # Get the conference by its slug.
        conf_get_stmt = select(Conference).where(Conference.slug == slug)
        conference = session.execute(conf_get_stmt).scalars().first()
        if conference is None:
            abort(404)

        total_stmt = (
            select(func.count())
            .select_from(Proposal)
            .where(Proposal.conference_id == conference.id)
        )
        limit_stmt = (
            select(Proposal)
            .where(Proposal.conference_id == conference.id)
            .order_by(Proposal.created.desc())
            .offset((page - 1) * current_app.config["ENTRY_PER_PAGE"])
            .limit(current_app.config["ENTRY_PER_PAGE"])
        )

        total = session.execute(total_stmt).scalars().first()
        raw_proposals = session.execute(limit_stmt).scalars().all()

        proposals = []
        for proposal in raw_proposals:
            short_title = get_short_title(proposal.title)
            proposals.append((short_title, proposal))

        number_of_pages = int(ceil(total / current_app.config["ENTRY_PER_PAGE"] * 1.0))
        pagination = {
            "curr_page": page,
            "has_prev": page > 1,
            "has_next": page < number_of_pages,
            "prev_num": page - 1,  # has_prev should be checked before using this value.
            "next_num": page + 1,  # has_next should be checked before using this value.
        }
        prev_url = (
            url_for(
                "conferences.list_proposals", slug=slug, page=pagination["prev_num"]
            )
            if pagination["has_prev"]
            else None
        )
        next_url = (
            url_for(
                "conferences.list_proposals", slug=slug, page=pagination["next_num"]
            )
            if pagination["has_next"]
            else None
        )
        current_app.logger.debug(pagination)
        current_app.logger.debug(prev_url)
        current_app.logger.debug(next_url)

        return render_template(
            "conference/list_proposals.html",
            conference=conference,
            cid=conference.id,
            slug=slug,
            conf_list_page=conf_list_page,
            items=proposals,
            utcnow=datetime.utcnow(),
            pagination=pagination,
            prev_url=prev_url,
            next_url=next_url,
        )


@conference_views.route("/conferences/<slug>/proposals/new", methods=["GET", "POST"])
def create_proposal(slug: str) -> Response:
    """Create a proposal for the conference `cid`."""
    return "New proposal."


@conference_views.route(
    "/conferences/<slug>/proposals/<int:pid>", methods=["GET", "POST"]
)
def proposal_detail(slug: str, pid: int) -> Response:
    """Return proposal detail."""
    conf_list_page = request.args.get("clp", 1, type=int)
    proposal_list_page = request.args.get("plp", 1, type=int)

    engine = get_engine()
    with Session(engine, future=True) as session:
        # Get the conference by its slug.
        conf_get_stmt = select(Conference).where(Conference.slug == slug)
        conference = session.execute(conf_get_stmt).scalars().first()
        if conference is None:
            abort(404)

        proposal_get_stmt = (
            select(Proposal)
            .where(Proposal.conference_id == conference.id)
            .where(Proposal.id == pid)
        )
        proposal = session.execute(proposal_get_stmt).scalars().first()
        if proposal is None:
            abort(404)

        return render_template(
            "conference/proposal_detail.html",
            conference=conference,
            cid=conference.id,
            slug=slug,
            item=proposal,
            conf_list_page=conf_list_page,
            proposal_list_page=proposal_list_page,
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
            "conference/list_panels.html",
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

        return render_template(
            "conference/create_panel.html",
            conference=conference,
            cid=conference.id,
            slug=slug,
            conf_list_page=conf_list_page,
            utcnow=datetime.utcnow(),
        )


@conference_views.route("/conferences/<slug>/panels/<int:pid>", methods=["GET", "POST"])
def panel_detail(slug: str, pid: int) -> Response:
    """Return panel detail."""
    return "Panel detail."


@conference_views.route("/conferences/<slug>/search", methods=["GET", "POST"])
def search_proposal(slug: str) -> Response:
    """Return panels matching the search keywords."""
    # TODO: Allow searching with author name.
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
        # titles = " ".join([p.title for p in proposals])

        return render_template("conference/search_results.html", items=proposals)


@conference_views.route("/conferences/<slug>/_debug", methods=["GET"])
def debug(slug: str) -> Response:
    """Return a debugging/prototyping view."""
    return render_template("conference/debug.html", slug=slug)
