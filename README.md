# 🧠 Dev Timeline AI Agent

This project is an AI-powered timeline tracker that reads tasks from a Google Sheet, analyzes matching GitHub commits, summarizes them using OpenAI GPT-4, predicts task delay status, and writes AI-powered insights back into the sheet.

---

## 📌 Features

- ✅ Reads task info from a Google Sheet
- 🔍 Compares GitHub branches to detect new commits
- 🧠 Summarizes diffs using OpenAI GPT-4
- 🔮 Predicts whether a task is on-track or delayed
- ✍️ Writes prediction and summary back to the sheet
- 📂 Logs detailed execution results for audit/debug

---

## 📁 Project Structure

```
.
├── config/             # Google API credentials and tokens
│   ├── credentials.json
│   ├── token.json
│   ├── token.pickle
│   └── README.txt
├── data/               # Data directory (reserved)
│   └── README.txt
├── logs/               # Logs with auto-rotation
│   └── log_YYYY-MM-DD.log
├── modules/            # Core functional modules
│   ├── commit_summarizer.py
│   ├── github_analyzer.py
│   ├── notifier.py
│   ├── predictor.py
│   ├── sheet_reader.py
│   ├── sheet_writer.py
│   ├── timeline_checker.py
│   └── utils.py
├── main.py             # 🔁 Entry point
├── logger_config.py    # Logging setup (file + console)
├── requirements.txt    # Python dependencies
├── README.md           # You're here
└── weam_ai.txt         # Prompt or notes
```

---

## 🔧 Setup

### 1. 📋 Install Python Requirements

```bash
pip install -r requirements.txt
```

---

### 2. 🔑 Configuration

#### Google Sheets API

- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create credentials for Google Sheets API
- Download `credentials.json` and place it in `config/`

---

#### GitHub Token

Use a **classic personal access token** (with `repo` scope).

```bash
export GITHUB_TOKEN="ghp_xxx"
```

---

#### OpenAI API Key

```bash
export OPENAI_API_KEY="sk-xxxx"
```

---

### 3. 🛠️ Set Repositories

Edit `main.py` and set your repositories and branches:

```python
REPOSITORIES = [
    {
        "owner": os.getenv("REPO_1_OWNER", "your-username"),
        "name": os.getenv("REPO_1_NAME", "repo-name"),
        "branch": os.getenv("REPO_1_BRANCH", "feature-branch")
    },
    ...
]
```

---

## 🚀 Run the Agent

```bash
python main.py
```

---

## 📊 Example Output

```
🔄 Fetching tasks from Google Sheet...
✅ Tasks fetched successfully

📦 Analyzing Repo: timeline-service
✅ Matching commits found for task: "Implement calendar sync"

🧠 Summarizing commit 91cd7ac...
✅ Summary: Added Google Calendar sync endpoint

📈 Prediction: 😎 On Track
Completion: 85% ✅, 15% ⏳
```

---

## 📂 Logs

All activity is logged with timestamps:
```
logs/log_2025-06-19.log
```

---

## 🧱 Dependencies

- `openai`
- `google-api-python-client`
- `google-auth`, `google-auth-oauthlib`
- `pandas`
- `requests`
- `python-dotenv` (optional)

---

## 🔒 .env Example (Optional)

You can use a `.env` file to store secrets:

```env
GITHUB_TOKEN=your-git-classic-token
GITHUB_OWNER=your-github-username-or-org
GITHUB_REPO=your-repo-name
GITHUB_BRANCH=your-feature-branch-name

GOOGLE_TOKEN_PATH=config/token.pickle
CREDENTIALS_PATH=config/credentials.json
TOKEN_PATH=config/token.json

# API KEYS
OPENAI_API_KEY=your-openai-api-key
GITHUB_TOKEN=your-github-token

# GOOGLE SHEET CONFIG
SHEET_ID=your-google-sheet-id
SHEET_RANGE=Sheet1!A:E

# REPO 1
REPO_1_OWNER=example-org
REPO_1_NAME=example-repo
REPO_1_BRANCH=feature-branch

# REPO 2
REPO_2_OWNER=example-org
REPO_2_NAME=another-repo
REPO_2_BRANCH=dev-branch

# REPO 3
REPO_3_OWNER=example-org
REPO_3_NAME=third-repo
REPO_3_BRANCH=bugfix-branch

LOG_LEVEL=DEBUG
LOG_FILE=logs/application.log
```

---

## 🙌 Author

**Dhruvish Patel**  
Backend Developer | AI Automator  
📧 Contact: [LinkedIn](https://linkedin.com/in/your-profile) | [GitHub](https://github.com/your-handle)

---

## 📄 License

For personal or internal use only. Not licensed for public redistribution.
