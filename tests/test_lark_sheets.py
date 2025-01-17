import os
import uuid
import logging
import pytest
from dotenv import load_dotenv
import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from cloud_sheets_slim import CloudSheetsSlim

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


@pytest.fixture(scope="module")
def lark_sheets():
    """Setup test Lark Sheets instance."""
    test_lark_spreadsheet_url = os.environ.get("TEST_LARK_SPREADSHEET_URL")
    test_lark_sheet_name = os.environ.get("TEST_LARK_SHEET_NAME", "Sheet1")
    
    if not test_lark_spreadsheet_url:
        pytest.skip("TEST_LARK_SPREADSHEET_URL not set")
    
    return CloudSheetsSlim(test_lark_spreadsheet_url, test_lark_sheet_name)


@pytest.fixture(scope="module")
def pdp(lark_sheets):
    """Get pandas proxy instance."""
    return lark_sheets.to_pdp()


def test_initialization_without_credentials():
    """Test initialization without API credentials."""
    # Temporarily unset environment variables
    app_id = os.environ.pop("LARK_APP_ID", None)
    app_secret = os.environ.pop("LARK_APP_SECRET", None)
    
    with pytest.raises(ValueError, match="LARK_APP_ID and LARK_APP_SECRET environment variables are required"):
        CloudSheetsSlim(os.environ.get("TEST_LARK_SPREADSHEET_URL", ""), "Sheet1")
    
    # Restore environment variables
    if app_id:
        os.environ["LARK_APP_ID"] = app_id
    if app_secret:
        os.environ["LARK_APP_SECRET"] = app_secret


def test_basic_crud_operations(pdp, lark_sheets):
    """Test basic CRUD operations."""
    # Create
    unique_id = str(uuid.uuid4())
    test_record = {
        "_id": unique_id,
        "name": "Test Record",
        "value": 42
    }
    pdp.insert_one(test_record)
    lark_sheets.push_df(pdp.get_df())
    
    # Read
    result = pdp.find_one({"_id": unique_id})
    assert result == test_record
    
    # Update
    update_data = {"value": 43}
    pdp.update_one({"_id": unique_id}, update_data)
    lark_sheets.push_df(pdp.get_df())
    updated_result = pdp.find_one({"_id": unique_id})
    assert updated_result["value"] == 43
    
    # Delete
    pdp.delete_one({"_id": unique_id})
    lark_sheets.push_df(pdp.get_df())
    deleted_result = pdp.find_one({"_id": unique_id})
    assert deleted_result is None


def test_batch_operations(pdp, lark_sheets):
    """Test batch insert and delete operations."""
    # Batch insert
    records = [
        {"_id": str(uuid.uuid4()), "name": f"Test {i}", "value": i}
        for i in range(3)
    ]
    pdp.insert_many(records)
    lark_sheets.push_df(pdp.get_df())
    
    # Verify all records were inserted
    for record in records:
        result = pdp.find_one({"_id": record["_id"]})
        assert result == record
    
    # Batch delete
    ids = [record["_id"] for record in records]
    pdp.delete_many({"_id": {"$in": ids}})
    lark_sheets.push_df(pdp.get_df())
    
    # Verify all records were deleted
    for record_id in ids:
        result = pdp.find_one({"_id": record_id})
        assert result is None


def test_filter_operations(pdp, lark_sheets):
    """Test filter operations."""
    # Insert test records
    records = [
        {"_id": str(uuid.uuid4()), "category": "A", "value": i}
        for i in range(5)
    ]
    pdp.insert_many(records)
    lark_sheets.push_df(pdp.get_df())
    
    # Test filtering
    results = pdp.find({"category": "A", "value": {"$gt": 2}})
    assert len(results) == 2
    
    # Clean up
    pdp.delete_many({"category": "A"})
    lark_sheets.push_df(pdp.get_df())


def test_error_handling(lark_sheets):
    """Test error handling for invalid operations."""
    # Test invalid sheet name
    with pytest.raises(ValueError, match="Sheet 'NonExistentSheet' not found"):
        CloudSheetsSlim(os.environ.get("TEST_LARK_SPREADSHEET_URL"), "NonExistentSheet")
    
    # Test pushing invalid DataFrame
    with pytest.raises(Exception):
        lark_sheets.push_df(None) 