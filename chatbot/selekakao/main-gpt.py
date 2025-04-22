# -*- coding: utf-8 -*-

import datetime
import json
import sys
# from selenium.webdriver.support.ui import WebDriverWait
import time
from typing import Union

import requests
from fastapi import FastAPI
from icecream import ic
from lxml import html
from pydantic import BaseModel
from selenium import webdriver
from selenium.common.exceptions import \
    TimeoutException  # Import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def sleepcount(n, l):
    print(f'{l} 대기', end=':')
    for i in range(n, -1, -1):
        print(i, end=' ')
        sys.stdout.flush()
        time.sleep(1)
    print()  # To move to next line after the loop ends.


def wait_return_true(driver, pth, for_what, how_long):
    elm = None
    try:
        # Wait up to 10 seconds until the element is present
        # element_present = EC.presence_of_element_located((By.XPATH, pth))
        element_present = EC.presence_of_element_located((By.XPATH, pth))
        elm = WebDriverWait(driver, how_long).until(element_present)
    except TimeoutException:
        print(f"Timed out waiting for {for_what} being clickable")
    finally:
        print(for_what, 'complete')
    if elm is not None:
        return True
    return ""


def wait_and_click(driver, pth, for_what, how_long):
    elm = None
    try:
        # Wait up to 10 seconds until the element is present
        # element_present = EC.presence_of_element_located((By.XPATH, pth))
        element_clickable = EC.element_to_be_clickable((By.XPATH, pth))
        elm = WebDriverWait(driver, how_long).until(element_clickable)
        elm.click()
    except TimeoutException:
        print(f"Timed out waiting for {for_what} being clickable")
    finally:
        print(for_what, 'complete')
    return elm


chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
chrome_options.add_argument("user-data-dir=/home/damianos/.config/google-chrome")
chrome_options.add_argument("profile-directory=Profile 4")


wait_return_true(driver, '//*[@id="__next"]/div[1]/div[1]/div[2]', 'Welcome to ChatGPT', 30)
wait_and_click(driver, '//*[@id="__next"]/div[1]/div[1]/div[4]/button[1]/div', 'ChatGPT Login', 30)
wait_and_click(driver, '/html/body/div/main/section/div/div/div/div[4]/form[2]/button', 'Continue with Google button click', 30)

wait_return_true(driver, '//*[@id="headingText"]/span', 'Sign In', 10)
elm = wait_and_click(driver, '//*[@id="identifierId"]', 'Google ID Field Click', 10)
if elm is not None:
    elm.send_keys('dcba@gmail.com')
driver.find_element(By.XPATH, '//*[@id="identifierNext"]/div/button/span').click()

# wait_return_true(driver,'//*[@id="headingText"]/span','Sign In',10) #Hi Damianos
elm = wait_and_click(driver, '//*[@id="password"]/div[1]/div/div[1]/input', 'Password Input Field clicked', 10)
if elm is not None:
    elm.send_keys('12345678')


class Ask(BaseModel):
    name: str
    ask_time: str
    ask_text: str
    answer_text: str
    answer_time: str


app = FastAPI()


@app.post("/ask/")
async def create_item(ask: Ask):
    now = datetime.datetime.now()

    ask.answer_text = '기본 답변'
    ask.answer_time = now.strftime('%m%d_%H%M%S')
    return ask
