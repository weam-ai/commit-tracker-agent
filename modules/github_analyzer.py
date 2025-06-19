import requests
from logger_config import logger


def get_github_commits(repo_owner, repo_name, keywords, token=None, branch='main'):
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    params = {'sha': branch, 'per_page': 100}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    matches = []
    for item in data:
        msg = item['commit']['message']
        for keyword in keywords:
            if keyword.lower() in msg.lower():
                matches.append({
                    'date': item['commit']['author']['date'][:10],
                    'author': item['commit']['author']['name'],
                    'message': msg.strip(),
                    'keyword': keyword,
                    'sha': item['sha']
                })
    logger.info(f"Found {len(matches)} matching commits in {repo_name}.")
    return matches


def get_unique_commits(repo_owner, repo_name, base_branch, head_branch, token=None):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/compare/{base_branch}...{head_branch}"
    headers = {"Authorization": f"token {token}"} if token else {}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['commits']


def get_commit_diff(repo_owner, repo_name, sha, token=None):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{sha}"
    headers = {"Authorization": f"token {token}"} if token else {}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    files = response.json().get("files", [])
    if not files:
        logger.warning(f"No files found for commit {sha}")
        return ""
    
    diff_output = ""
    for f in files:
        filename = f.get("filename", "")
        patch = f.get("patch", "")
        if patch:
            diff_output += f"+++ {filename}\\n{patch}\\n"

    return diff_output
