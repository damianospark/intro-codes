import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials

MAX_RETRIES = 3
RETRY_DELAY = 3  # delay in seconds


def execute_with_retry(func, *args, **kwargs):
    for i in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            if e.response.status_code == 503:
                print(f"APIError occurred with status 503. Retrying {i+1} of {MAX_RETRIES}.")
                print(f"Error details: {e}")
                time.sleep(RETRY_DELAY)
            else:
                raise
    raise RuntimeError("Failed to execute function after multiple retries.")


# use creds to create a client to interact with the Google Drive API
# scope = ['https://www.googleapis.com/auth/drive']
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('./cleanbedding-c9b48eb044cf-service-account-key.json', scope)
client = gspread.authorize(creds)

# Open the Google spreadsheet by its url
sheet = client.open_by_url(spreadsheet_url).sheet1

# Insert data into the second row, right after the column header row
data = ['고객명2', '응답일시', '문의내용', '특이질문', '답변일시', '답변시각']
sheet.insert_row(data, index=2)
data = ['고객명1', '응답일시1', '문의내용1', '특이질문1', '답변일시1', '답변시각']
# sheet.insert_row(data, index=2)
execute_with_retry(sheet.insert_row, data, index=2)
