import os
from dotenv import load_dotenv
from github import Github
from sqlalchemy.orm import Session
from agent.database import SessionLocal, FileEntry, CommitEntry, PullRequestEntry
import datetime
import requests

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

github_client = Github(GITHUB_TOKEN)

def get_repo(repo_name):
    """repository dets"""
    try:
        repo = github_client.get_repo(repo_name)
        return repo
    except Exception as e:
        return f"Error: {str(e)}"

def list_files(repo_name):
    """files and directories in a repository"""
    try:
        repo = github_client.get_repo(repo_name)
        contents = repo.get_contents("")  
        files = []

        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            files.append({"path": file_content.path, "type": file_content.type})

        return files
    except Exception as e:
        return {"error": str(e)}

def list_commits(repo_name):
    """Commits from a repository"""
    try:
        repo = github_client.get_repo(repo_name)
        commits = repo.get_commits()
        
        commit_list = []
        for commit in commits[:10]:  # Get last 10 commits
            commit_list.append({
                "sha": commit.sha,
                "author": commit.author.login if commit.author else "Unknown",
                "message": commit.commit.message,
                "date": commit.commit.author.date.strftime("%Y-%m-%d %H:%M:%S")
            })

        return commit_list
    except Exception as e:
        return {"error": str(e)}


def list_pull_requests(repo_name):
    """Open pull requests from a repository"""
    try:
        repo = github_client.get_repo(repo_name)
        pulls = repo.get_pulls(state='open')
        
        pr_list = []
        for pr in pulls:
            pr_list.append({
                "id": pr.id,
                "title": pr.title,
                "user": pr.user.login,
                "created_at": pr.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "url": pr.html_url
            })

        return pr_list
    except Exception as e:
        return {"error": str(e)}

def get_db():
    """Create a new database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def track_files(repo_name, db: Session):
    """Track file changes."""
    repo = github_client.get_repo(repo_name)
    contents = repo.get_contents("")
    new_files = set()

    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        new_files.add(file_content.path)

    # Get stored files from database
    stored_files = {file.path for file in db.query(FileEntry).all()}

    # Detect added and removed files
    added_files = new_files - stored_files
    removed_files = stored_files - new_files

    # Update database
    for path in added_files:
        db.add(FileEntry(path=path, type="file"))
    for path in removed_files:
        db.query(FileEntry).filter(FileEntry.path == path).delete()

    db.commit()
    return {"added": list(added_files), "removed": list(removed_files)}

def track_commits(repo_name, db: Session):
    """Track new commits."""
    repo = github_client.get_repo(repo_name)
    commits = repo.get_commits()
    
    new_commits = []
    for commit in commits[:10]:  # Check last 10 commits
        if not db.query(CommitEntry).filter(CommitEntry.sha == commit.sha).first():
            new_commits.append(commit)

    # Insert new commits into database
    for commit in new_commits:
        db.add(CommitEntry(
            sha=commit.sha,
            author=commit.author.login if commit.author else "Unknown",
            message=commit.commit.message,
            date=commit.commit.author.date
        ))

    db.commit()
    return {"new_commits": [{"sha": c.sha, "message": c.commit.message} for c in new_commits]}

def track_pull_requests(repo_name, db: Session):
    """Track new pull requests."""
    repo = github_client.get_repo(repo_name)
    pulls = repo.get_pulls(state='open')

    new_prs = []
    for pr in pulls:
        if not db.query(PullRequestEntry).filter(PullRequestEntry.id == pr.id).first():
            new_prs.append(pr)

    # Insert new PRs into database
    for pr in new_prs:
        db.add(PullRequestEntry(
            id=pr.id, title=pr.title, user=pr.user.login,
            created_at=pr.created_at, url=pr.html_url
        ))

    db.commit()
    return {"new_prs": [{"id": p.id, "title": p.title} for p in new_prs]}


