from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Proposal(Base):
    """ORM model for Proposal table."""

    __tablename__ = "proposal"

    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    modified = Column(DateTime)

    # TODO: Add author

    type = Column(String(length=200))
    abstract = Column(Text)


class Panel(Base):
    """ORM model for Panel table."""

    __tablename__ = "panel"

    id = Column(Integer, primary_key=True)
    title = Column(String(length=200))
    start = Column(DateTime)
    end = Column(DateTime)
    url = Column(String(length=4096))
