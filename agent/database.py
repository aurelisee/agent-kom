from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
# Create SQLite database
DATABASE_URL = "sqlite:///./repo_data.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define models
class FileEntry(Base):
    __tablename__ = "files"
    path = Column(String, primary_key=True)
    type = Column(String)

class CommitEntry(Base):
    __tablename__ = "commits"
    sha = Column(String, primary_key=True)
    author = Column(String)
    message = Column(String)
    date = Column(DateTime)

class PullRequestEntry(Base):
    __tablename__ = "pull_requests"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    user = Column(String)
    created_at = Column(DateTime)
    url = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# Function to get a database session
def get_db():
    """Create a new database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

