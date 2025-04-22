import numpy as np
import unittest
import argparse
import datetime
import sys
import csv
import os
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium import webdriver
from urllib.parse import urljoin
import traceback
from icecream import ic
import base64
import pandas as pd
import locale
from io import StringIO
# from needle.cases import NeedleTestCase
# from needle.engines.perceptualdiff_engine import Engine as PerceptualDiffEngine
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests


def get_web_driver():
    # profile_path = "~/.config/google-chrome/Profile 9" #집에서 작업할 때
    profile_path = "/home/max/.config/google-chrome/Default"  # 회사에서 작업할 때
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=" + profile_path)
    # UI 띄우지 않고 실행하기위한 옵션
    chrome_options.add_argument("--headless")  # Headless 모드 활성화
    cpath = ChromeDriverManager().install()
    print('drifver path', cpath)
    return webdriver.Chrome(executable_path=cpath, options=chrome_options)


driver = get_web_driver()
driver.get("http://cleanb.life")
driver.set_window_size(412, 975)
# 검색창 엘리먼트 가져오기
elm_body = driver.find_element(By.XPATH, '/html/body')

# 검색창 엘리먼트만 스크린샷
screenshot = elm_body.get_screenshot_as_png()
screenshot
