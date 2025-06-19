import os
import pandas as pd
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from logger_config import logger
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']



TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", "config/token.pickle")

def read_google_sheet(sheet_id, sheet_range):
    try:
        creds = None
        token_path = os.getenv("GOOGLE_TOKEN_PATH", "config/token.pickle")

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
                logger.info("✅ Loaded credentials from token.pickle.")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'config/client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        result = sheet.values().get(spreadsheetId=sheet_id,
                                    range=sheet_range).execute()
        values = result.get('values', [])

        if not values:
            logger.warning("⚠️ No data found in the sheet.")
            return pd.DataFrame()

        headers = values[0]
        rows = values[1:]
        return pd.DataFrame(rows, columns=headers)
    except Exception as e:
        logger.error(f"❌ Failed to read Google Sheet: {e}")
        return pd.DataFrame()
