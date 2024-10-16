"""
https://docs.gspread.org/en/latest/index.html
"""
import os
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from .cloud_sheets_base import CloudSheetsBase
import logging

logger = logging.getLogger(__name__)


class GoogleSheets(CloudSheetsBase):
    def __init__(self, spreadsheet_url, sheet_name):
        gcp_json_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = Credentials.from_service_account_file(
            gcp_json_key,
            scopes=scopes
        )
        self.gc = gspread.authorize(credentials)
        self.sh = self.gc.open_by_url(spreadsheet_url)
        self.worksheet = self.sh.worksheet(sheet_name)

    @staticmethod
    def is_vaild_url(url):
        return url.startswith("https://docs.google.com/spreadsheets/")

    def pull_sheet_to_df(self):
        df = pd.DataFrame(self.worksheet.get_all_records())
        df = df.set_index(0).fillna("")
        return df

    def push_df_to_sheet(self, df):
        self.worksheet.clear()
        self.worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        logger.info(f"Pushed {len(df)} records to Google Sheets")
