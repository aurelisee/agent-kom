from fastapi import FastAPI
from agent.github_client import get_repo, list_files, list_commits, list_pull_requests
from fastapi import Depends
from sqlalchemy.orm import Session
from agent.database import get_db
#from agent.models import CommitModel, PullRequestModel
from agent.github_client import track_files, track_commits, track_pull_requests
from fastapi import FastAPI, Request
from pydantic import BaseModel
import json
from fastapi import APIRouter, HTTPException, Request
import requests
import os

app = FastAPI()
router = APIRouter()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Set this in your .env file

@router.get("/")
def home():
    return {"message": "Agent is running"}

@router.get("/repo/{owner}/{repo_name}")
def fetch_repo(owner: str, repo_name: str):
    """API endpoint"""
    full_repo_name = f"{owner}/{repo_name}"
    repo = get_repo(full_repo_name)
    
    if isinstance(repo, str):
        return {"error": repo}
    
    return {
        "name": repo.name,
        "description": repo.description,
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "owner": repo.owner.login,
    }

@router.get("/repo/{owner}/{repo_name}/files")
def fetch_files(owner: str, repo_name: str):
    """API endpoint to fetch all files in a repository."""
    return list_files(f"{owner}/{repo_name}")

@router.get("/repo/{owner}/{repo_name}/commits")
def fetch_commits(owner: str, repo_name: str):
    """API endpoint to fetch recent commits in a repository."""
    return list_commits(f"{owner}/{repo_name}")

@router.get("/repo/{owner}/{repo_name}/pulls")
def fetch_pull_requests(owner: str, repo_name: str):
    """API endpoint to fetch open pull requests."""
    return list_pull_requests(f"{owner}/{repo_name}")

@router.get("/repo/{owner}/{repo_name}/track/files")
def track_repo_files(owner: str, repo_name: str, db: Session = Depends(get_db)):
    """API to track file changes."""
    return track_files(f"{owner}/{repo_name}", db)

@router.get("/repo/{owner}/{repo_name}/track/commits")
def track_repo_commits(owner: str, repo_name: str, db: Session = Depends(get_db)):
    """API to track new commits."""
    return track_commits(f"{owner}/{repo_name}", db)

@router.get("/repo/{owner}/{repo_name}/track/pulls")
def track_repo_pulls(owner: str, repo_name: str, db: Session = Depends(get_db)):
    """API to track new pull requests."""
    return track_pull_requests(f"{owner}/{repo_name}", db)

@router.post("/repo/{owner}/{repo}/track/{type}")
async def track_changes(owner: str, repo: str, type: str, webhook: bool = False):
    if webhook:
        webhook_url = f"http://your-server-url/webhook/{owner}/{repo}"
        github_api_url = f"https://api.github.com/repos/{owner}/{repo}/hooks"

        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        payload = {
            "name": "web",
            "active": True,
            "events": ["push", "pull_request"],
            "config": {
                "url": webhook_url,
                "content_type": "json"
            }
        }

        response = requests.post(github_api_url, json=payload, headers=headers)

        if response.status_code != 201:
            raise HTTPException(status_code=400, detail=f"Webhook setup failed: {response.text}")

    return {"message": f"Tracking {type} for {owner}/{repo}"}

@router.post("/webhook/{owner}/{repo}")
async def github_webhook(owner: str, repo: str, request: Request):
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event")

    if event_type == "push":
        print(f"New push event in {owner}/{repo}: {payload}")
    elif event_type == "pull_request":
        print(f"New pull request event in {owner}/{repo}: {payload}")

    return {"message": "Webhook received"}


app.include_router(router)