# -*- coding: utf-8 -*-

import sys
from collections import Counter
from datetime import datetime, timedelta

import gspread
import pandas as pd
from icecream import ic
from oauth2client.service_account import ServiceAccountCredentials
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def is_today_holiday():
    # Load the holiday data
    holidays = pd.read_csv('holidays.tsv', sep='\t', header=None, names=['date', 'holiday'], comment='#')
    holidays['date'] = pd.to_datetime(holidays['date'], format='%Y%m%d')

    # Check if today is a holiday or a weekend
    today = datetime.now().date()
    if today in holidays['date'].dt.date.values or today.weekday() >= 5:
        holiday_name = holidays.loc[holidays['date'].dt.date == today, 'holiday'].values[0] if today in holidays['date'].dt.date.values else "주말"
        date_str = today.strftime('%m-%d')
        return True, f'{holiday_name}({date_str})'
    else:
        return False, ''



slack_client = WebClient(token=SLACK_BOT_TOKEN)


def send_block_to_channel(channel_name, block_message, fallback_text):
    try:
        response = slack_client.conversations_list()
        channels = response['channels']
        channel_id = None

        for channel in channels:
            if channel['name'] == channel_name:
                channel_id = channel['id']
                break

        if channel_id is not None:
            slack_client.chat_postMessage(channel=channel_id, blocks=block_message, text=fallback_text)
            print(f'Message sent to {channel_name}')
        else:
            print(f'Channel {channel_name} not found.')

    except SlackApiError as e:
        print(f'Error: {e}')


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


def get_dup_names(cn, min_cnt=1):
    counter = Counter(cn)
    ic(cn)
    ncn = []
    for name, count in counter.items():
        if count >= min_cnt:
            ncn.append(str(count) + ':' + name)

    ucn = '\n'.join(ncn) if len(ncn) > 0 else '없음 \n'
    ic(ucn)

    return ucn, len(ncn)


is_holiday, s = is_today_holiday()

if is_holiday:
    print(f'{s}로 아무 메세지도 전송하지 않습니다.')
    sys.exit()
channel_name = 'chatbot-today'

# Google Sheets API를 사용하기 위한 설정
scope = [
    "https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name('./cleanbedding-c9b48eb044cf-service-account-key.json', scope)

client = gspread.authorize(creds)

# 여기에 실제 스프레드시트의 ID를 넣어야 합니다.

# 데이터를 읽어옵니다.
data = sheet.get_all_records()

# 고객명을 저장할 세 개의 집합을 초기화합니다.
customer_names1 = set()
# customer_names2 = set()
# customer_names3 = set()
customer_names = []
customer_names2 = []
customer_names3 = []

for row in data:
    if row['두었습니다'] == '발견':
        customer_names1.add(row['고객명'])
        customer_names.append(row['고객명'])
    elif row['두었습니다'] == '없음':
        # customer_names2.add(row['고객명'])
        customer_names2.append(row['고객명'])
    elif row['두었습니다'] == '모름':
        # customer_names3.add(row['고객명'])
        customer_names3.append(row['고객명'])

detected = '\n'.join(customer_names1).replace('\n\n', '\n') if len(customer_names1) > 0 else '없음 \n'
# notfounds = '\n'.join(customer_names2).replace('\n\n', '\n') if len(customer_names2) > 0 else '없음 \n'
# dontknows = '\n'.join(customer_names3).replace('\n\n', '\n') if len(customer_names3) > 0 else '없음 \n'

ntimenames, ntime_cutomers = get_dup_names(customer_names, 2)
notfounds, ntime_cutomers2 = get_dup_names(customer_names2)
dontknows, ntime_cutomers3 = get_dup_names(customer_names3)

# counter = Counter(customer_names)
# ntime_cutomers = []
# for name, count in counter.items():
#     if count > 1:
#         ntime_cutomers.append(name + ':' + str(count))
# ntimenames = '\n'.join(ntime_cutomers) if len(ntime_cutomers) > 0 else '없음 \n'

# 각 카테고리별 고객 수를 출력합니다.
print('발견 고객 수:', len(customer_names1))
print(detected)
print('-------------------------------')
print()
print('없음 (기타 질문 확인 필요) 고객 수 :', len(customer_names2))
print(notfounds)
print('-------------------------------')
print()
print('모름 (두었습니다. 가 있을 수 있는) 고객 수:', len(customer_names3))
print(dontknows)
print('-------------------------------')
print()
print()
print('두었습니다 여러번 응답한 고객 수:', ntime_cutomers)
print(ntimenames)

report_text = f'''*발견 고객 수* : {len(customer_names1)}\n
{detected}
*없음 고객 수* : {ntime_cutomers2}
{notfounds}
*모름 고객 수* : {ntime_cutomers3}
{dontknows}

*두었습니다 여러번 응답* : {ntime_cutomers}
{ntimenames}
'''

now = datetime.now()
answr_time = now.strftime('%Y-%m-%d %H:%M')

# send_message_to_channel(channel_name, f'> *응답현황 : {now}*')
# send_message_to_channel(channel_name, report_text)

report_block = [{"type": "header", "text": {"type": "plain_text", "text": f' {answr_time} 응답현황점검 '}}, {"type": "section", "text": {"type": "mrkdwn", "text": f' > *두었습니다 점검*'}},
                {
                    "type": "section",
                    "fields": [{"type": "mrkdwn", "text": f"*발견 고객 수* : {len(customer_names1)}\n```{detected}```"},
                               {"type": "mrkdwn", "text": f"*두었습니다 여러번 응답* : {ntime_cutomers}\n```{ntimenames}```"}]
                }, {"type": "divider"}, {"type": "section", "text": {"type": "mrkdwn", "text": f'> *기타 확인*'}},
                {
                    "type": "section",
                    "fields": [{"type": "mrkdwn", "text": f"*없음 고객 수* : {ntime_cutomers2}\n```{notfounds}```"},
                               {"type": "mrkdwn", "text": f"*모름 고객 수* : {ntime_cutomers3}\n```{dontknows}```"}]
                }, {"type": "divider"}]

send_block_to_channel(channel_name, report_block, report_text)
