from datetime import datetime
from logger_config import logger

def check_timeline_status(task_row, matched_commits):
    task_keyword = task_row['Git Keyword']
    today = datetime.today()

    # Validate that Start Date and End Date exist
    if not task_row['Start Date'] or not task_row['End Date']:
        logger.warning("Start or End Date missing for task.")
        return "❌ Missing timeline info (Start or End Date)"

    try:
        start_date = datetime.strptime(task_row['Start Date'], "%Y-%m-%d")
        end_date = datetime.strptime(task_row['End Date'], "%Y-%m-%d")
    except Exception:
        logger.error(f"Date parsing error: {e}")
        return "❌ Invalid date format"

    relevant_commits = [c for c in matched_commits if c['keyword'] == task_keyword]

    if not relevant_commits:
        if today < start_date:
            return "🟡 Upcoming"
        elif start_date <= today <= end_date:
            return "⚠️ No progress (in progress phase)"
        else:
            return "❌ Delayed (no commits)"

    try:
        latest_commit_date = max(datetime.strptime(c['date'], "%Y-%m-%d") for c in relevant_commits)
    except Exception as e:
        logger.error(f"Commit date parsing failed: {e}")
        return "❌ Error in commit dates"

    if latest_commit_date <= end_date:
        return "✅ On Track"
    else:
        days_late = (latest_commit_date - end_date).days
        return f"❌ Delayed by {days_late} day(s)"
