import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from .cloud_sheets_base import CloudSheetsBase
import logging

logger = logging.getLogger(__name__)


class GoogleSheets(CloudSheetsBase):
    def __init__(self, spreadsheet_url, sheet_name):
        json_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        client = self.authenticate_google_sheets(json_file)
        self.worksheet = client.open_by_url(spreadsheet_url).worksheet(sheet_name)

    def authenticate_google_sheets(self, json_file):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)
        client = gspread.authorize(creds)
        return client

    def _get_all_records(self):
        return pd.DataFrame(self.worksheet.get_all_records())

    def _update_all_records(self, df):
        self.worksheet.clear()
        data = [df.columns.tolist()] + df.values.tolist()
        self.worksheet.append_rows(data)

    def _get_header(self):
        return self.worksheet.row_values(1)

    def find_one(self, query):
        df = self._get_all_records()

        for key, value in query.items():
            df = df[df[key] == value]

        result = df.head(1).to_dict("records")[0] if not df.empty else None

        if result is None:
            return None

        result = {k: v for k, v in result.items() if v != ""}

        return result

    def find(self, query={}):
        df = self._get_all_records()

        for key, value in query.items():
            df = df[df[key] == value]

        result = df.to_dict("records") if not df.empty else []
        result = [{k: v for k, v in res.items() if v != ""} for res in result]

        return result

    def insert_one(self, record):
        header = self._get_header()
        record_keys = list(record.keys())

        if not header:
            self.worksheet.insert_row(record_keys, 1)
        else:
            new_keys = [key for key in record_keys if key not in header]
            if new_keys:
                header.extend(new_keys)
                self.worksheet.delete_rows(1)
                self.worksheet.insert_row(header, 1)

        values = [record.get(key) for key in header]
        self.worksheet.append_row(values)

    def insert_many(self, records):
        header = self._get_header()
        if not header:
            self.worksheet.insert_row(list(records[0].keys()), 1)
            header = list(records[0].keys())

        for record in records:
            record_keys = list(record.keys())
            new_keys = [key for key in record_keys if key not in header]
            if new_keys:
                self.worksheet.insert_row(new_keys, len(header) + 1)
                header.extend(new_keys)

        rows = [list(record.get(key) for key in header) for record in records]
        self.worksheet.append_rows(rows)

    def replace_one(self, query, new_record):
        df = self._get_all_records()

        mask = (df[list(query.keys())] == pd.Series(query)).all(axis=1)
        idx = df[mask].index

        if not idx.empty:
            for key, value in new_record.items():
                col = df.columns.get_loc(key) + 1
                self.worksheet.update_cell(int(idx[0]) + 2, col, value)

    def update_one(self, query, new_items, upsert=False):
        df = self._get_all_records()

        for key, value in query.items():
            df = df[df[key] == value]

        idx = df.index

        if not idx.empty:
            for key, value in new_items.items():
                if key not in df.columns:
                    self.worksheet.add_cols(1)
                    self.worksheet.update_cell(1, len(df.columns) + 1, key)
                    df.columns = self._get_header()
                self.worksheet.update_cell(
                    idx[0] + 2, df.columns.get_loc(key) + 1, value
                )
        elif upsert:
            new_row = {**query, **new_items}
            self.insert_one(new_row)

    def update_many(self, query, update, upsert=False):
        df = self._get_all_records()

        if df.empty and upsert:
            self.insert_one({**query, **update})
            return

        if not set(query.keys()).issubset(df.columns):
            raise KeyError("Some query keys are not in the DataFrame")

        mask = (df[list(query.keys())] == pd.Series(query)).all(axis=1)
        matching_rows = df[mask]

        if not matching_rows.empty:
            df.update(matching_rows.assign(**update))

        if upsert and matching_rows.empty:
            new_row = {**query, **update}
            df = df.append(new_row, ignore_index=True)

        self._update_all_records(df)

    def delete_one(self, query):
        df = self._get_all_records()

        for key, value in query.items():
            df = df[df[key] == value]

        idx = df.index

        if not idx.empty:
            row_to_delete = int(idx[0]) + 2
            self.worksheet.delete_rows(row_to_delete)

    def delete_many(self, query):
        df = self._get_all_records()

        mask = (df[list(query.keys())] == pd.Series(query)).all(axis=1)
        idx_list = df[mask].index.tolist()

        for idx in reversed(idx_list):
            self.worksheet.delete_rows(int(idx) + 2)

    def count_records(self, query={}):
        df = self._get_all_records()

        if query:
            mask = (df[list(query.keys())] == pd.Series(query)).all(axis=1)
            return len(df[mask])
        else:
            return len(df)
