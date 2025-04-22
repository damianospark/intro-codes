# -*- coding: utf-8 -*-
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from icecream import ic
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import mecab
import re
import hgtk

import pandas as pd

import string
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

mcab = mecab.MeCab()


def random_sleep(a, b):
    sleep_time = random.uniform(a, b)  # generates a random float number between 1 and 2
    time.sleep(sleep_time)


def parse_domain_name(competitor_url):
    match = re.match(r"https?://(.[^/]+)/", competitor_url)
    if match:
        return match.group(1)
    else:
        return None


def get_driver_with_random_user_agent():
    options = Options()
    options.page_load_strategy = 'eager'  # Or 'none'
    driver = webdriver.Firefox(options=options)
    return driver


def check_detected(driver, competitor_url):
    title_text = None
    text_content = None
    meta_data = None
    try:
        driver.get(competitor_url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
        time.sleep(0.1)
        element = driver.find_element(By.TAG_NAME, "body")
        element.send_keys(Keys.ESCAPE)  # time.sleep(2)
        time.sleep(0.1)
    except WebDriverException as e:
        print("페이지 찾을 수 없음")
        return ''
    except UnexpectedAlertPresentException as e:
        element = driver.find_element(By.TAG_NAME, "html")
        element.send_keys(Keys.ESCAPE)  # time.sleep(2)
        time.sleep(0.1)
        return ''
    except TimeoutException:
        print(f"timed out to get {competitor_url}")
        return ''

    try:
        title_text = driver.title
    except UnexpectedAlertPresentException as e:
        print(e)
        title_text = ""
    except NoSuchElementException as e:
        title_text = ""
        print(e)

    try:
        text_content = driver.find_element(By.TAG_NAME, "body").text
    except NoSuchElementException as e:
        text_content = ""
        print("text_content not found")
        print(e)
    # print('title_text:', title_text)
    try:
        meta_data = driver.find_element(By.XPATH, "//*[@name='description']").get_attribute("content")
    except StaleElementReferenceException as e:
        meta_data = ""
    except NoSuchElementException as e:
        meta_data = ""
        print('description 발견 안됨', e)

    text_of_this_site = title_text + ' ' + text_content + ' ' + meta_data
    keywords = ["cleanbedding.kr", "클린베딩", "클린 베딩"]
    detected = "None"

    for keyword in keywords:
        if keyword in text_of_this_site:
            detected = keyword
            break
    print(detected, '\t', competitor_url)
    return detected


drv = get_driver_with_random_user_agent()
columns = ['keyword', 'domain', 'url', 'title_text', 'meta_data', 'text_content', 'detected']

# Read the CSV file into a DataFrame
df = pd.read_csv('ourlinks.csv', usecols=columns)
df = df.drop_duplicates()

df['detected'] = df['url'].apply(lambda x: check_detected(drv, x))

# Filter the DataFrame to only include rows where 'detected' is 'Found'
# filtered_df = df[df['detected'] == 'Found']

# Write the filtered DataFrame to a new CSV file
df.to_csv('final_ourlinks.csv', index=False)
