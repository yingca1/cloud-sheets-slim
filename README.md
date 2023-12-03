# Cloud Sheets Slim

## Installation

```bash
pip install cloud-sheets-slim
```

## Usage

```bash
from cloud_sheets_slim import CloudSheetsSlim

cloud_sheet = CloudSheetsSlim("https://docs.google.com/spreadsheets/d/1LS1gMp_wFkmuFTS17D***your-doc-key***", "Sheet1")
cloud_sheet.find()
```

## Features

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
