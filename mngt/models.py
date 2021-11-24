import flask_login
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(flask_login.UserMixin):
    """User model."""

    pass


class Participant(Base):
    """ORM model for Participant table."""

    __tablename__ = "participant"

    id = Column(Integer, primary_key=True)
    # Let overshoot it; https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
    email = Column(String(length=350), unique=True)
    created = Column(DateTime)
    modified = Column(DateTime)

    first_name = Column(String(length=250))
    last_name = Column(String(length=250))
    affiliation = Column(String(length=300))


class Proposal(Base):
    """ORM model for Proposal table."""

    __tablename__ = "proposal"

    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    modified = Column(DateTime)

    # TODO: Add author

    type = Column(String(length=200))
    abstract = Column(Text)


class Participation(Base):
    """Connect Panel and Participant."""

    __tablename__ = "participation"

    id = Column(Integer, primary_key=True)

    panel_id = Column(Integer, ForeignKey("panel.id"))
    participant_id = Column(Integer, ForeignKey("participant.id"))

    role = Column(String(length=150))


class Panel(Base):
    """ORM model for Panel table."""

    __tablename__ = "panel"

    id = Column(Integer, primary_key=True)
    title = Column(String(length=200))
    start = Column(DateTime)
    end = Column(DateTime)
    url = Column(String(length=4096))

    # TODO: Add relation to participant via paricipation table.
    participants = relationship(
        "Participation", secondary=Participation, backref="panels"
    )
