import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from modules.sheet_reader import read_google_sheet
from modules.github_analyzer import get_commit_diff, get_unique_commits as get_unique_commits_analyzer
from modules.commit_summarizer import summarize_commit
from modules.timeline_checker import check_timeline_status
from modules.sheet_writer import write_task_updates
from modules.predictor import predict_delay_status
from modules.utils import compile_task_pattern
from logger_config import logger

# === Load environment variables ===
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")
SHEET_RANGE = os.getenv("SHEET_RANGE", "Sheet1!A:E")  # default range

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

REPOSITORIES = [
    {
        "owner": os.getenv("REPO_1_OWNER", "default-owner-1"),
        "name": os.getenv("REPO_1_NAME", "default-repo-1"),
        "branch": os.getenv("REPO_1_BRANCH", "main")
    },
    {
        "owner": os.getenv("REPO_2_OWNER", "default-owner-2"),
        "name": os.getenv("REPO_2_NAME", "default-repo-2"),
        "branch": os.getenv("REPO_2_BRANCH", "main")
    },
    {
        "owner": os.getenv("REPO_3_OWNER", "default-owner-3"),
        "name": os.getenv("REPO_3_NAME", "default-repo-3"),
        "branch": os.getenv("REPO_3_BRANCH", "main")
    },
]

def print_commit_info(commits):
    for commit in commits:
        message = commit['commit']['message']
        created = commit['commit']['author']['date']
        updated = commit['commit']['committer']['date']
        logger.info(f"Commit: {message}")
        logger.info(f"  Created: {created}")
        logger.info(f"  Updated: {updated}\n")

def is_related(task_name, keyword, commit_msg):
    import re
    commit_msg_lower = commit_msg.lower()
    task_tokens = [w for w in re.findall(r'\w+', task_name.lower()) if len(w) > 2]
    match_score = sum(1 for token in task_tokens if token in commit_msg_lower)
    return match_score >= 2 or (keyword and keyword.lower() in commit_msg_lower)

def main():
    logger.info("🔄 Fetching tasks from Google Sheet...")
    df = read_google_sheet(SHEET_ID, SHEET_RANGE)

    if df.empty:
        logger.warning("⚠️ No data found in the sheet.")
        return

    logger.info("✅ Tasks fetched successfully.")
    task_updates = {}

    for _, task in df.iterrows():
        task_name = task['Task Name']
        start_date = task['Start Date']
        end_date = task['End Date']
        keyword = task['Git Keyword']
        task_pattern = compile_task_pattern(keyword)

        if not task_pattern:
            logger.debug(f"Skipping task without valid pattern: {task_name}")
            continue

        matched_commits = []
        task_start = datetime.strptime(str(start_date), "%Y-%m-%d")

        for repo in REPOSITORIES:
            if not all(repo.values()):
                continue

            logger.info(f"\n📦 Analyzing Repo: {repo['name']} ({repo['branch']})")


            try:
                all_commits = get_unique_commits_analyzer(
                    repo_owner=repo['owner'],
                    repo_name=repo['name'],
                    base_branch="main",
                    head_branch=repo['branch'],
                    token=GITHUB_TOKEN
                )
            except Exception as e:
                logger.error(f"❌ Failed to fetch commits: {e}")
                continue

            unique_commits = [commit for commit in all_commits if datetime.strptime(commit['commit']['author']['date'][:10], "%Y-%m-%d") >= task_start]

            if not unique_commits:
                logger.warning(f"⚠️ No unique commits in {repo['name']} after task start.")
                continue

            print_commit_info(unique_commits)

            for commit in unique_commits:
                try:
                    commit_msg = commit['commit']['message']
                    keyword_str = str(keyword) if isinstance(keyword, str) and not pd.isna(keyword) else ""

                    if is_related(task_name, keyword_str, commit_msg):
                        matched_commits.append({
                            'sha': commit['sha'],
                            'date': commit['commit']['author']['date'][:10],
                            'author': commit['commit']['author']['name'],
                            'message': commit_msg.strip(),
                            'keyword': keyword_str,
                            'repo_name': repo['name'],
                            'repo_owner': repo['owner']
                        })
                except (KeyError, ValueError) as e:
                    logger.warning(f"⚠️ Commit processing error: {e}")
                    continue

        if not matched_commits:
            logger.info(f"❌ No matching commits for task: {task_name}")
            summary = "No relevant commits found."
        else:
            logger.info(f"✅ Matching commits found for task: {task_name}")
            for commit in matched_commits:
                print(f"🔹 [{commit['date']}] {commit['author']} - {commit['message']} ({commit['keyword']})")

            summaries = []
            for c in matched_commits:
                try:
                    logger.info(f"🧠 Summarizing commit {c['sha']} from {c['repo_name']}...")
                    diff = get_commit_diff(c['repo_owner'], c['repo_name'], c['sha'], GITHUB_TOKEN)

                    if diff.strip():
                        part_summary = summarize_commit(diff, OPENAI_API_KEY, task_name=str(task_name))
                    else:
                        part_summary = "⚠️ Empty diff or no content to summarize."

                    summaries.append(f"🔹 Commit {c['sha'][:7]}:\n{part_summary}")
                    logger.info(f"✅ Summary complete for {c['sha']}")
                except Exception as e:
                    logger.error(f"❌ Summary failed for {c['sha']}: {e}")
                    summaries.append(f"❌ Commit {c['sha'][:7]} failed: {e}")

            summary = "\n\n".join(summaries) if summaries else "No relevant commits found."

        ai_prediction = predict_delay_status(
            task_description=task_name,
            end_date=end_date,
            commit_summary=summary,
            openai_api_key=OPENAI_API_KEY
        )

        logger.info(f"📝 Prediction for '{task_name}': {ai_prediction}")
        task_updates[task_name] = (ai_prediction, summary)

    write_task_updates(SHEET_ID, "Sheet1", task_updates)
    logger.info("✅ Sheet updated with AI predictions and summaries.")

if __name__ == "__main__":
    main()
