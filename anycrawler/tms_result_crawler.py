#!/home/max/miniconda3/bin/python
# -*- coding: utf-8 -*-

import base64
import csv
import datetime
import locale
import os
import sys
import time
import traceback
from urllib.parse import urljoin

import pandas as pd
import requests
from icecream import ic
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# webhook-monitoring-alert
slack_webhook_url = (

)

DEBUG = False


def send_slack_message(webhook_url, title, message, ok=True):
    if DEBUG:
        return
    ccode = "#2c9b3d" if ok else "#d75c15"
    ok_word = "OK" if ok else "NG"
    slack_data = {
        "attachments": [
            {
                "color": ccode,  # 색상 코드
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*[{ok_word}] {title}*",
                        },  # 타이틀
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"{message}"},
                    },
                ],
            }
        ]
    }
    # slack_data = {
    #     "text": message,
    #     "attachments": [{"text": f"<{link}|바로가기>"}]
    # }
    requests.post(webhook_url, json=slack_data)


def close_new_window_and_return(driver, original_window, original_windows):
    # 현재 창의 핸들을 저장
    ic(original_window, original_windows)
    time.sleep(1)
    # 페이지 상호작용 (예: 버튼 클릭 등) 후에 새 창이 열렸는지 확인
    # 예: driver.find_element_by_id("your-button-id").click()

    # 새로운 창이 열렸는지 검사
    new_windows = [window for window in driver.window_handles if window not in original_windows]
    ic(new_windows)
    # 새 창이 있으면 닫고 원래 창으로 돌아감

    # 새 창들이 있으면 각각 닫고 원래 창으로 돌아감
    for new_window in new_windows:
        # 새 창의 유효성 검사
        if new_window in driver.window_handles:
            # 새 창으로 전환
            driver.switch_to.window(new_window)
            # 새 창 닫기
            driver.close()

    # 원래 창으로 돌아가기 전 유효성 검사
    if original_window in driver.window_handles:
        driver.switch_to.window(original_window)
    else:
        print("Original window is no longer available.")

# def close_new_window_and_return(driver, original_window, original_windows):

#     # 페이지 상호작용 (예: 버튼 클릭 등) 후에 새 창이 열렸는지 확인
#     # 예: driver.find_element_by_id("your-button-id").click()

#     # 새로운 창이 열렸는지 검사
#     new_windows = [window for window in driver.window_handles if window not in original_windows]

#     # 새 창이 있으면 닫고 원래 창으로 돌아감
#     if new_windows:
#         # 새 창으로 전환
#         driver.switch_to.window(new_windows[0])
#         # 새 창 닫기
#         driver.close()
#         # 원래 창으로 돌아가기
#         driver.switch_to.window(original_window)


def remove_claim_button(driver):
    remove_script = """
    var element = document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    if (element) {
        element.parentNode.removeChild(element);
    }
    """

    # XPath of the element to be removed
    xpath_to_remove = '//*[@id="teamfresh"]/div/div/div[1]'

    # Execute the script
    driver.execute_script(remove_script, xpath_to_remove)


# get_all_sms 함수화
#
def get_all_sms(driver):
    extract_sms = True
    try:
        # Click on the first element
        first_element_xpath = '//*[@id="teamfresh"]/div/div/div[2]/div[2]/div/table[1]/tbody/tr/td[2]/div' if 'shipping' in driver.current_url else '//*[@id="teamfresh"]/div/div/div/div[2]/div/table[1]/tbody/tr/td[2]/div'
        first_element = driver.find_element(By.XPATH, first_element_xpath)
        first_element.click()
        time.sleep(0.5)
    except NoSuchElementException:
        # traceback.print_exc()
        print("Element not found. SMS 없어 추출 안함")
        extract_sms = False

    if extract_sms:
        # Wait for the new element to appear and get its text
        new_element_xpath = "/html/body/div[2]/div/div[1]/div/div/div[2]/p"
        new_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, new_element_xpath)))
        tmp_text = driver.execute_script("return arguments[0].innerHTML;", new_element)
        new_text = tmp_text.replace('\n', '<br>')
        # ic(new_text)

        # close the popup
        close_xpath = "/html/body/div[2]/div/div[1]/div/div/div[1]/button"
        close_bttn = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, close_xpath)))
        close_bttn.click()
        time.sleep(0.5)
        # Set the new text to the target element
        target_element_xpath = '//*[@id="teamfresh"]/div/div/div[2]/div[2]/div/table[1]/tbody/tr/td[2]' if 'shipping' in driver.current_url else '//*[@id="teamfresh"]/div/div/div/div[2]/div/table[1]/tbody/tr/td[2]'
        target_element = driver.find_element(By.XPATH, target_element_xpath)
        driver.execute_script("arguments[0].innerHTML = arguments[1];", target_element, new_text)


#
# get_image 함수화
#
def get_image(driver, save_root_path):
    current_url = driver.current_url
    try:
        # Check and click the specified element
        icon_xpath = '//*[@id="teamfresh"]/div/div/div[2]/div[2]/div/table[1]/tbody/tr/td[3]/i' if "shipping" in current_url else '//*[@id="teamfresh"]/div/div/div/div[2]/div/table[1]/tbody/tr/td[3]/i'
        icon_element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, icon_xpath)))
        icon_element.click()
        # Wait for the new image element and get its 'src' attribute
        img_xpath = '//*[@id="imgTag"]'
        img_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, img_xpath)))
        blob_img_url = img_element.get_attribute("src")

        # Download the image and save it locally
        img_folder = "img"
        os.makedirs(os.path.join(save_root_path, img_folder), exist_ok=True)
        img_name = blob_img_url.split("/")[-1] + ".jpg"
        img_path = os.path.join(save_root_path, img_folder, img_name)
        if not os.path.exists(img_path):
            image_bytes = get_file_content_chrome(driver, blob_img_url)
            with open(img_path, "wb") as img_file:
                img_file.write(image_bytes)

        time.sleep(1)
        # Click the button to return to the previous screen
        back_button_xpath = "/html/body/div[2]/div/div[1]/div/div/div[1]/button" if "shipping" in current_url else "/html/body/div[2]/div/div[1]/div/div/div[1]/h5/div/button"
        back_button = driver.find_element(By.XPATH, back_button_xpath)
        back_button.click()
        time.sleep(0.5)

        # Replace the original icon element with the downloaded image
        img_src_path = os.path.join('../', img_folder, img_name)
        driver.execute_script(
            """
            var iconElement = arguments[0];
            var newImg = document.createElement('img');
            newImg.src = arguments[1];
            iconElement.parentNode.replaceChild(newImg, iconElement);
            """,
            icon_element,
            img_src_path,
        )
        time.sleep(0.5)
    except TimeoutException:
        traceback.print_exc()
        print("Timeout. 이미지 추출 취소: 해당 건은 추출 안되고 그냥 건너뜀")
        # ESC 키를 보내어 팝업을 무시
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        ).send_keys(Keys.ESCAPE)
    except NoSuchElementException:
        traceback.print_exc()
        print("Element not found. 이미지 추출 취소")
        # ESC 키를 보내어 팝업을 무시
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        ).send_keys(Keys.ESCAPE)


def select_second_tab(driver):
    # 두 번째 탭으로 이동
    element_to_click = driver.find_element(By.XPATH, '//*[@id="teamfresh"]/div/div/ul/li[2]/a')
    element_to_click.click()


def embed_js_for_tabselection(driver):
    # 페이지의 HTML 내용 가져오기
    html_content = driver.page_source

    # 탭선택 가능하게 하는 JavaScript snippet
    javascript_snippet = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var tabs = document.querySelectorAll('.nav-item .nav-link');
        var tabPanes = document.querySelectorAll('.tab-content .tab-pane');
        tabs.forEach(function(tab, index) {
            tab.addEventListener('click', function(event) {
                event.preventDefault();
                tabs.forEach(t => t.classList.remove('active'));
                tabPanes.forEach(pane => pane.classList.remove('active'));
                tab.classList.add('active');
                tabPanes[index].classList.add('active');
            });
        });
    });
    </script>
    """
    # Insert the JavaScript snippet before the closing </body> tag
    html_content = html_content.replace("</body>", javascript_snippet + "</body>")
    return html_content


def get_css_and_link_to_local(driver, html_content, save_root_path):
    # 'css' 및 'js' 폴더 생성
    css_folder = "css"
    os.makedirs(os.path.join(save_root_path, css_folder), exist_ok=True)

    # CSS 및 JavaScript 파일 처리
    for tag in ["link"]:
        elements = driver.find_elements(By.TAG_NAME, tag)
        for element in elements:
            href = element.get_attribute("href") if tag == "link" else element.get_attribute("src")
            if href and ((tag == "link" and "stylesheet" in element.get_attribute("rel")) or tag == "script"):
                # 절대 URL로 변환
                href = urljoin(remote_url, href)
                file_name = href.split("/")[-1]
                file_path = os.path.join(save_root_path, css_folder, file_name)

                # 파일 다운로드 및 저장
                if not os.path.exists(file_path):
                    response = requests.get(href)
                    with open(file_path, "wb") as file:
                        file.write(response.content)
                # HTML 내용에서 링크 경로 수정

                new_href = os.path.join('../../..', css_folder, file_name)
                old_href = os.path.join("/static", css_folder, file_name)
                # ic(old_href)
                # ic(new_href)
                html_content = html_content.replace(old_href, new_href)
    return html_content


def get_file_content_chrome(driver, uri):
    result = driver.execute_async_script(
        """
        var uri = arguments[0];
        var callback = arguments[1];
        var xhr = new XMLHttpRequest();
        xhr.responseType = 'arraybuffer';
        xhr.onload = function() {
            var reader = new FileReader();
            reader.readAsDataURL(new Blob([xhr.response]));
            reader.onloadend = function() {
                callback(reader.result);
            }
        };
        xhr.onerror = function() { callback(xhr.status) };
        xhr.open('GET', uri);
        xhr.send();
    """,
        uri,
    )
    if isinstance(result, int):
        raise Exception("Request failed with status %s" % result)
    return base64.b64decode(result.split(",")[1])


def navigate_to_page(url, wait_xpath, sec_to_wait=5):
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
        password_field.send_keys("dummypassword")
        original_window = driver.current_window_handle
        original_windows = driver.window_handles
        # 로그인 버튼 클릭
        login_button = driver.find_element(By.XPATH, '//*[@id="teamfresh"]/div/div/form/button')
        login_button.click()
    except Exception as e:
        print("로그인 페이지를 찾을 수 없습니다:", e)
    return original_window, original_windows


# 한국어 환경을 설정합니다.
# 윈도우의 경우 locale.setlocale(locale.LC_TIME, 'Korean') 를 사용하세요.
locale.setlocale(locale.LC_TIME, "ko_KR.UTF-8")


def parse_korean_month_year(month_year_str):
    # "1월 2024" 형식의 문자열을 datetime.date 객체로 변환합니다.
    return datetime.datetime.strptime(month_year_str, "%B %Y").date()


def format_date_korean(date):
    # 날짜를 "1월 2024" 형식으로 변환합니다.
    return date.strftime("%B %Y")


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
    print('show_daily_data ---------------')
    select_date(driver, datetime.date(year, month, day))

    # Click the search button
    search_button = driver.find_element(By.XPATH, "//*[@id='searchBtn']")
    search_button.click()


def get_all_table_data(driver):
    # Now proceed with the rest of the script
    # Extract table data and store it in a DataFrame
    table = driver.find_element(
        By.XPATH, "//*[@id='teamfresh']/div[2]/div[2]/div[2]/table"
    )
    rows = table.find_elements(By.TAG_NAME, "tr")
    # 데이터 행이 없는 경우 None을 반환
    if len(rows) <= 1:  # 헤더 행만 존재하면 데이터 행이 없는 것으로 간주
        print('요약 테이블에 발견된 행이 없음.')
        return None
    data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        data.append([col.text for col in cols])

    df = pd.DataFrame(data[1:], columns=[col.text for col in rows[0].find_elements(By.TAG_NAME, "th")])
    df["tms상세주소"] = pd.Series(dtype="str")
    return df


def create_filename_from_url(url, day, save_root, *sub_folders):
    # 폴더 경로를 구성합니다. save_root 다음에 sub_folders 요소들을 추가합니다.
    folder_path = os.path.join(save_root, *sub_folders)
    # 폴더가 존재하지 않으면 생성합니다.
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    url_parts = url.split("/")
    a = url_parts[-3]  # 마지막에서 세 번째 요소
    b = url_parts[-1]  # 마지막 요소
    filename = f"{a}-{day}-{b}.html"
    return os.path.join(folder_path, filename)


def create_filename_from_id(df, index, id_column, save_root, sub_folders):
    folder_path = os.path.join(save_root, *sub_folders)
    # 폴더가 존재하지 않으면 생성합니다.
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    identifier = df.at[index, id_column]
    filename = f"{identifier}.html"
    file_path = os.path.join(save_root, *sub_folders, filename)
    return file_path


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


class DataFrameSaveError(Exception):
    def __init__(self, message, file_path, dataframe):
        super().__init__(message)
        self.file_path = file_path
        self.dataframe = dataframe

    def __str__(self):
        return f"{super().__str__()}\nFile path: {self.file_path}\nDataFrame content:\n{self.dataframe}"


def save_dataframe_to_csv(df, filename, sub_folder, write_mode='auto'):
    # 지정된 서브 폴더 경로를 생성합니다.
    save_path = os.path.join("./", sub_folder)
    # 폴더가 존재하지 않으면 생성합니다.
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    file_path = os.path.join(save_path, filename)
    if 'shipping' in filename:
        df['실수령자명'] = df['실수령자명'].str.replace('\n', ' ')
    else:
        df['반품자명'] = df['반품자명'].str.replace('\n', ' ')
    # 파일이 존재하는 경우 데이터를 추가하고, 존재하지 않는 경우 새 파일을 생성합니다.
    try:
        if os.path.exists(file_path):
            df.to_csv(
    file_path,
    mode="a" if write_mode == 'auto' else write_mode,
    header=True if write_mode == 'w' else False,
    index=False,
    encoding="utf-8-sig",
     escapechar='\\')
        else:
            # 수거: Unkown,No.,최종상태,반품번호,거래처명,반품자명,회수상태,대분류,입고,반납,배송특이사항,기본주소,상세주소,공동현관PWD,공동현관PWD (소비자),고객요청사항,최종권역,수량,고객사반품번호,바코드생성여부,상세보기,tms상세주소
            # 배송: Unkown,No.,최종상태,주문번호,거래처명,실수령자명,입고,출고,배송,지연,대분류,운송료반환여부,배송특이사항,기본주소,상세주소,공동현관PWD,공동현관PWD (소비자),고객요청사항,수량,고객사주문번호,상세보기,tms상세주소
            df.to_csv(
    file_path,
    mode="w" if write_mode == 'auto' else write_mode,
    header=True if write_mode == 'w' else False,
    index=False,
    encoding="utf-8-sig",
     escapechar='\\')
    except csv.Error as e:
        print(f"CSV writing error ignored: {e}")
        print(f"File path: {file_path}")
        print(f"DataFrame content:\n{df}")
        raise DataFrameSaveError(f"CSV writing error: {e}", file_path, df)

# https://tms.teamfresh.co.kr/tcc/delivery/report


def process_tcc_page(driver, tcc_page_url, yy, mm, dd, ym, list_only=False):
    print(f'process_tcc_page 시작-----------------list_only?{list_only}')
    chk_elm_xpath = '//*[@id="teamfresh"]/div[2]/div[2]/form/div/div/div[1]/div/div/label/div[1]' if 'delivery' in tcc_page_url else '//*[@id="teamfresh"]/div[2]/div[2]/div[1]/div/div/button[4]'
    navigate_to_page(tcc_page_url, chk_elm_xpath, 3)

    show_daily_data(driver, yy, mm, dd)
    time.sleep(2)
    df = get_all_table_data(driver)
    print(f'shown data : len({df}) ----------')
    if df is None:
        return None
    if list_only:
        return df
    # buttons_xpath = '//*[@id="teamfresh"]/div[2]/div[2]/div[2]/table/tbody/tr/td[21]/button' if "delivery" in driver.current_url else '//*[@id="teamfresh"]/div[2]/div[2]/div[2]/table/tbody/tr/td[22]/button'
    buttons_xpath = '//button[@class="sc-mkiqe0-0 btn btn-outline-secondary btn-sm"]'
    report_size = len(driver.find_elements(By.XPATH, buttons_xpath))
    nums_of_bttns = len(df)

    operation_type = '배송' if 'delivery' in driver.current_url else '수거'
    send_slack_message(
        slack_webhook_url,
        f"`{input_date}일` TMS상세 보고서 수집전 `{operation_type}`결과 보고 테이블의 내역과 상세페이지 버튼의 갯수비교",
        f"요약테이블 보고서 수:`{report_size}` \n"
        + f"요약테이블 내 버튼 수:`{nums_of_bttns}`",
        report_size == nums_of_bttns,
    )
    if report_size != nums_of_bttns:
        # 웹페이지의 테이블의 데이터 수와 버튼의 갯수가 맞지 않으므로 문제1
        raise ValueError("Mismatch between number of rows in DataFrame and number of detail buttons")

    main_window_handle = driver.current_window_handle

    for i, button in enumerate(driver.find_elements(By.XPATH, buttons_xpath, )):
        button.click()
        time.sleep(1)

        for handle in driver.window_handles:
            if handle != main_window_handle:
                driver.switch_to.window(handle)
                break
        # 상세 페이지 처리 로직
        which_step = '배송' if 'shipping' in driver.current_url else '수거'
        id_column = '주문번호' if which_step == '배송' else '반품번호'

        select_second_tab(driver)
        time.sleep(1)
        get_all_sms(driver)
        get_image(driver, f"./tms/{which_step}/{ym}")
        if "shipping" in driver.current_url:
            remove_claim_button(driver)
        html_content = embed_js_for_tabselection(driver)
        html_content = get_css_and_link_to_local(driver, html_content, "./tms")
        # detail_html_file_path = create_filename_from_id(driver.current_url, f"{yy:04d}{mm:02d}{dd:02d}", f"./tms/{which_step}/{ym}/html")
        detail_html_file_path = create_filename_from_id(df, i, id_column, "./tms", [which_step, ym, "html"])

        with open(detail_html_file_path, "w", encoding="utf-8") as file:
            file.write(html_content)
        print(f'{detail_html_file_path} 상세페이지 저장')
        df.at[i, "tms상세주소"] = driver.current_url
        df.at[i, "상세보기"] = detail_html_file_path

        driver.close()
        driver.switch_to.window(main_window_handle)
        # TODO: debugging 끝나면 제거할 것!
        # if i > 2:
        #     break
    print('process_tcc_page 종료-----------------')
    return df


def filter_dataframe_by_date(file_name, input_date, dataframe, rem_this_df=False):
    # 주어진 dataframe 에 input_date의 데이터가 있으면 이를 제외한 데이터를 반환(rem_this_df=True일 때) 하거나
    # 주어진 dataframe 에 input_date의 데이터가 있으면 이 데이터만 반환(rem_this_dfe=False일 때)
    # 날짜 부분 추출
    if 'shipping' in file_name:
        dataframe['date_portion'] = dataframe['주문번호'].str[0:8]
    else:
        dataframe['date_portion'] = dataframe['반품번호'].str[1:9]
    filtered_data = None
    if rem_this_df:
        filtered_data = dataframe[dataframe['date_portion'] != input_date.replace('-', '')]
    else:
        # '-'를 제거한 입력 날짜와 일치하는 행 필터링
        filtered_data = dataframe[dataframe['date_portion'] == input_date.replace('-', '')]
    return filtered_data


#  ./tms/tms_return.csv 나 deliver.csv 에 input_date 의 데이터가 있는 지 점검하고 해당 데이터들을 반환
def check_existing_data(file_name, directory, input_date):
    file_path = os.path.join(directory, file_name)
    if not os.path.exists(file_path):
        return None  # File does not exist, no existing data to check
    existing_data = pd.read_csv(file_path, )
    # Unkown,No.,최종상태,반품번호,거래처명,반품자명,회수상태,대분류,운송료반환여부,입고,반납,배송특이사항,기본주소,상세주소,공동현관PWD,공동현관PWD (소비자),고객요청사항,최종권역,수량,고객사반품번호,바코드생성여부,상세보기,tms상세주소

    existing_data = filter_dataframe_by_date(file_name, input_date, existing_data)

    return existing_data


def load_and_replace_data(file_name, df_all, operation_type, input_date):
    existing_data = check_existing_data(file_name, "./tms", input_date)
    len_existing_data = 0 if existing_data is None else len(existing_data)

    print(f"{input_date}일에 기존 {operation_type} 데이터 {len_existing_data}건이 발견되었습니다.")

    if len_existing_data > 0:
        replace_data_yn = input(f"기존 {operation_type} 데이터를 대체하시겠습니까? (yes/no): ")
        if replace_data_yn.lower() == "yes":
            # 해당하는 날짜의 데이터만 전체 데이터에서 빼기
            df_all = filter_dataframe_by_date(file_name, input_date, df_all, rem_this_df=True)
            print(f" {input_date}일의 {operation_type} 데이터 존재하여 수집후 덮어쓰기 결정")
    else:
        replace_data_yn = 'new'
        print(f"{input_date}일의 {operation_type} 데이터 신규 수집후 추가 결정")
    return df_all, replace_data_yn


def process_and_save_data(df, file_name, folder_path, input_date, operation_type, url, list_only=False):
    """_summary_

    Args:
        df (_type_): 지정된 날짜에 해당하는 리스트의 값들을 제외한 모든 데이터
        file_name (_type_): TTMS 리스트의 테이블들의 모든 날짜들의 값을 저장하고 있는 csv파일
        folder_path (_type_): ./tms
        input_date (_type_): 수집해야하는 날짜로 확인해야하는 날짜의 전일, 즉 어제날짜
        operation_type (_type_): 수거 또는 배송
        url (_type_): TMS에 수거 또는 배송 보고서를 보여주는 각각의 페이지 url
        list_only (bool, optional): 방문한 페이지에서 날짜 조회로 나온 테이블 list만 저장할 지를 알려주는 플래그, 테이블만 저장이면 True,  테이블 맨 끝에 있는 버튼을 눌러 상세 html파일도 저장할땐 False _. Defaults to False.
    """
    replace_data_yn = 'yes' if df is not None else 'new'

    print(f"{input_date}일의 tms {operation_type} 데이터 추출 시작 (작업 타입: {operation_type}보고서 수집)")

    yy, mm, dd, ym = validate_and_extract_date_parts(input_date)
    data_frame = process_tcc_page(driver, url, yy, mm, dd, ym, list_only)
    wmode = 'a'
    save_result = '저장전'
    save_cnt = -1
    if data_frame is None or len(data_frame) == 0:
        save_result = f'수집된 데이터 테이블에 보고내역이 없어 {file_name}에 저장없이 종료'
        save_cnt = 0
        print(f'{input_date}일에 {operation_type} 데이터 테이블 없음: {save_result}')
    else:
        # 데이터 병합
        if replace_data_yn == 'yes' and df is not None:
            combined_df = pd.concat([df, data_frame], ignore_index=True)
            wmode = 'w'
            save_result = f'수집된 데이터 테이블의 보고내역{len(data_frame)}건과 과거수집건 {len(df)} 개를 병합하여 {len(combined_df)}건을 {file_name}에 overwrite 저장'
        else:
            combined_df = data_frame
            save_result = f'수집된 데이터 테이블의 보고내역{len(data_frame)}건을 {file_name}에 append 저장'
        ic(replace_data_yn)
        save_cnt = len(combined_df)
        save_dataframe_to_csv(combined_df, file_name, folder_path, write_mode=wmode)
        print(f'{input_date}일 {operation_type} 데이터 기록 완료: {save_result} ')

    send_slack_message(
        slack_webhook_url,
        f"`{input_date}일` TMS보고서 수집후 `{operation_type}`결과보고 테이블의 내역과 기존 데이터를 병합 저장한 결과",
        f"저장된 데이터 수:`{save_cnt}` \n"
        + f"저장대상:" + ("`보고내역만`" if list_only else "`보고내역+상세내용 html`") + "\n"
        + f"파일 쓰기 모드(a/w):`{wmode}`\n"
        + f"보고내역 저장 방법:`{save_result}`",
        save_cnt > 0,
    )


if __name__ == "__main__":
    try:
        input_date = None
        # 실행 인자 확인
        if len(sys.argv) > 1:
            input_date = sys.argv[1]
        else:
            input_date = datetime.datetime.now().strftime("%Y-%m-%d")
            print("No date argument provided. Using today's date:", input_date)

        # 추가: 작업 타입 인자 확인
        operation_type = None
        if len(sys.argv) > 2:
            operation_type = sys.argv[2]
        else:
            operation_type = "모두"  # 기본값으로 모두 수집
        if operation_type not in ['수거', '배송', '모두']:
            sys.exit()

        save_only_list = False
        if len(sys.argv) > 3:
            save_only_list = sys.argv[3] == '리스트'

        # print(f"{input_date}일의 tms 데이터 추출 시작")
        # 메인 코드 실행 부분
        # profile_path = "~/.config/google-chrome/Profile 9"  # 집에서 작업할 때
        profile_path = "/home/max/.config/google-chrome/Default"  # 회사에서 작업할 때
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=" + profile_path)
        # UI 띄우지 않고 실행하기위한 옵션
        chrome_options.add_argument("--headless")  # Headless 모드 활성화
        chrome_options.add_argument("--no-sandbox")  # Sandbox 프로세스 비활성화
        chrome_options.add_argument("--disable-dev-shm-usage")  # 컨테이너 환경에서의 메모리 문제 방지

        chrome_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        # Load tms_shipping.csv into df_all_shipping
        df_all_shipping = None
        df_all_return = None
        try:
            if os.path.exists("./tms/tms_shipping.csv"):
                df_all_shipping = pd.read_csv("./tms/tms_shipping.csv")
            else:
                print("Shipping data file not found.")

            if os.path.exists("./tms/tms_return.csv"):
                df_all_return = pd.read_csv("./tms/tms_return.csv")
            else:
                print("Return data file not found.")
        except pd.errors.ParserError as e:
            print("ParserError:", e)
            with open("./tms/tms_return.csv", 'r') as file:
                lines = file.readlines()
                print("Error in line 2078:", lines[0])

        print("You can pass a date as an argument in YYYY-MM-DD format.")

        replace_shipping_data_yn = ''
        replace_return_data_yn = ''

        if operation_type == '배송':
            df_all_shipping, replace_shipping_data_yn = load_and_replace_data("tms_shipping.csv", df_all_shipping, '배송', input_date)
        elif operation_type == '수거':
            df_all_return, replace_return_data_yn = load_and_replace_data("tms_return.csv", df_all_return, '수거', input_date, )
        else:
            df_all_shipping, replace_shipping_data_yn = load_and_replace_data("tms_shipping.csv", df_all_shipping, '배송', input_date)
            df_all_return, replace_return_data_yn = load_and_replace_data("tms_return.csv", df_all_return, '수거', input_date, )

        remote_url = "https://tms.teamfresh.co.kr"
        original_window, original_windows = open_and_login(driver)
        time.sleep(2)

        close_new_window_and_return(driver, original_window, original_windows)
        df_to_pass = None  # None 이면 append 저장하고 값이 있으면 이 값을 이용해 overwrite저장함.
        if replace_shipping_data_yn in ['yes', 'new']:
            tcc_page_url1 = "https://tms.teamfresh.co.kr/tcc/delivery/report"
            df_to_pass = None if replace_shipping_data_yn == 'new' else df_all_shipping
            process_and_save_data(df_to_pass, "tms_shipping.csv", "./tms", input_date, "배송", tcc_page_url1, save_only_list)
        if replace_return_data_yn in ['yes', 'new']:
            df_to_pass = None if replace_return_data_yn == 'new' else df_all_return
            tcc_page_url2 = "https://tms.teamfresh.co.kr/tcc/return/report"
            process_and_save_data(df_to_pass, "tms_return.csv", "./tms", input_date, "수거", tcc_page_url2, save_only_list)

        driver.quit()  # 브라우저를 닫습니다.
        print(f"{input_date}일의 tms 데이터 추출 완료--------------------------")

    except Exception as e:
        error_message = f"오류 내용\n ```{str(e)}\n{traceback.format_exc()}```"
        print(error_message)
        # 오류 발생 시 슬랙 메시지 전송
        send_slack_message(slack_webhook_url, "TMS 데이터 추출 오류", error_message, ok=False)
