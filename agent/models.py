from sqlalchemy import Column, String, DateTime, Integer
from agent.database import Base

class CommitModel(Base):
    __tablename__ = "commits"

    id = Column(Integer, primary_key=True, index=True)
    sha = Column(String, unique=True, nullable=False)
    author = Column(String, nullable=False)
    message = Column(String, nullable=False)
    date = Column(DateTime, nullable=False, extend_existing=True)  # Extend existing columns

class PullRequestModel(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, nullable=False)
    title = Column(String, nullable=False)
    state = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, extend_existing=True)
