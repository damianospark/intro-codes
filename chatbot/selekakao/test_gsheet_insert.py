import datetime
import traceback

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name('./cleanbedding-c9b48eb044cf-service-account-key.json', scope)

client = gspread.authorize(creds)
# Open the Google Spreadsheet (replace 'Your spreadsheet' with your actual spreadsheet name)
# spreadsheet = client.open("insert-test")

# Rename the first sheet
current_date = datetime.datetime.now().strftime('%m-%d')
worksheet = spreadsheet.get_worksheet(0)  # get the first sheet
worksheet.update_title(current_date)
sheet = spreadsheet.sheet1

# Insert data into the second row, right after the column header row
data = ['', '고객명', '카카오날짜', '두었습니다', '문의내용', '메세지수', '발견된질문', '응답일시', '답변일시', '답변내용']
sheet.update('A{}:J{}'.format(0 + 1, 0 + 1), [data])  # The '+1' is because Google Sheets are 1-indexed

print(worksheet.title)
# Add a new sheet and make it the first sheet
spreadsheet.add_worksheet(title='Sheet1', rows="100", cols="20", index=0)
