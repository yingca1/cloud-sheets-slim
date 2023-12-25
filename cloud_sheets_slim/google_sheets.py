import os
from gspread_pandas import Spread, Client
from oauth2client.service_account import ServiceAccountCredentials
from .cloud_sheets_base import CloudSheetsBase
import logging

logger = logging.getLogger(__name__)


class GoogleSheets(CloudSheetsBase):
    def __init__(self, spreadsheet_url, sheet_name):
        json_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)
        self.spread = Spread(spreadsheet_url, sheet_name, creds=creds)

    def pull_sheet_to_df(self):
        return self.spread.sheet_to_df(index=0, header_rows=1).fillna("")

    def push_df_to_sheet(self, df):
        self.spread.df_to_sheet(df, index=False, sheet=self.spread.sheet)
        logger.info(f"Pushed {len(df)} records to Google Sheets")
