import unittest
import os
import gspread
import uuid
import logging
from dotenv import load_dotenv
from cloud_sheets_slim.google_sheets import GoogleSheets

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class TestGoogleSheets(unittest.TestCase):
    def setUp(self):
        # self.create_test_spreadsheet()
        test_google_spreadsheet_url = os.environ.get("TEST_GOOGLE_SPREADSHEET_URL")
        test_google_sheet_name = os.environ.get("TEST_GOOGLE_SHEET_NAME", "Sheet1")
        self.sheet = GoogleSheets(test_google_spreadsheet_url, test_google_sheet_name)

    def create_test_spreadsheet(self, name="test_spreadsheet"):
        gc = gspread.service_account(
            filename=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        )
        sh = gc.create(name)
        test_google_account = os.environ.get("TEST_GOOGLE_ACCOUNT", None)
        if test_google_account:
            sh.share(test_google_account, perm_type="user", role="writer")
        logger.info(f"Create worksheet {name} successfully, id: {sh.id}")

    def test_insert_one(self):
        unique_id = str(uuid.uuid4())
        test_record = {
            "_id": unique_id,
            "key3": "value3",
            # "key1": "value1",
            # "key2": "value2",
            # "key4": "value4",
            "key5": "value5",
        }
        self.sheet.insert_one(test_record)
        result = self.sheet.find_one({"_id": unique_id})
        self.assertEqual(result, test_record)

    def test_insert_many(self):
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
        self.sheet.insert_many(records)

        for record in records:
            result = self.sheet.find_one({"_id": record["_id"]})
            self.assertEqual(result, record)

    def test_find_one(self):
        # Insert a record to find
        unique_id = str(uuid.uuid4())
        test_record = {
            "_id": unique_id,
            "key3": "value3",
            "key5": "value5",
        }
        self.sheet.insert_one(test_record)

        # Find the inserted record
        result = self.sheet.find_one({"_id": unique_id})

        # Check if the result is not None
        self.assertIsNotNone(result)

        # Check if the result has the correct keys and values
        self.assertEqual(result, test_record)

    def test_find(self):
        # Generate a unique value for key1
        unique_value = str(uuid.uuid4())

        # Insert multiple records
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
        self.sheet.insert_many(records)

        # Find the inserted records
        result = self.sheet.find({"key1": unique_value})

        # Check if the result list is not empty
        self.assertTrue(result)

        # Check if all records in the result list have 'key1' value as the unique value
        for record in result:
            self.assertEqual(record["key1"], unique_value)

        # Check if the first record in the result list is in the inserted records
        self.assertIn(result[0], records)

    def test_get_all_records(self):
        res = self.sheet.find({})
        logger.info(res)

    def test_delete_one(self):
        # Insert a record to delete
        unique_id = str(uuid.uuid4())
        test_record = {
            "_id": unique_id,
            "key3": "value3",
            "key5": "value5",
        }
        self.sheet.insert_one(test_record)

        # Delete the inserted record
        self.sheet.delete_one({"_id": unique_id})

        # Try to find the deleted record
        result = self.sheet.find_one({"_id": unique_id})

        # Check if the result is None
        self.assertIsNone(result)

    def test_delete_many(self):
        # Generate a unique value for key1
        unique_value = str(uuid.uuid4())

        # Insert multiple records
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
        self.sheet.insert_many(records)

        # Delete the inserted records
        self.sheet.delete_many({"key1": unique_value})

        # Try to find the deleted records
        result = self.sheet.find({"key1": unique_value})

        # Check if the result list is empty
        self.assertFalse(result)

    def test_update_one(self):
        # Insert a record to update
        unique_id = str(uuid.uuid4())
        test_record = {
            "_id": unique_id,
            "key1": "value1",
            "key2": "value2",
        }
        self.sheet.insert_one(test_record)

        # Update the inserted record
        self.sheet.update_one(
            {"_id": unique_id}, {"key1": "new_value1", "key2": "new_value2"}
        )

        # Find the updated record
        result = self.sheet.find_one({"_id": unique_id})

        # Check if the update was successful
        self.assertEqual(result["key1"], "new_value1")
        self.assertEqual(result["key2"], "new_value2")

    def test_update_many(self):
        # Insert multiple records to update
        unique_value = str(uuid.uuid4())
        records = [
            {
                "_id": str(uuid.uuid4()),
                "key1": unique_value,
                "key2": "value2",
            },
            {
                "_id": str(uuid.uuid4()),
                "key1": unique_value,
                "key2": "value3",
            },
        ]
        self.sheet.insert_many(records)

        # Update the inserted records
        self.sheet.update_many(
            {"key1": unique_value}, {"key1": "new_value1", "key2": "new_value2"}
        )

        # Find the updated records
        results = self.sheet.find({"key1": "new_value1"})

        # Check if the update was successful for all records
        for result in results:
            self.assertEqual(result["key1"], "new_value1")
            self.assertEqual(result["key2"], "new_value2")

    def test_replace_one(self):
        # Insert a record to replace
        unique_id = str(uuid.uuid4())
        test_record = {
            "_id": unique_id,
            "key1": "value1",
            "key2": "value2",
        }
        self.sheet.insert_one(test_record)

        # Replace the inserted record
        new_record = {
            "_id": unique_id,
            "key1": "new_value1",
            "key2": "new_value2",
            "key3": "new_value3",
        }
        self.sheet.replace_one({"_id": unique_id}, new_record)

        # Find the replaced record
        result = self.sheet.find_one({"_id": unique_id})

        # Check if the replacement was successful
        self.assertEqual(result, new_record)

    def test_count_records(self):
        # Insert multiple records with key3 as "value333"
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
        self.sheet.insert_many(records)

        # Insert a record with key3 as "value444" to ensure the count function works correctly
        unique_id = str(uuid.uuid4())
        test_record = {
            "_id": unique_id,
            "key1": "value1",
            "key2": "value2",
            "key3": "value444",
        }
        self.sheet.insert_one(test_record)

        # Count the records with key3 as "value333"
        count = self.sheet.count_records({"key3": "value333"})
        logger.info(count)

        # Assert that the count is correct
        self.assertEqual(count, 2)
