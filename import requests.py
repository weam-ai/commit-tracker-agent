import os
import logging
import requests
from dotenv import load_dotenv
from logger_config import logger

# ==== LOAD ENV VARIABLES ====
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = os.getenv("GITHUB_OWNER")
REPO = os.getenv("GITHUB_REPO")
BRANCH_NAME = os.getenv("GITHUB_BRANCH", "main")

# ==== HEADERS ====
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


def get_commits_from_pr(owner, repo, pr_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits"
    logger.info(f"Fetching commits for PR #{pr_number} from {owner}/{repo}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_unique_commits(owner, repo, base_branch, head_branch):
    url = f"https://api.github.com/repos/{owner}/{repo}/compare/{base_branch}...{head_branch}"
    logger.info(f"Comparing branches: base='{base_branch}' vs head='{head_branch}'")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['commits']  # list of commit objects


def print_commit_info(commits):
    if not commits:
        logger.info("No unique commits found.")
        return

    for commit in commits:
        message = commit['commit']['message']
        created = commit['commit']['author']['date']
        updated = commit['commit']['committer']['date']
        logger.info(f"Commit: {message}")
        logger.info(f"  Created: {created}")
        logger.info(f"  Updated: {updated}")

if __name__ == "__main__":
    logger.info("Checking for unique commits...")
    try:
        unique_commits = get_unique_commits(OWNER, REPO, base_branch="main", head_branch=BRANCH_NAME)
        print_commit_info(unique_commits)
    except requests.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
