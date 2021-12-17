from math import ceil

from flask import current_app, request, url_for
from flask_restful import Resource
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from .db import get_engine
from .models import Proposal


class ProposalDetail(Resource):
    """Proposal detail endpoint."""

    def get(self, proposal_id: int) -> dict:
        """
        Return detail of the proposal.

        :param proposal_id: The ID of the proposal.
        """
        engine = get_engine()
        with Session(engine, future=True) as session:
            stmt = select(Proposal).where(Proposal.id == proposal_id)
            row = session.execute(stmt).scalars().first()
            return {"proposal_id": row.id, "title": row.title, "abstract": row.abstract}


class ProposalList(Resource):
    """Proposal list endpoint."""

    def get(self) -> dict:
        """Return list of proposals."""
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

            number_of_pages = int(
                ceil(total / current_app.config["ENTRY_PER_PAGE"] * 1.0)
            )
            pagination = {
                "has_prev": page > 1,
                "has_next": page < number_of_pages,
                "prev_num": page
                - 1,  # has_prev should be checked before using this value.
                "next_num": page
                + 1,  # has_next should be checked before using this value.
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

        proposals_dicts = []
        for proposal in proposals:
            p = {
                "title": proposal.title,
                "abstract": proposal.abstract,
            }
            proposals_dicts.append(p)

        return {
            "result": {"proposals": proposals_dicts},
            "next": next_url,
            "prev": prev_url,
        }
