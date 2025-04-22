# -*- coding: utf-8 -*-

import json
import time
from datetime import datetime, timedelta

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

creds = ServiceAccountCredentials.from_json_keyfile_name('./cleanbedding-c9b48eb044cf-service-account-key.json', scope)
client = gspread.authorize(creds)

# Open the Google spreadsheet by its url
spreadsheet = client.open_by_url(spreadsheet_url)
sheet = spreadsheet.sheet1

slack_client = WebClient(token=SLACK_BOT_TOKEN)

# Load the appropriate .env file


def send_message_to_channel(channel_name, message):
    try:
        response = slack_client.conversations_list()
        channels = response['channels']
        channel_id = None

        for channel in channels:
            if channel['name'] == channel_name:
                channel_id = channel['id']
                break

        if channel_id is not None:
            slack_client.chat_postMessage(channel=channel_id, text=message)
            print(f'Message sent to {channel_name}')
        else:
            print(f'Channel {channel_name} not found.')

    except SlackApiError as e:
        print(f'Error: {e}')


def backup_sheet1():
    # Rename the first sheet
    current_date = datetime.now().strftime('%m-%d')
    worksheet = spreadsheet.get_worksheet(0)  # get the first sheet
    worksheet.update_title(current_date)
    print(worksheet.title)
    # Add a new sheet and make it the first sheet
    spreadsheet.add_worksheet(title='Sheet1', rows="100", cols="20", index=0)


current_time = datetime.now().time()
if current_time.hour >= 11 and current_time.minute >= 1:
    backup_sheet1()
    send_message_to_channel('chatbot-today', '구글시트 로그 백업 완료')
    today_backuped = True
