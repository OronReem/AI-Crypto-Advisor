from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DateTime, Index, func
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    coins = Column(ARRAY(String))
    investor_type = Column(String)
    content_types = Column(ARRAY(String))


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    section = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    item = Column(String, nullable=False)
    direction = Column(String, nullable=False)
    # no timezone stored — required for the date-based index below to be
    # allowed at all (Postgres rejects an index built on a value that could
    # change with the session's timezone setting)
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())

    __table_args__ = (
        # one row per user+section+item+day — func.date() strips the time,
        # leaving just the calendar day, so a re-vote on a different day is
        # a new row instead of overwriting today's
        Index(
            "one_vote_per_item_per_day",
            user_id, section, item, func.date(created_at),
            unique=True,
        ),
    )


class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # a real Date column, not a timestamp — the day is the whole point here,
    # so there's no time to strip and no index expression needed
    date = Column(Date, nullable=False)
    # Text rather than String: no length limit, since it's a paragraph
    insight = Column(Text, nullable=False)
    topic = Column(String, nullable=False)

    __table_args__ = (
        # one insight per user per day — this is what makes the second page
        # load of the day reuse the row instead of calling the LLM again
        Index("one_insight_per_user_per_day", user_id, date, unique=True),
    )
