import argparse
import base64
import csv
import datetime
import locale
import os
import sys
import time
import traceback
import unittest
from io import StringIO
from urllib.parse import urljoin

import numpy as np
import pandas as pd
import requests
from icecream import ic
from needle.cases import NeedleTestCase
from needle.engines.perceptualdiff_engine import Engine as PerceptualDiffEngine
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from webdriver_manager.chrome import ChromeDriverManager

img_dir = '/home/max/cleanbeding/anycrawler/needle/imgs'
base_img_dir = os.path.join(img_dir, 'base')
test_img_dir = os.path.join(img_dir, 'target')
locale.setlocale(locale.LC_TIME, "ko_KR.UTF-8")
# input_date = '2024-01-11'
remote_url = "hhttps://tms.teamfresh.co.kr"

os.environ['NEEDLE_OUTPUT_DIR'] = test_img_dir
os.environ['NEEDLE_BASELINE_DIR'] = base_img_dir
channel_id = "C061P7KP2UQ"
channel_pjw_id = "D04HE04L86N"
slack_client = WebClient(token=SLACK_BOT_TOKEN)
# webhook-monitoring-alert
slack_webhook_url = (
)


def analyze_diff_ratio(diff_ratio, screen_name):
    # 현재 날짜와 시간 설정
    current_date = datetime.datetime.now().strftime("%y%m%d")
    current_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # diff_history.csv 파일 읽기 (파일이 없으면 새로 생성)
    try:
        df = pd.read_csv('diff_history.csv')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['diff_ratio', 'date', 'ts', 'screen_name'])

    # 오늘 날짜의 같은 screen_name 데이터 제거
    df = df[~((df['date'] == current_date) & (df['screen_name'] == screen_name))]

    # 새로운 데이터 추가
    df = df.append({'diff_ratio': diff_ratio, 'date': current_date, 'ts': current_ts, 'screen_name': screen_name}, ignore_index=True)

    # 파일에 저장
    df.to_csv('diff_history.csv', index=False)

    # 동일한 screen_name 데이터만 필터링
    df_screen = df[df['screen_name'] == screen_name]

    # 가장 최근 날짜의 데이터만 사용
    df_screen['date'] = pd.to_datetime(df_screen['date'])
    df_screen = df_screen[df_screen['date'] == df_screen['date'].max()]

    # 이상 탐지 로직
    if len(df_screen) > 30:  # 데이터가 충분히 많은 경우
        mean = df_screen['diff_ratio'].mean()
        std = df_screen['diff_ratio'].std()
        anomaly = abs(diff_ratio - mean) > 2 * std
        reason = f"Mean: {mean}, Standard Deviation: {std}, Anomaly detected" if anomaly else "Within normal range"
    else:  # 데이터가 충분하지 않은 경우
        anomaly = diff_ratio >= 5
        reason = "Diff ratio >= 5%" if anomaly else "Diff ratio < 5%"

    # 결과 반환
    return reason, anomaly


def upload_file_to_slack(token, file_path, channels):
    with open(file_path, 'rb') as file_content:
        response = requests.post(
            url='https://slack.com/api/files.upload',
            data={
                'token': token,
                'channels': channels
            },
            files={
                'file': file_content
            }
        )
    return response.json()


def upload_file_and_get_ts(channel_id, file_path, initial_comment=""):
    try:
        # 파일 업로드 및 초기 코멘트와 함께 메시지 게시
        upload_response = slack_client.files_upload(
            channels=channel_id,
            initial_comment=initial_comment,
            file=file_path
        )
        file_id = upload_response["file"]["id"]
        # ic(upload_response["file"])
        # 업로드된 파일과 관련된 메시지의 타임스탬프 추출
        image_url = slack_client.files_sharedPublicURL(file=file_id)["file"]["permalink_public"]
        message_ts = upload_response['file']['shares']['private'][channel_id][0]['ts']
        file_name = upload_response["file"]['name']

        return message_ts, image_url, file_name

    except SlackApiError as e:
        print(f"Error uploading file: {e.response['error']}")
        return None, None


def delete_message(channel_id, message_ts):
    try:
        result = slack_client.chat_delete(
            channel=channel_id,
            ts=message_ts  # Timestamp of the message to be deleted
        )
        return result
    except SlackApiError as e:
        print(f"Error deleting message: {e.response['error']}")


def send_slack_msg_image_at_once(title, message, file_path, ok=True):
    # attachments 형태의 포맷된 메세지를 작성합니다.
    ccode = "#2c9b3d" if ok else "#d75c15"
    ok_word = "OK" if ok else "NG"
    attachment = {"mrkdwn_in": ["text"], "color": ccode, "text": message}

    if file_path:
        message_ts, image_url, fname = upload_file_and_get_ts(channel_pjw_id, file_path, file_path.split('/')[-1])
        ic(message_ts, image_url)
        message += f"\n_{fname}_" if file_path is not None else "\n"
        attachment["image_url"] = image_url
        attachment["text"] = message

    try:
        # 메세지를 보냅니다.
        result = slack_client.chat_postMessage(
            channel=channel_id,
            text=f"*[{ok_word}] {title}*",
            attachments=[attachment],
        )
        print(attachment)
        return result
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
    finally:
        if file_path:
            delete_message(channel_pjw_id, message_ts)


def validate_and_extract_date_parts(date_str):
    try:
        # 날짜 객체를 생성합니다.
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")

        # 연도, 월, 일을 추출합니다.
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day

        # YYYYMM 형식의 문자열을 생성합니다.
        yyyymm_str = date_obj.strftime("%Y%m")

        return year, month, day, yyyymm_str
    except ValueError as e:
        # 입력된 날짜가 올바른 형식이 아닌 경우 예외를 다시 발생시킵니다.
        raise e


def navigate_to_page(driver, url, wait_xpath, sec_to_wait=5):
    try:
        driver.get(url)
        WebDriverWait(driver, sec_to_wait).until(EC.presence_of_element_located((By.XPATH, wait_xpath)))
        time.sleep(sec_to_wait)
    except Exception as e:
        traceback.print_exc()
        print(f"Error navigating to {url}: {e}")


def open_and_login(driver):
    # 페이지 로드
    driver.get(remote_url)
    time.sleep(1)

    # 로그인 페이지 확인 및 로그인 수행
    try:
        # ID와 Password 입력 필드를 찾아 값을 입력
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "userLoginId")))
        id_field = driver.find_element(By.ID, "userLoginId")
        password_field = driver.find_element(By.ID, "userLoginPw")

        id_field.send_keys("dummyid")
        password_field.send_keys("12345678")

        # 로그인 버튼 클릭
        login_button = driver.find_element(By.XPATH, '//*[@id="teamfresh"]/div/div/form/button')
        login_button.click()
    except Exception as e:
        print("로그인 페이지를 찾을 수 없습니다:", e)


def select_date(driver, target_date):
    ic(target_date, type(target_date))
    ic(driver.current_url)
    # XPath selectors

    date_input_xpath = '//*[@id="teamfresh"]/div[2]/div[2]/form/div/div/div[2]/div/label[3]/div/div[1]/div/input' if "delivery" in driver.current_url else '//*[@id="teamfresh"]/div[2]/div[2]/form/div/div/div[1]/div/label[3]/div/div[1]/div/input'
    current_month_year_xpath = '//*[@id="teamfresh"]/div[2]/div[2]/form/div/div/div[2]/div/label[3]/div/div[2]/div[2]/div/div/div[2]/div[1]/div[1]' if "delivery" in driver.current_url else '//*[@id="teamfresh"]/div[2]/div[2]/form/div/div/div[1]/div/label[3]/div/div[2]/div[2]/div/div/div[2]/div[1]/div[1]'
    prev_month_button_xpath = '//*[@id="teamfresh"]/div[2]/div[2]/form/div/div/div[2]/div/label[3]/div/div[2]/div[2]/div/div/button[1]' if "delivery" in driver.current_url else '//*[@id="teamfresh"]/div[2]/div[2]/form/div/div/div[1]/div/label[3]/div/div[2]/div[2]/div/div/button[1]'
    next_month_button_xpath = '//*[@id="teamfresh"]/div[2]/div[2]/form/div/div/div[2]/div/label[3]/div/div[2]/div[2]/div/div/button[2]' if "delivery" in driver.current_url else '//*[@id="teamfresh"]/div[2]/div[2]/form/div/div/div[1]/div/label[3]/div/div[2]/div[2]/div/div/button[2]'
    wait = WebDriverWait(driver, 5)
    # Open calendar
    driver.find_element(By.XPATH, date_input_xpath).click()
    time.sleep(0.5)  # Wait for calendar to open

    # Get the current displayed month and year from the calendar
    current_month_year_text = driver.find_element(
        By.XPATH, current_month_year_xpath
    ).text  # e.g., "1월 2024"

    # Parse the current month and year to a datetime.date object
    current_month_year = datetime.datetime.strptime(
        current_month_year_text, "%B %Y"
    ).date()

    cnt = 0
    # Navigate the calendar to the correct month and year
    while current_month_year != target_date.replace(day=1):
        print("looping", cnt)
        cnt += 1
        if current_month_year > target_date.replace(day=1):
            driver.find_element(By.XPATH, prev_month_button_xpath).click()
        else:
            driver.find_element(By.XPATH, next_month_button_xpath).click()
        time.sleep(0.3)  # Wait for calendar to update
        current_month_year_text = driver.find_element(By.XPATH, current_month_year_xpath).text
        current_month_year = datetime.datetime.strptime(current_month_year_text, "%B %Y").date()
    # Click the correct day
    # Construct the XPath for the target date
    # Assuming the days in the calendar are zero-padded to 3 digits
    day_xpath = f"//div[contains(@class, 'react-datepicker__day') and not(contains(@class, 'react-datepicker__day--outside-month')) and text()='{
                                 target_date.day}']"
    # Wait for the target day to be visible and clickable
    wait.until(EC.visibility_of_element_located((By.XPATH, day_xpath)))
    wait.until(EC.element_to_be_clickable((By.XPATH, day_xpath)))

    # Click the correct day
    driver.find_element(By.XPATH, day_xpath).click()

    # Assuming that selecting the date will close the calendar
    time.sleep(1)  # Wait for calendar to close


def show_daily_data(driver, year, month, day):
    print(f'show_daily_data ---------------{year}-{month}-{day}')
    select_date(driver, datetime.date(year, month, day))
    # Click the search button
    search_button = driver.find_element(By.XPATH, "//*[@id='searchBtn']")
    search_button.click()


tsv_string = '''target_name	url	xpath_to_check
로그인	https://tms.teamfresh.co.kr	/html/body/div
수거내역	https://tms.teamfresh.co.kr/tcc/return/report	/html/body/div
배송내역	https://tms.teamfresh.co.kr/tcc/delivery/report	/html/body/div'''


class TeamfreshVisualTest(NeedleTestCase):
    engine_class = 'needle.engines.perceptualdiff_engine.Engine'

    @classmethod
    def get_web_driver(cls):
        # profile_path = "~/.config/google-chrome/Profile 9" #집에서 작업할 때
        profile_path = "/home/max/.config/google-chrome/Default"  # 회사에서 작업할 때
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=" + profile_path)
        # UI 띄우지 않고 실행하기위한 옵션
        chrome_options.add_argument("--headless")  # Headless 모드 활성화
        cpath = ChromeDriverManager().install()
        print('drifver path', cpath)
        return webdriver.Chrome(executable_path=cpath, options=chrome_options)

    @classmethod
    def setUpClass(cls):
        super(TeamfreshVisualTest, cls).setUpClass()
        # cls.engine = cls.engine_class()
        cls.driver = cls.get_web_driver()
        cls.set_viewport_size(1700, 750)

    def setUp(self):
        self.test_date = args.date if args.date else datetime.datetime.now().strftime("%Y-%m-%d")
        self.save_baseline = args.save_baseline
        pass

    def load_test_cases(self, tsv_data):
        test_cases = []
        tsv_file = StringIO(tsv_data)
        reader = csv.DictReader(tsv_file, delimiter='\t')
        for row in reader:
            test_cases.append(row)
        return test_cases

    def test_visual(self):
        test_cases = self.load_test_cases(tsv_string)
        logged_in = False
        for case in test_cases:
            # if case['target_name'] != '배송내역':
            #     continue
            # self.driver.get(case['url'])
            print(case['target_name'])
            if case['target_name'] in ['배송내역', '수거내역']:
                if not logged_in:
                    open_and_login(self.driver)
                    time.sleep(1)
                    logged_in = True
                chk_elm_xpath = '//*[@id="teamfresh"]/div[2]/div[2]/form/div/div/div[1]/div/div/label/div[1]' if 'delivery' in case['url'] else '//*[@id="teamfresh"]/div[2]/div[2]/div[1]/div/div/button[4]'
                ic(self.driver.current_url)
                navigate_to_page(self.driver, case['url'], chk_elm_xpath, 3)
                ic(chk_elm_xpath)

                yy, mm, dd, ym = validate_and_extract_date_parts(self.test_date)
                show_daily_data(self.driver, yy, mm, dd)
            else:
                self.driver.get(case['url'])

            time.sleep(3)
            ic(self.driver.current_url)
            ic('|' + case['xpath_to_check'] + '|')
            self.assertScreenshot(case['xpath_to_check'], case['target_name'], 0)  # 모든 차이 다 검출
            # self.assertScreenshot(1, case['target_name']) # needle case.py를 열어보고 싶으면 일부러 오류낼 것.
            diff_ratio = None
            diff_pixels = None
            title, message, img_file = None, None, None
            # date_obj = datetime.datetime.strptime(self.test_date, "%Y-%m-%d")
            # date_to_check = date_obj.strftime("%Y%m%d")
            check_date = self.test_date
            diff_ratio = 0
            diff_ppm = os.path.join(test_img_dir, case['target_name'] + '-' + datetime.datetime.now().strftime('%Y%m%d') + '.diff.png')
            if os.path.exists(diff_ppm):
                filename = os.path.join(test_img_dir, case['target_name'] + '-' + datetime.datetime.now().strftime('%Y%m%d') + '.txt')
                # Write the string to the file
                with open(filename, 'r') as file:
                    # Find the line with 'pixels are different'
                    for line in file.readlines():
                        if 'Diff Ratio is' in line:
                            diff_ratio_str = line.split()[3]
                            ic(diff_ratio_str)
                            diff_ratio = float(diff_ratio_str[:-1])
                        if 'pixels are different' in line:
                            # Extract the number of different pixels
                            diff_pixels = int(line.split()[0])
                        if diff_ratio is not None and diff_pixels is not None:
                            break
                if diff_ratio > 0:
                    message = f"*변화 비율:* `{diff_ratio} %`\n*픽셀수 차이:* `{diff_pixels} px`\n"
                    img_file = diff_ppm
                else:
                    message = f"변화 없음\n"
            else:
                message = f"변화 없음\n"
            time.sleep(2)
            if not args.save_baseline:
                fpath = os.path.join(base_img_dir, case['target_name'] + '.png')
                base_date = datetime.datetime.fromtimestamp(os.path.getctime(fpath)).strftime('%Y-%m-%d')
                today = datetime.datetime.now().strftime('%Y-%m-%d')
                title = f"`{check_date}`로 `{case['target_name']}`화면변화 점검 `{base_date}`-->`{today}` "
                # 예시 사용
                reason, is_anomalous = analyze_diff_ratio(diff_ratio, case['target_name'])
                print("Anomaly Detection Reason:", reason)
                print("Is Anomalous:", is_anomalous)
                reason = f"\n_{reason}_"
                message += reason
                send_slack_msg_image_at_once(title, message, img_file, not is_anomalous)
            else:
                print('Baseline imaged saved')

            # send_slack_message_with_image(slack_webhook_url, title, message, image_url, diff_ratio < 10)

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--save-baseline', action='store_true', help='Save baseline images instead of comparing')
    parser.add_argument('date', nargs='?', help='Date in YYYY-MM-DD format', default=None)
    args, remaining_argv = parser.parse_known_args()

    # Remove custom arguments from sys.argv
    sys.argv[1:] = remaining_argv

    if not os.path.exists(base_img_dir):
        os.makedirs(base_img_dir)
    if not os.path.exists(test_img_dir):
        os.makedirs(test_img_dir)

    unittest.main()
