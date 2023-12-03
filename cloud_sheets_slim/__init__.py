import logging
logging.basicConfig(level=logging.INFO)

from .google_sheets import GoogleSheets

logger = logging.getLogger(__name__)

class CloudSheetsSlim:
    def __init__(self, spreadsheet_url, sheet_name="Sheet1") -> None:
        self.cloud_sheet = GoogleSheets(spreadsheet_url, sheet_name)

    def insert_one(self, record):
        self.cloud_sheet.insert_one(record)

    def insert_many(self, records):
        self.cloud_sheet.insert_many(records)

    def find_one(self, query):
        return self.cloud_sheet.find_one(query)

    def find(self, query):
        return self.cloud_sheet.find(query)

    def update_one(self, query, update, upsert=False):
        return self.cloud_sheet.update_one(query, update, upsert)

    def update_many(self, query, update, upsert=False):
        return self.cloud_sheet.update_many(query, update, upsert)

    def replace_one(self, query, replacement):
        return self.cloud_sheet.replace_one(query, replacement)

    def delete_one(self, query):
        return self.cloud_sheet.delete_one(query)

    def delete_many(self, query):
        return self.cloud_sheet.delete_many(query)

    def delete_all(self):
        return self.cloud_sheet.delete_all()

    def get_all_records(self):
        return self.cloud_sheet.get_all_records()
