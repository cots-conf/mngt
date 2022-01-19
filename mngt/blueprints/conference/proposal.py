from datetime import datetime
from math import ceil

from flask import (
    Response, abort, current_app, flash, redirect, render_template, request,
    url_for
)
from flask_login import login_required
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from mngt.db import get_engine, get_short_title
from mngt.forms import NewProposalForm
from mngt.models import Conference, Participant, Proposal

from . import conference_views


@conference_views.route("/conferences/<slug>/proposals/new", methods=["GET", "POST"])
def create_proposal(slug: str) -> Response:
    """Create a proposal for the conference `slug`."""
    conf_list_page = request.args.get("clp", 1, type=int)
    proposal_list_page = request.args.get("plp", 1, type=int)

    engine = get_engine()
    with Session(engine, future=True) as session:
        # Get the conference by its slug.
        conf_get_stmt = select(Conference).where(Conference.slug == slug)
        conference = session.execute(conf_get_stmt).scalars().first()

        authors = (
            session.query(Participant)
            .filter(Participant.conference_id == conference.id)
            .all()
        )

        if conference is None:
            abort(404)

        form = NewProposalForm(request.form)
        form.author_id.choices = [
            (a.id, f"{a.last_name}, {a.first_name}") for a in authors
        ]

        if request.method == "POST" and form.validate():
            engine = get_engine()
            with Session(engine, future=True) as session:
                proposal = Proposal()
                form.populate_obj(proposal)
                proposal.conference_id = conference.id
                proposal.created = datetime.utcnow()
                proposal.modified = datetime.utcnow()

                session.add(proposal)
                session.commit()
                return redirect(
                    url_for(
                        "conferences.list_proposals",
                        slug=conference.slug,
                        page=proposal_list_page,
                        clp=conf_list_page,
                    )
                )
        return render_template(
            "conference/proposal/create.html",
            slug=slug,
            conference=conference,
            form=form,
            conf_list_page=conf_list_page,
            proposal_list_page=proposal_list_page,
            authors=authors,
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
            .where(Proposal.is_deleted == False)  # noqa: E712
        )
        limit_stmt = (
            select(Proposal)
            .where(Proposal.conference_id == conference.id)
            .where(Proposal.is_deleted == False)  # noqa: E712
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
            "conference/proposal/list.html",
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
            "conference/proposal/detail.html",
            conference=conference,
            cid=conference.id,
            slug=slug,
            item=proposal,
            conf_list_page=conf_list_page,
            proposal_list_page=proposal_list_page,
        )


@conference_views.route(
    "/conferences/<slug>/proposals/<int:pid>/delete", methods=["GET", "POST"]
)
@login_required
def proposal_delete(slug: str, pid: int) -> Response:
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

        proposal.is_deleted = True
        session.commit()

        flash(f"Proposal #{proposal.id} was successfully deleted")
        return redirect(
            url_for(
                "conferences.list_proposals",
                slug=slug,
                page=proposal_list_page,
                clp=conf_list_page,
            )
        )
