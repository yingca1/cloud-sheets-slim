# Cloud Sheets Slim

## Installation

```bash
pip install cloud-sheets-slim
```

## Usage

```bash
from cloud_sheets_slim import CloudSheetsSlim

cloud_sheet = CloudSheetsSlim("https://docs.google.com/spreadsheets/d/1LS1gMp_wFkmuFTS17D***your-doc-key***", "Sheet1")
pdp = sheets.to_pdp()

# query operations
pdp.find({'key': 'value'})
pdp.find_one({'key': 'value'})

# write operations
pdp.update_one({'key': 'value'}, update_object)
pdp.replace_one({'key': 'value'}, update_object)
pdp.delete_one({'key': 'value'})
# send updated result to cloud sheets
cloud_sheet.push_df(pdp.get_df())
```

## Features

load data from cloud sheets to pandas proxy, manipulate data in pandas proxy, every operation will be recorded in pandas proxy, and push back to cloud sheets.

avoid too many API calls to cloud sheets.

### Pandas proxy

- [x] find_one
- [x] find
- [x] insert_one
- [x] insert_many
- [x] replace_one
- [x] update_one
- [x] update_many
- [x] delete_one
- [x] delete_many
- [x] count_records

## Supported Platform

### [x] Google Sheets

- https://developers.google.com/sheets/api/quickstart/python
- https://developers.google.com/sheets/api/guides/concepts
- https://github.com/burnash/gspread
- https://docs.gspread.org/en/latest/oauth2.html

### [ ] Lark sheets

- https://github.com/larksuite/oapi-sdk-python
- https://github.com/larksuite/oapi-sdk-python-demo/blob/main/composite_api/sheets/copy_and_paste_by_range.py
- https://open.larksuite.com/document/server-docs/docs/sheets-v3/spreadsheet-sheet/operate-sheets

### [ ] MS Excel Sheets

- https://github.com/microsoftgraph/msgraph-sdk-python
