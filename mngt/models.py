import flask_login
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.schema import Table

Base = declarative_base()


class User(flask_login.UserMixin):
    """User model."""

    pass


class Conference(Base):
    """ORM model for Conference table."""

    __tablename__ = "conference"

    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    modified = Column(DateTime)

    name = Column(String(length=350), unique=True)
    description = Column(String(length=250))
    begin = Column(DateTime)
    end = Column(DateTime)

    panels = relationship("Panel", back_populates="conference")


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

    proposals = relationship("Proposal", back_populates="author")


class Proposal(Base):
    """ORM model for Proposal table."""

    __tablename__ = "proposal"

    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    modified = Column(DateTime)

    author_id = Column(Integer, ForeignKey("participant.id"))
    author = relationship("Participant", back_populates="proposals")
    title = Column(String(length=300))
    type = Column(String(length=200))
    abstract = Column(Text)


Participation = Table(
    "participation",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("panel_id", Integer, ForeignKey("panel.id")),
    Column("participant_Id", Integer, ForeignKey("participant.id")),
    Column("role", String(length=150)),
)


class Panel(Base):
    """ORM model for Panel table."""

    __tablename__ = "panel"

    id = Column(Integer, primary_key=True)
    title = Column(String(length=200))
    start = Column(DateTime)
    end = Column(DateTime)
    url = Column(String(length=4096))

    conference_id = Column(Integer, ForeignKey("conference.id"))
    conference = relationship("Conference", back_populates="panels")

    participants = relationship(
        "Participant", secondary=Participation, backref="panels"
    )
