from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from logger_config import logger
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_PATH = os.getenv("GOOGLE_TOKEN_PATH", "config/credentials.json")
TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", "config/token.json")
def get_oauth_credentials(credentials_path=CREDENTIALS_PATH, token_path=TOKEN_PATH):
    creds = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
            logger.info("✅ Loaded credentials from token.")
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            logger.info("🔄 Refreshed expired credentials.")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            logger.info("🆕 Obtained new credentials.")
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
            logger.info("💾 Saved new credentials to token file.")
    return creds

def write_task_updates(sheet_id, worksheet_name, task_updates, credentials_path='config/credentials.json'):
    try:
        credentials = get_oauth_credentials(credentials_path)

        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        # Fetch header row
        result = sheet.values().get(spreadsheetId=sheet_id, range=f"{worksheet_name}!A1:Z1").execute()
        header = result.get('values', [])[0]

        today = datetime.today().strftime('%Y-%m-%d')
        status_col = f"{today} Status"
        summary_col = f"{today} Summary"

        # Add columns if missing
        modified = False
        if status_col not in header:
            header.append(status_col)
            modified = True
        if summary_col not in header:
            header.append(summary_col)
            modified = True

        if modified:
            sheet.values().update(
                spreadsheetId=sheet_id,
                range=f"{worksheet_name}!A1",
                valueInputOption="RAW",
                body={"values": [header]}
            ).execute()

        # Get all task rows
        result = sheet.values().get(spreadsheetId=sheet_id, range=f"{worksheet_name}!A2:{chr(65+len(header))}").execute()
        rows = result.get('values', [])

        status_index = header.index(status_col)
        summary_index = header.index(summary_col)

        updates = []
        for row in rows:
            task_name = row[0] if len(row) > 0 else ""
            status, summary = task_updates.get(task_name, ("", ""))
            updates.append([status, summary])  # ✅ Clean and flat row with two values

        # Write only the new two columns
        col_start = chr(65 + status_index)
        col_end = chr(65 + summary_index)
        range_to_update = f"{worksheet_name}!{col_start}2:{col_end}{1 + len(rows)}"

        sheet.values().update(
            spreadsheetId=sheet_id,
            range=range_to_update,
            valueInputOption="RAW",
            body={"values": updates}
        ).execute()

        logger.info(f"✅ Successfully updated {len(updates)} tasks to Google Sheet.")
    except Exception as e:
        logger.error(f"❌ Failed to write task updates to Google Sheet: {e}")