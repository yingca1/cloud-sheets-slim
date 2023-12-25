import os
import gspread
import uuid
import logging
from dotenv import load_dotenv
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from cloud_sheets_slim import CloudSheetsSlim

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


# Setup function
def setup_module(module):
    global sheets
    global pdp
    # self.create_test_spreadsheet()
    test_google_spreadsheet_url = os.environ.get("TEST_GOOGLE_SPREADSHEET_URL")
    test_google_sheet_name = os.environ.get("TEST_GOOGLE_SHEET_NAME", "Sheet1")
    sheets = CloudSheetsSlim(test_google_spreadsheet_url, test_google_sheet_name)
    pdp = sheets.to_pdp()


def create_test_spreadsheet(name="test_spreadsheet"):
    gc = gspread.service_account(
        filename=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    )
    sh = gc.create(name)
    test_google_account = os.environ.get("TEST_GOOGLE_ACCOUNT", None)
    if test_google_account:
        sh.share(test_google_account, perm_type="user", role="writer")
    logger.info(f"Create worksheet {name} successfully, id: {sh.id}")


def test_push_to_remote():
    unique_id = str(uuid.uuid4())
    test_record = {
        "_id": unique_id,
        "key3": "value3",
        "key5": "value5",
    }
    pdp.insert_one(test_record)
    result = pdp.find_one({"_id": unique_id})
    assert result == test_record

    sheets.push_df(pdp.get_df())

    new_pdp = sheets.to_pdp()
    assert new_pdp.find_one({"_id": unique_id}) == test_record
