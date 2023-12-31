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
    test_google_spreadsheet_url = os.environ.get("TEST_GOOGLE_SPREADSHEET_URL")
    test_google_sheet_name = os.environ.get("TEST_GOOGLE_SHEET_NAME", "Sheet1")
    sheets = CloudSheetsSlim(test_google_spreadsheet_url, test_google_sheet_name)
    pdp = sheets.to_pdp()


def test_insert_one():
    unique_id = str(uuid.uuid4())
    test_record = {
        "_id": unique_id,
        "key3": "value3",
        "key5": "value5",
    }
    pdp.insert_one(test_record)
    result = pdp.find_one({"_id": unique_id})
    assert result == test_record


def test_insert_many():
    records = [
        {
            "_id": str(uuid.uuid4()),
            "key1": "value12",
            "key3": "value32",
            "key2": "value22",
        },
        {
            "_id": str(uuid.uuid4()),
            "key1": "value13",
            "key3": "value33",
            "key2": "value23",
        },
    ]
    pdp.insert_many(records)
    for record in records:
        result = pdp.find_one({"_id": record["_id"]})
        assert result == record


def test_find_one():
    unique_id = str(uuid.uuid4())
    test_record = {"_id": unique_id, "key3": "value3", "key5": "value5"}
    pdp.insert_one(test_record)
    result = pdp.find_one({"_id": unique_id})
    assert result is not None
    assert result == test_record


def test_find():
    unique_value = str(uuid.uuid4())
    records = [
        {
            "_id": str(uuid.uuid4()),
            "key1": unique_value,
            "key3": "value32",
            "key2": "value22",
        },
        {
            "_id": str(uuid.uuid4()),
            "key1": "value13",
            "key3": "value33",
            "key2": "value23",
        },
    ]
    pdp.insert_many(records)
    result = pdp.find({"key1": unique_value})
    assert result
    for record in result:
        assert record["key1"] == unique_value
    assert result[0] in records


def test_get_all_records():
    res = pdp.find({})
    logger.info(res)


def test_delete_one():
    unique_id = str(uuid.uuid4())
    test_record = {"_id": unique_id, "key3": "value3", "key5": "value5"}
    pdp.insert_one(test_record)
    pdp.delete_one({"_id": unique_id})
    result = pdp.find_one({"_id": unique_id})
    assert result is None


def test_delete_many():
    unique_value = str(uuid.uuid4())
    records = [
        {
            "_id": str(uuid.uuid4()),
            "key1": unique_value,
            "key3": "value32",
            "key2": "value22",
        },
        {
            "_id": str(uuid.uuid4()),
            "key1": unique_value,
            "key3": "value33",
            "key2": "value23",
        },
    ]
    pdp.insert_many(records)
    pdp.delete_many({"key1": unique_value})
    result = pdp.find({"key1": unique_value})
    assert not result


def test_update_one():
    unique_id = str(uuid.uuid4())
    test_record = {"_id": unique_id, "key1": "value1", "key2": "value2"}
    pdp.insert_one(test_record)
    pdp.update_one(
        {"_id": unique_id}, {"key1": "new_value1", "key2": "new_value2"}
    )
    result = pdp.find_one({"_id": unique_id})
    assert result["key1"] == "new_value1"
    assert result["key2"] == "new_value2"


def test_update_one_with_upsert():
    random_id = str(uuid.uuid4())
    random_key = str(uuid.uuid4())
    update_record = {
        "key1": "new_value1_upsert",
        "key2": "new_value2_upsert",
        random_key: random_key,
    }
    pdp.update_one({"_id": random_id}, update_record, upsert=True)
    result = pdp.find_one({"_id": random_id})
    assert result["key1"] == "new_value1_upsert"
    assert result["key2"] == "new_value2_upsert"
    assert result[random_key] == random_key


def test_update_many():
    unique_value = str(uuid.uuid4())
    records = [
        {"_id": str(uuid.uuid4()), "key1": unique_value, "key2": "value2"},
        {"_id": str(uuid.uuid4()), "key1": unique_value, "key2": "value3"},
    ]
    pdp.insert_many(records)
    pdp.update_many(
        {"key1": unique_value}, {"key1": "new_value1", "key2": "new_value2"}
    )
    results = pdp.find({"key1": "new_value1"})
    for result in results:
        assert result["key1"] == "new_value1"
        assert result["key2"] == "new_value2"


def test_replace_one():
    unique_id = str(uuid.uuid4())
    test_record = {"_id": unique_id, "key1": "value1", "key2": "value2"}
    pdp.insert_one(test_record)
    new_record = {
        "_id": unique_id,
        "key1": "new_value1",
        "key2": "new_value2",
        "key3": "new_value3",
    }
    pdp.replace_one({"_id": unique_id}, new_record)
    result = pdp.find_one({"_id": unique_id})
    assert result == new_record


def test_count_records():
    records = [
        {
            "_id": str(uuid.uuid4()),
            "key1": "value1",
            "key2": "value2",
            "key3": "value333",
        },
        {
            "_id": str(uuid.uuid4()),
            "key1": "value1",
            "key2": "value2",
            "key3": "value333",
        },
    ]
    pdp.insert_many(records)
    unique_id = str(uuid.uuid4())
    test_record = {
        "_id": unique_id,
        "key1": "value1",
        "key2": "value2",
        "key3": "value444",
    }
    pdp.insert_one(test_record)
    count = pdp.count_records({"key3": "value333"})
    logger.info(count)
    assert count == 2
