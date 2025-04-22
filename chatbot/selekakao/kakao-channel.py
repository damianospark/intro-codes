# -*- coding: utf-8 -*-
import json
import os
import sys
import time
import traceback
from datetime import datetime, timedelta
from typing import Optional

import gspread
import pandas as pd
import pyperclip
import requests
from dotenv import load_dotenv
from gspread.exceptions import APIError
from icecream import ic
from loguru import logger
from lxml import html
from oauth2client.service_account import ServiceAccountCredentials
from pydantic import BaseModel
from selenium import webdriver
from selenium.common.exceptions import \
    TimeoutException  # Import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# last_visit=datetime.now()

load_dotenv()
# logging.basicConfig(level=logger.info, format='%(asctime)s - %(levelname)s - %(message)s')
slack_client = WebClient(token=SLACK_BOT_TOKEN)

# Access variables
KAKAO_ID = os.getenv('KAKAO_ID')
KAKAO_PW = os.getenv('KAKAO_PW')

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('./cleanbedding-c9b48eb044cf-service-account-key.json', scope)


def get_gspread_sheet():
    MAX_RETRIES = 5
    RETRY_DELAY = 5  # delay in seconds
    for i in range(MAX_RETRIES):
        try:
            client = gspread.authorize(creds)
            spreadsht = client.open_by_url(spreadsht_url)
            sht = spreadsht.sheet1
            return sht
        except APIError as e:
            if e.response.status_code == 503:
                logger.debug(f"APIError occurred with status 503. Retrying {i+1} of {MAX_RETRIES}.")
                logger.debug(f"Error details: {e}")
                time.sleep(RETRY_DELAY)
            else:
                logger.debug(f"gspread APIError로 5초 sleep...")
                traceback.print_exc()
                time.sleep(RETRY_DELAY)
    raise RuntimeError("Failed to execute 'get_gspread_sheet' function after multiple retries.")


os.environ['TZ'] = 'Asia/Seoul'
# Define the log file path and rotation settings
log_filename = './logs/run_{time:%Y%m%d}.log'  # Updated log file path
# log_filename = '/app/logs/run_{time:%Y%m%d}.log'  # Updated log file path
sink_id = logger.add(log_filename, format="{time} - {level} - {message}", rotation="11:01", level="DEBUG")

# Example usage
logger.debug("This is a log message")


# Open the Google spreadsheet by its url
# client = gspread.authorize(creds)
# spreadsheet = client.open_by_url(spreadsheet_url)
# sheet = spreadsheet.sheet1
sheet = get_gspread_sheet()
# Insert data into the second row, right after the column header row
data = ['', '고객명', '카카오날짜', '두었습니다', '문의내용', '메세지수', '발견된질문', '응답일시', '답변일시', '답변내용']
sheet.update('A{}:J{}'.format(0 + 1, 0 + 1), [data])  # The '+1' is because Google Sheets are 1-indexed


def is_holiday(date: datetime.date):
    holidays = pd.read_csv('holidays.tsv', sep='\t', header=None, names=['date', 'holiday'], comment='#')
    holidays['date'] = pd.to_datetime(holidays['date'], format='%Y%m%d')
    # Check if the provided date is a holiday or a weekend
    if date in holidays['date'].dt.date.values or date.weekday() >= 5:
        holiday_name = holidays.loc[holidays['date'].dt.date == date, 'holiday'].values[0] if date in holidays['date'].dt.date.values else "주말"
        date_str = date.strftime('%m-%d')
        return True, f'{holiday_name}({date_str})'
    else:
        return False, ''


def is_today_holiday():
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


def is_tomorrow_holiday():
    holidays = pd.read_csv('holidays.tsv', sep='\t', header=None, names=['date', 'holiday'], comment='#')
    holidays['date'] = pd.to_datetime(holidays['date'], format='%Y%m%d')
    # Check if tomorrow is a holiday or a weekend
    tomorrow = datetime.now().date() + timedelta(days=1)
    if tomorrow in holidays['date'].dt.date.values or tomorrow.weekday() >= 5:
        holiday_name = holidays.loc[holidays['date'].dt.date == tomorrow,
     'holiday'].values[0] if tomorrow in holidays['date'].dt.date.values else "주말"
        date_str = tomorrow.strftime('%m-%d')
        return True, f'{holiday_name}({date_str})'
    else:
        return False, ''


# def backup_sheet1():
#     # Rename the first sheet
#     current_date = datetime.now().strftime('%m-%d')
#     worksheet = spreadsheet.get_worksheet(0)  # get the first sheet
#     worksheet.update_title(current_date)
#     logger.info(worksheet.title)
#     # Add a new sheet and make it the first sheet
#     spreadsheet.add_worksheet(title='Sheet1', rows="100", cols="20", index=0)


class Ask(BaseModel):
    name: str
    ask_time: str
    ask_text: str
    answer_text: Optional[str] = ''
    answr_time: Optional[str] = ''


answr_put = "요청이 접수되었습니다.\n\n■ 교체 안내 메시지는 총 세 차례 발송되며, 버튼은 한 번만 눌러주셔도 접수가 완료됩니다.\n■ 배송 완료 메시지 수신 전까지 침구를 그대로 두어주 시기 바랍니다.\n■ 배송일 오전 11시 이후에 배송을 접수해 주시면 답변이 발송되어도 배송이 취소될 수 있습니다."


def kakao_send_keys(text, elm, driver):
    # Split the text by newline character
    lines = text.split('\n')
    for i, line in enumerate(lines):
        # Send this line of text
        elm.send_keys(line)
        elm.send_keys(Keys.LEFT_SHIFT + Keys.ENTER)


def kakao_paste_send_keys(text, elm, driver):
    pyperclip.copy(text)
    elm.send_keys(Keys.CONTROL, 'v')
    elm.send_keys(Keys.LEFT_SHIFT + Keys.ENTER)


def get_new_chatext(html_content):
    # Parse the HTML
    root = html.fromstring(html_content)
    # Flag to start recording chats
    start_recording = False
    # List to hold chat texts
    chat_texts = []
    # Find all p elements
    p_elements = root.xpath('//p[@class="txt_check"] | //*[@class="item_chat item_start" or @class="item_chat"]//p')
    # Iterate through each p element
    for p in p_elements:
        # If the p has the class 'txt_check', set the flag to start recording
        if 'txt_check' in p.attrib.get('class', ''):
            start_recording = True
        # If the flag is set and the p has the class 'txt_chat', record the chat
        if start_recording and 'txt_chat' in p.attrib.get('class', ''):
            chat_texts.append(p.text_content())
    ret_texts = ""
    # Print the chat texts
    for chat_text in chat_texts:
        ret_texts += chat_text + '\n'

    return ret_texts


def get_new_msglist(html_content):
    root = html.fromstring(html_content)
    targets = []
    li_elements = root.xpath("//*[@id='mArticle']/div[2]/div[3]/div/div/li")
    for i, li in enumerate(li_elements, 1):
        txt_name = li.xpath(".//span[@class='txt_name']/text()")
        last_msg = li.xpath(".//p[@class='txt_info']/text()")
        num_round = li.xpath(".//span[@class='num_round']/text()")
        txt_date = li.xpath(".//span[@class='txt_date']/span/text()")
        a_link = li.xpath(".//a[@class='link_chat']")
        # ic(num_round)
        # ic(last_msg)
        if num_round:
            targets.append({
                'txt_name': f"{txt_name[0] if txt_name else ''}",
                'num_round': f"{num_round[0] if num_round else '0'}",
                'last_msg': f"{last_msg[0] if last_msg else ''}",
                'txt_date': f"{txt_date[0] if txt_date else ''}",
                'a_link': a_link[0] if a_link else None,
                'a_path': f"//*[@id='mArticle']/div[2]/div[3]/div/div/li[{i}]/a"
            })
    return targets


def sleepcount(n, l):
    print(f'{l} 대기', end=':')
    for i in range(n, -1, -1):
        if n > 1000:
            if i % 100 == 0:
                print(i, end=' ')
        else:
            print(i, end=' ')
        sys.stdout.flush()
        time.sleep(1)
    # if time_difference.total_seconds() > 1:
    print()  # To move to next line after the loop ends.
    # last_visit = datetime.now()


def get_gpt_answer(txt, cust_name, ask_time):
    url = 'http://localhost:8888/ask/'
    now = datetime.now()
    ask = Ask(name=cust_name, ask_time=ask_time, ask_text=txt)
    # logger.info('json',ask.json())
    headers = {'Content-type': 'application/json', 'Accept': 'json/plain'}
    response = requests.post(url, data=ask.json(), headers=headers)
    logger.debug(response.status_code)
    logger.debug(response.text)
    ret_obj = Ask.parse_raw(response.text)
    return ret_obj.answer_text


def in_yesterday(kakao_date_str, ask_ts_in_sheet):
    ymd = kakao_date_str.split()
    y = int(ymd[0].replace('년', '') if len(ymd) == 3 else 0)
    mi = 1 if len(ymd) == 3 else 0  # 년월일이 아닐 때는 0 년월일 때는 1
    m = int(ymd[mi].replace('월', ''))
    d = int(ymd[mi + 1].replace('일', ''))
    # ymd = kakao_date_str.strptime('%Y-%m-%d %H:%M')
    # y=ymd.year
    # m=ymd.m
    # d=ymd.d
    now = datetime.now()
    given_date = datetime(year=now.year if not y else y, month=m, day=d).date()
    ask_date = datetime.strptime(ask_ts_in_sheet, '%Y-%m-%d %H:%M').date()
    yesterday = now.date() - timedelta(days=1)
    # ic(given_date,ask_date,yesterday)
    # ic(given_date == yesterday,ask_date == yesterday )
    return given_date == yesterday and ask_date == yesterday


def kakao_dt_norm(txt_date, answr_time):
    answr_ts = datetime.strptime(answr_time, '%Y-%m-%d %H:%M:%S')

    if '오전' in txt_date or '오후' in txt_date:
        kakao_ts = txt_date.replace('오전', 'AM').replace('오후', 'PM')
        kakao_parsed_ts = datetime.strptime(kakao_ts, '%p %I:%M')
        answr_ts = datetime.strptime(answr_time, '%Y-%m-%d %H:%M:%S')
        return datetime(answr_ts.year, answr_ts.month, answr_ts.day, kakao_parsed_ts.hour, kakao_parsed_ts.minute).strftime('%Y-%m-%d %H:%M')
    else:
        ymd = txt_date.split()
        y = int(ymd[0].replace('년', '') if len(ymd) == 3 else 0)
        mi = 1 if len(ymd) == 3 else 0  # 년월일이 아닐 때는 0 년월일 때는 1
        m = int(ymd[mi].replace('월', ''))
        d = int(ymd[mi + 1].replace('일', ''))
        return datetime(answr_ts.year if y == 0 else y, m, d, 1, 1).strftime('%Y-%m-%d %H:%M')


def is_same_ts(kakao_ts_in_sheet, ask_ts_in_sheet, kakao_ts_from_ui):
    # ic(kakao_ts_in_sheet, kakao_ts_from_ui)
    # logger.info('is_same_ts-->', kakao_ts_in_sheet == kakao_ts_from_ui , ('월' in kakao_ts_from_ui and in_yesterday(kakao_ts_from_ui,ask_ts_in_sheet)))
    return kakao_ts_in_sheet == kakao_ts_from_ui or ('월' in kakao_ts_from_ui and in_yesterday(kakao_ts_from_ui, ask_ts_in_sheet))


def already_recorded(rows, row_to_insert_or_update):
    for i, r in enumerate(rows):
        if i == 0:  # Skip the header row
            continue
        # logger.info('c_row', row_to_insert_or_update[1:5],  r[1+0] == row_to_insert_or_update[1+0],is_same_ts(r[1+1],r[1+6], row_to_insert_or_update[1+1]),  r[1+3] == row_to_insert_or_update[1+3] )
        # logger.info('s_row',r[1:5])
        if r[1 + 0] == row_to_insert_or_update[1 + 0] and is_same_ts(r[1 + 1], r[1 + 6],
                                                                     row_to_insert_or_update[1 + 1]) and r[1 + 3] == row_to_insert_or_update[1 + 3]:
            # logger.info('exist in the sheet', row_to_insert_or_update)
            return True
    return False


def gspread_upsert(sheet, row_to_insert_or_update):
    MAX_RETRIES = 5
    RETRY_DELAY = 5  # delay in seconds

    def execute_with_retry(func, *args, **kwargs):
        for i in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except APIError as e:
                if e.response.status_code == 503:
                    logger.debug(f"APIError occurred with status 503. Retrying {i+1} of {MAX_RETRIES}.")
                    logger.debug(f"Error details: {e}")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.debug(f"gspread APIError로 50초 sleep...")
                    traceback.print_exc()
                    time.sleep(RETRY_DELAY)
        raise RuntimeError("Failed to execute function after multiple retries.")

    rows = execute_with_retry(sheet.get_all_values)
    if already_recorded(rows, row_to_insert_or_update):
        return

    # When answer sent with status '발견' or '없음'
    if row_to_insert_or_update[1 + 2] in ['발견', '없음']:
        logger.debug("1개 메세지라 확실한 데이터 INSERT")
        tsv_data = ",".join(['"{}"'.format(element) for element in row_to_insert_or_update]).replace(',\n', ',')
        logger.info(f'"INSERT_BAK",{tsv_data}')
        execute_with_retry(sheet.insert_row, row_to_insert_or_update, index=2)
        return

    status = ['발견', '없음', '모름']
    ndx = -1

    row = []
    i = -1
    for i, r in enumerate(rows):
        ic(record_time)
        if i == 0:  # Skip the header row
            continue
        if r[1 + 0] == row_to_insert_or_update[1 + 0]:
            row = r
            break

    if not row:
        if '두었습니다' in row_to_insert_or_update[1 + 3]:
            ndx = 0
        else:
            ndx = 2
        row_to_insert_or_update[1 + 2] = status[ndx]
        tsv_data = ",".join(['"{}"'.format(element) for element in row_to_insert_or_update]).replace(',\n', ',')
        logger.info(f'"INSERT_BAK",{tsv_data}')
        execute_with_retry(sheet.insert_row, row_to_insert_or_update, index=2)
        logger.debug("sheet에 기록된적 없는 고객 insert")
        return
    elif row[1 + 0] == row_to_insert_or_update[1 + 0]:
        if '두었습니다' in row_to_insert_or_update[1 + 3]:
            ndx = 0
        elif row[1 + 2] == '발견' and int(row_to_insert_or_update[1 + 4]) - int(row[1 + 4]) == 1:
            ndx = 0  # 발견
        elif row[1 + 2] == '없음' and int(row_to_insert_or_update[1 + 4]) - int(row[1 + 4]) == 1:
            ndx = 1  # 없음
        else:  # 2개 이상의 메세지에 마지막 메세지가 두었습니다가 있을 수도 없을 수도 있을 때
            ndx = 2
        row_to_insert_or_update[1 + 2] = status[ndx]
        row_to_insert_or_update[1 + 5] = row[1 + 5] + '\n' + row_to_insert_or_update[1 + 5]
        tsv_data = ",".join(['"{}"'.format(element) for element in row_to_insert_or_update]).replace(',\n', ',')
        logger.info(f'"UPDATE_BAK",{tsv_data}')
        execute_with_retry(sheet.update, 'A{}:J{}'.format(i + 1, i + 1), [row_to_insert_or_update])  # The '+1' is because Google Sheets are 1-indexed
        return

    row_to_insert_or_update[1 + 2] = status[2]
    logger.debug('------------- 찐모름 ---------------------')
    logger.debug('kakao UI  :' + str(row_to_insert_or_update))
    logger.debug('sheet row :' + str(row))
    tsv_data = ",".join(['"{}"'.format(element) for element in row_to_insert_or_update]).replace(',\n', ',')
    logger.info(f'"INSERT_BAK",{tsv_data}')
    execute_with_retry(sheet.insert_row, row_to_insert_or_update, index=2)


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
            logger.debug(f'Message sent to {channel_name}')
        else:
            logger.debug(f'Channel {channel_name} not found.')
    except SlackApiError as e:
        logger.debug(f'Error: {e}')


def wait_return_true(driver, pth, for_what, how_long):
    elm = None
    try:
        # Wait up to 10 seconds until the element is present
        # element_present = EC.presence_of_element_located((By.XPATH, pth))
        element_present = EC.presence_of_element_located((By.XPATH, pth))
        elm = WebDriverWait(driver, how_long).until(element_present)
    except TimeoutException:
        logger.debug(f"Timed out waiting for {for_what} being clickable")
    finally:
        logger.debug(for_what + ': complete' + ', elm:' + str(elm))
    if elm is not None:
        return True
    return False


# Create a new ChromeOptions object
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--headless')
# chrome_options.add_argument("--single-process")
# chrome_options.add_argument("--disable-dev-shm-usage")
# Set the user-data-dir option to the path of your Chrome profile

# chrome_options.add_argument("user-data-dir=/home/damianos/.config/google-chrome")
# chrome_options.add_argument("profile-directory=Profile 9")

# Create a new WebDriver object using the ChromeOptions object
# driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
driver = webdriver.Chrome(options=chrome_options)
# driver.set_window_size(1198, 1128)
driver.maximize_window()
#
# 카카오 인증
#
# driver.get('https://center-pf.kakao.com/_jvQUxj/chats') #CleanB Life
driver.get('https://center-pf.kakao.com/_rXWfj/chats')
sleepcount(1, 'Wait Login Screen')
driver.find_element(By.XPATH, '//*[@id="loginId--1"]').click()
driver.find_element(By.XPATH, '//*[@id="loginId--1"]').send_keys(KAKAO_ID)
driver.find_element(By.XPATH, '//*[@id="password--2"]').click()
driver.find_element(By.XPATH, '//*[@id="password--2"]').send_keys(KAKAO_PW)
driver.find_element(By.XPATH, '//*[@id="mainContent"]/div/div/form/div[4]/button[1]').click()
timedout = False
try:
    # Wait up to 10 seconds until the element is present
    element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="mArticle"]/div[1]/h3'))
    send_message_to_channel('chatbot-today', '30초간 인증대기중입니다. 빨리 인증해주세요 : ' + KAKAO_ID)
    WebDriverWait(driver, 30).until(element_present)
except TimeoutException:
    timedout = True
    logger.debug("Timed out waiting for page to load")
finally:
    if timedout:
        send_message_to_channel('chatbot-today', '\n30초 인증만료로 챗봇 실행 중지합니다.\n카카오채널 관리지 인증 준비된 상태에서 챗봇을 다시 실행해주세요.\n' + KAKAO_ID)
        driver.quit()

element = driver.find_element(By.TAG_NAME, "body")
element.send_keys(Keys.ESCAPE)
chatlist_ui_present = wait_return_true(driver, '//*[@id="mArticle"]/div[2]/div[3]/div/div/li', '1:1채팅리스트화면', 5)

#
# 관리자 추가인증
#
adminauth_ui_present = wait_return_true(driver, '//*[@id="mArticle"]/div[2]/div/button[1]', '관리자 추가인증', 3)
if not chatlist_ui_present and adminauth_ui_present:
    driver.find_element(By.XPATH, '//*[@id="mArticle"]/div[2]/div/button[1]').click()  # 관리자 추가인증 버튼 클릭
    try:
        element_present = EC.presence_of_element_located((By.XPATH, '//*[@id="mArticle"]/div[2]/div[2]/button[1]'))
        WebDriverWait(driver, 30).until(element_present)
    except TimeoutException:
        logger.debug("Timed out waiting for page to load")
    finally:
        logger.debug("관리자 추가 인증 완료")

results = []
sleepcount(3, '채팅리스트 render')
old_elements = []
send_message_to_channel('chatbot-today', '인증완료후 모니터링 착수 : ' + KAKAO_ID)
refresed = False
break_time = False
today_backuped = False
while True:
    now = datetime.now()
    remain_hour = 20 - now.hour - 1
    remain_minute = 60 - now.minute
    break_dura = remain_hour * 60 * 60 + remain_minute * 60 - 10 * 60
    current_time = datetime.now().time()
    # ic(current_time.hour, current_time.minute)
    today_nowork, hol_name = is_today_holiday()
    if not break_time and break_dura > 0 and (current_time.hour >= 11 and current_time.minute >=
                                              0 and current_time.second >= 20) and current_time.hour < 20:
        break_time = True
    elif not break_time and today_nowork and current_time.hour < 11:
        send_message_to_channel('chatbot-today', f'{hol_name} 휴무일에 챗봇 시작되어 모니터링 보류 필요')
        break_time = True
    else:
        break_time = False

    if break_time:
        logger.debug(f"클린 챗봇 모니터링 종료")
        send_message_to_channel('chatbot-today', f'클린 챗봇 모니터링 종료\n{break_dura/60/60:.1f}시간 동안 모니터링 보류\n오후 7시 50분쯤 재 시작예정.')
        sleepcount(break_dura, '챗봇의 쉬는시간')  # 7시45분까지 쉰다.
        today_backuped = False
        refresed = False
        logger.debug('쉬는 시간 끝 동작 재개: ' + str(now))
        # 백업 때문에 시트의 인덱스가 바뀌었을 것이므로 안전하게 다시 오픈.
        sheet = get_gspread_sheet()
        driver.refresh()
        element = driver.find_element(By.TAG_NAME, "body")
        element.send_keys(Keys.ESCAPE)
        send_message_to_channel('chatbot-today', f'클린 챗봇 모니터링 재 시작')
    # 저녁에 내일배송을 위한 두었습니다. 확인하기 전에 내일이 휴일인지 확인
    nowork_tomorrow, dayname = is_tomorrow_holiday()
    if current_time.minute >= 1 and current_time.hour > 11 and nowork_tomorrow:
        now = datetime.now()
        remain_hour = 20 - now.hour - 1
        remain_minute = 60 - now.minute if remain_hour > 0 else 60
        # break_dura = 24 * 60 * 60  #하루(24시간)동안 쉬고 다시 확인
        break_dura = (24 + remain_hour + 1) * 60 * 60 - now.minute * 60 - 10 * 60
        send_message_to_channel('chatbot-today', f'내일이 {dayname} 휴무이므로{break_dura/60/60:.2f}시간 동안 모니터링 보류\n')
        sleepcount(break_dura, '내일 휴무로 챗봇 모니터링 보류중')  # 7시45분까지 쉰다.
        sheet = get_gspread_sheet()
        driver.refresh()
        element = driver.find_element(By.TAG_NAME, "body")
        element.send_keys(Keys.ESCAPE)
        send_message_to_channel('chatbot-today', f'{dayname} 휴무 모니터링 보류후 재기동\n')

    # if not today_backuped and current_time.hour == 11 and current_time.minute == 1:
    #     backup_sheet1()
    #     send_message_to_channel('chatbot-today', '구글시트 로그 백업 완료')
    #     today_backuped = True

    if not refresed and current_time.hour == 0 and current_time.minute == 0:
        refresed = True
        driver.refresh()
        element = driver.find_element(By.TAG_NAME, "body")
        element.send_keys(Keys.ESCAPE)
        send_message_to_channel('chatbot-today', '0시가 넘어서 카카오 채널 UI 버그회피를 위해 화면 리프레시 진행함')

    chat_elements = driver.find_elements(By.XPATH, '//*[@id="mArticle"]/div[2]/div[3]/div/div/li')
    if not chat_elements:
        sleepcount(5, '채팅리스트 없어서')  # wait for chat window to open
        continue
    html_content = driver.page_source
    chat_elements = get_new_msglist(html_content)
    #
    # google docs의 초당 조회 수가 60회 limit이므로 이를 피하기 위해 최대한 채팅 리스트에 변화가 없으면 insert나 updae를 위한 로직으로 들어가지 않는다.
    #
    old_chk_keys = '_'.join(ce['txt_name'] + ce['txt_date'] + ce['num_round'] for ce in old_elements)
    new_chk_keys = '_'.join(ce['txt_name'] + ce['txt_date'] + ce['num_round'] for ce in chat_elements)
    old_elements = chat_elements
    if old_chk_keys == new_chk_keys:
        sleepcount(1, '이전 리스트의 값과 동일해서')
        continue
    for chat in chat_elements:
        # if '두었습니다' not in chat['last_msg']:
        # if "두었습니다" in new_texts and int(chat['num_round']) == 1:
        if int(chat['num_round']) == 0:
            continue
        elif int(chat['num_round']) == 1:
            if '두었습니다' in chat['last_msg']:
                user_row = driver.find_element(By.XPATH, chat['a_path'])
                user_row.click()
                sleepcount(1, '채팅팝업 open')  # wait for chat window to open
                original_window = driver.current_window_handle
                #
                # goto popup window
                #
                windows = driver.window_handles
                driver.switch_to.window(windows[-1])  # switch to the new window (it's the last one in the list)
                html_content = driver.page_source
                new_texts = get_new_chatext(html_content)  # 채팅창에서 캡처한 내용

                try:
                    driver.find_element(By.XPATH, '//*[@id="chatWrite"]').click()
                    kakao_paste_send_keys(answr_put, driver.find_element(By.XPATH, '//*[@id="chatWrite"]'), driver)
                except NoSuchElementException:
                    logger.error("NoSuchElementException 발생!\n" + traceback.format_exc())
                    send_message_to_channel('chatbot-today', '채팅 상담 답변 쓰기 안됨 ```traceback.format_exc()```')

                now = datetime.now()
                answr_time = now.strftime('%Y-%m-%d %H:%M:%S')

                # sleepcount(1,'전송버튼 enable')
                try:
                    element_clickable = EC.element_to_be_clickable(
    (By.XPATH, '//*[@id="kakaoWrap"]/div[1]/div[2]/div/div[2]/div/form/fieldset/button'))
                    # Wait up to 10 seconds until the element is present
                    clickable_elm = WebDriverWait(driver, 7).until(element_clickable)
                    clickable_elm.click()
                    sleepcount(0, '전송되기까지')
                except TimeoutException:
                    logger.debug("Timed out waiting for 전송버튼 enabled")
                finally:
                    driver.close()  # TODO: 사용자 확인을 위해 닫지 않는 것을 구현할 필요있으며, 이렬 경우 주석 처리
                    logger.debug("채팅창 닫기 완료")

                driver.switch_to.window(original_window)
                # if "요청이 접수되었습니다." in new_texts: # 고객이  두었습니다. 누른 것에 대해 답변하는 중 두었습니다를 또 누를 경우 창을 닫은 뒤 1개 새로운 메세지로 인식이되어 또 다시 답변을 하려고 하는데 이 때 마지막 메세지가 이전에 챗봇이 답한  내용으로 잡힐 수 있다.
                #     new_texts = '두었습니다'
                data = ['', chat['txt_name'], chat['txt_date'], '발견', new_texts, chat['num_round'],
                    new_texts, kakao_dt_norm(chat['txt_date'], answr_time), answr_time, answr_put]
                gspread_upsert(sheet, data)
                # logger.debug(f"봇 진행 내용 report")
                # logger.debug(f"===============")
                # logger.debug(f"고 객 명:{chat['txt_name']}")
                # logger.debug(f"문의일시:{chat['txt_date']}")
                # logger.debug(f"문의내용:{new_texts}")
                # logger.debug(f"답변내용:{answr_put}")
                # logger.debug(f"------------------------------")  # noqa: E501
            else:
                record_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data = [
                    '',
                    chat['txt_name'],
                    chat['txt_date'],
                    '없음',
                    chat['last_msg'],
                    chat['num_round'],
                    chat['last_msg'],
                    kakao_dt_norm(chat['txt_date'], record_time),
                    record_time,
                    ''
                ]
                gspread_upsert(sheet, data)
            continue
        else:
            record_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = [
                '', chat['txt_name'], chat['txt_date'], ' ', chat['last_msg'], chat['num_round'], chat['last_msg'], kakao_dt_norm(
                    chat['txt_date'], record_time), record_time, ''
            ]
            gspread_upsert(sheet, data)
            continue
            # answr_auto = None
            # pass
            # answer_gpt=get_gpt_answer(new_texts,chat['txt_name'],chat['txt_date'])
            # answr_auto = answer_gpt

    sleepcount(2, '신규문의 없어서')
# Close the web browser
# driver.quit()
