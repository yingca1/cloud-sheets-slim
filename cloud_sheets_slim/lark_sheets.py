"""
Lark Sheets API implementation using the latest lark_oapi client.

Documentation:
- https://open.larksuite.com/document/server-docs/docs/sheets-v3/guide/overview
- https://open.larksuite.com/document/server-docs/docs/sheets-v3/data-operation/reading-a-single-range
- https://open.larksuite.com/document/server-docs/docs/sheets-v3/data-operation/write-data-to-a-single-range
- https://open.larksuite.com/document/server-docs/docs/sheets-v3/data-operation/reading-multiple-ranges
- https://open.larksuite.com/document/server-docs/docs/sheets-v3/data-operation/write-data-to-multiple-ranges
"""
import os
import json
from typing import List, Dict, Any, Optional
import pandas as pd
import lark_oapi as lark
from .cloud_sheets_base import CloudSheetsBase
import logging

logger = logging.getLogger(__name__)

class LarkSheets(CloudSheetsBase):
    def __init__(self, spreadsheet_url: str, sheet_name: str):
        """Initialize LarkSheets with spreadsheet URL and sheet name.
        
        Args:
            spreadsheet_url: The URL of the Lark/Feishu spreadsheet
            sheet_name: The name of the sheet to operate on
        """
        app_id = os.getenv("LARK_APP_ID")
        app_secret = os.getenv("LARK_APP_SECRET")
        
        if not app_id or not app_secret:
            raise ValueError("LARK_APP_ID and LARK_APP_SECRET environment variables are required")

        # Initialize lark client
        self.client = lark.Client.builder() \
            .app_id(app_id) \
            .app_secret(app_secret) \
            .log_level(lark.LogLevel.INFO) \
            .build()
        
        self.spreadsheet_token = self._extract_token_from_url(spreadsheet_url)
        self.sheet_name = sheet_name
        self.sheet_id = self._get_sheet_id(sheet_name)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if the URL is a valid Lark Sheets URL."""
        return "feishu.cn/sheets" in url or "larksuite.com/sheets" in url

    @staticmethod
    def _extract_token_from_url(url: str) -> str:
        """Extract spreadsheet token from Lark Sheets URL."""
        if "sheets/" not in url:
            raise ValueError("Invalid Lark Sheets URL")
        return url.split("sheets/")[1].split("/")[0]

    def _get_sheet_id(self, sheet_name: str) -> str:
        """Get sheet ID by sheet name."""
        req = lark.BaseRequest.builder() \
            .http_method(lark.HttpMethod.GET) \
            .uri(f"/open-apis/sheets/v2/spreadsheets/{self.spreadsheet_token}/metainfo") \
            .token_types({lark.AccessTokenType.TENANT}) \
            .build()
        
        resp = self.client.request(req)
        if not resp.success():
            raise Exception(f"Failed to get sheet info: {resp.msg}")
        
        sheets = json.loads(str(resp.raw.content, lark.UTF_8)).get("data", {}).get("sheets", [])
        for sheet in sheets:
            if sheet.get("title") == sheet_name:
                return sheet.get("sheetId")
        raise ValueError(f"Sheet '{sheet_name}' not found")

    def _read_range(self, cell_range: Optional[str] = None) -> Dict:
        """Read data from a single range.
        
        Args:
            cell_range: Optional cell range in A1 notation (e.g. 'A1:B2'). 
                       If None, reads entire sheet.
        """
        # Construct range string according to API spec
        range_str = self.sheet_id
        if cell_range:
            range_str = f"{self.sheet_id}!{cell_range}"
            
        req = lark.BaseRequest.builder() \
            .http_method(lark.HttpMethod.GET) \
            .uri(f"/open-apis/sheets/v2/spreadsheets/{self.spreadsheet_token}/values/{range_str}") \
            .token_types({lark.AccessTokenType.APP}) \
            .build()
        
        resp = self.client.request(req)
        if not resp.success():
            raise Exception(f"Failed to read range: {resp.msg}")
        
        return json.loads(str(resp.raw.content, lark.UTF_8)).get("data", {})

    def _write_range(self, range_str: str, values: List[List[Any]]) -> Dict:
        """Write data to a single range."""
        # Ensure range includes sheet name
        if "!" not in range_str:
            range_str = f"{self.sheet_id}!{range_str}"
            
        body = {
            "valueRange": {
                "range": range_str,
                "values": values
            }
        }
        
        req = lark.BaseRequest.builder() \
            .http_method(lark.HttpMethod.PUT) \
            .uri(f"/open-apis/sheets/v2/spreadsheets/{self.spreadsheet_token}/values") \
            .token_types({lark.AccessTokenType.APP}) \
            .body(body) \
            .build()
        
        resp = self.client.request(req)
        if not resp.success():
            raise Exception(f"Failed to write range: {resp.msg}")
        
        return json.loads(str(resp.raw.content, lark.UTF_8)).get("data", {})

    def _read_ranges(self, ranges: List[str]) -> Dict:
        """Read data from multiple ranges."""
        ranges_str = ",".join(ranges)
        req = lark.BaseRequest.builder() \
            .http_method(lark.HttpMethod.GET) \
            .uri(f"/open-apis/sheets/v2/spreadsheets/{self.spreadsheet_token}/values_batch_get") \
            .query_params({"ranges": ranges_str}) \
            .token_types({lark.AccessTokenType.APP}) \
            .build()
        
        resp = self.client.request(req)
        if not resp.success():
            raise Exception(f"Failed to read ranges: {resp.msg}")
        
        return json.loads(str(resp.raw.content, lark.UTF_8)).get("data", {})

    def _write_ranges(self, range_data: List[Dict[str, Any]]) -> Dict:
        """Write data to multiple ranges."""
        body = {"valueRanges": range_data}
        
        req = lark.BaseRequest.builder() \
            .http_method(lark.HttpMethod.PUT) \
            .uri(f"/open-apis/sheets/v2/spreadsheets/{self.spreadsheet_token}/values_batch_update") \
            .token_types({lark.AccessTokenType.APP}) \
            .body(body) \
            .build()
        
        resp = self.client.request(req)
        if not resp.success():
            raise Exception(f"Failed to write ranges: {resp.msg}")
        
        return json.loads(str(resp.raw.content, lark.UTF_8)).get("data", {})

    def pull_sheet_to_df(self) -> pd.DataFrame:
        """Read entire sheet into a DataFrame."""
        data = self._read_range()  # No range needed, will read entire sheet
        values = data.get("valueRange", {}).get("values", [])
        
        if not values:
            return pd.DataFrame()

        # First row as columns
        columns = values[0]
        data = values[1:]
        
        df = pd.DataFrame(data, columns=columns)
        return df.fillna("")

    def _delete_rows(self, start_row: int, row_count: int) -> None:
        """Delete rows from the sheet."""
        body = {
            "dimension": {
                "sheetId": self.sheet_id,
                "majorDimension": "ROWS",
                "startIndex": start_row + 2,  # Convert to 0-based index
                "endIndex": start_row + 2 + row_count  # endIndex is exclusive
            }
        }
        
        req = lark.BaseRequest.builder() \
            .http_method(lark.HttpMethod.DELETE) \
            .uri(f"/open-apis/sheets/v2/spreadsheets/{self.spreadsheet_token}/dimension_range") \
            .token_types({lark.AccessTokenType.APP}) \
            .body(body) \
            .build()
        
        resp = self.client.request(req)
        if not resp.success():
            raise Exception(f"Failed to delete rows: {resp.msg}")

    def _delete_columns(self, start_col: int, col_count: int) -> None:
        """Delete columns from the sheet."""
        body = {
            "dimension": {
                "sheetId": self.sheet_id,
                "majorDimension": "COLUMNS",
                "startIndex": start_col + 1,  # Convert to 0-based index
                "endIndex": start_col + 1 + col_count  # endIndex is exclusive
            }
        }
        
        req = lark.BaseRequest.builder() \
            .http_method(lark.HttpMethod.DELETE) \
            .uri(f"/open-apis/sheets/v2/spreadsheets/{self.spreadsheet_token}/dimension_range/delete") \
            .token_types({lark.AccessTokenType.APP}) \
            .body(body) \
            .build()
        
        resp = self.client.request(req)
        if not resp.success():
            raise Exception(f"Failed to delete columns: {resp.msg}")

    def push_df_to_sheet(self, df):
        """Write DataFrame to sheet."""
        # Prepare data: columns and values
        values = [df.columns.tolist()] + df.values.tolist()
        
        # Calculate dimensions
        new_df_rows = len(df)  # DataFrame rows (without header)
        new_cols = len(df.columns)
        old_df_rows = len(self.snapshot_df) if hasattr(self, 'snapshot_df') else 0
        old_cols = len(self.snapshot_df.columns) if hasattr(self, 'snapshot_df') and not self.snapshot_df.empty else 0
        
        # Write new data
        end_col = chr(ord('A') + new_cols - 1) if new_cols > 0 else 'A'
        range_str = f"{self.sheet_id}!A1:{end_col}{new_df_rows + 1}"  # +1 for header row
        self._write_range(range_str, values)
        
        # Delete extra rows if new data has fewer rows
        if old_df_rows > new_df_rows:
            self._delete_rows(new_df_rows, old_df_rows - new_df_rows)
            
        # Delete extra columns if new data has fewer columns
        if old_cols > new_cols:
            self._delete_columns(new_cols, old_cols - new_cols)
        
        logger.info(f"Pushed {len(df)} records to Lark Sheets")
