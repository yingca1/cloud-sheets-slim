import logging
logging.basicConfig(level=logging.INFO)

from .google_sheets import GoogleSheets
from .lark_sheets import LarkSheets
from .pandas_proxy import PandasProxy

logger = logging.getLogger(__name__)

class CloudSheetsSlim:
    def __init__(self, spreadsheet_url=None, sheet_name="Sheet1") -> None:
        self.cloud_sheet = None
        if spreadsheet_url:
            self.set_remote(spreadsheet_url, sheet_name)


    def set_remote(self, spreadsheet_url, sheet_name="Sheet1"):
        if not spreadsheet_url:
            raise Exception("spreadsheet_url is required")

        if GoogleSheets.is_vaild_url(spreadsheet_url):
            self.cloud_sheet = GoogleSheets(spreadsheet_url, sheet_name)
        elif LarkSheets.is_valid_url(spreadsheet_url):
            self.cloud_sheet = LarkSheets(spreadsheet_url, sheet_name)
        else:
            raise Exception("spreadsheet_url is not supported")
        return self

    def push_df(self, df):
        if not self.cloud_sheet:
            raise Exception("cloud_sheet is not set")

        self.cloud_sheet.push_df_to_sheet(df)
        self.cloud_sheet.snapshot_df = df.copy()

    def to_pdp(self):
        if not self.cloud_sheet:
            raise Exception("cloud_sheet is not set")

        all_records = self.cloud_sheet.pull_sheet_to_df()
        self.cloud_sheet.snapshot_df = all_records.copy()
        return PandasProxy(all_records)
