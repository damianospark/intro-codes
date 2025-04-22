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

# import MeCab
import mecab
import re
import hgtk

import pandas as pd

import string
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

import random
from fake_useragent import UserAgent
# from http_request_randomizer.requests.proxy.requestProxy import RequestProxy


# req_proxy = RequestProxy()  # you may get different number of proxy when  you run this at each time
# proxies = req_proxy.get_proxy_list()

# ua = UserAgent()


# from selenium.webdriver.common.proxy import Proxy, ProxyType
def scroll_to_end(driver):
    old_position = 0
    new_position = None

    while new_position != old_position:
        # Get old scroll position
        old_position = driver.execute_script(
            ("return (window.pageYOffset !== undefined) ?"
             " window.pageYOffset : (document.documentElement ||"
             " document.body.parentNode || document.body);"))
        # Sleep and Scroll
        time.sleep(1)
        ActionChains(driver).send_keys(Keys.END).perform()
        # Get new position
        new_position = driver.execute_script(
            ("return (window.pageYOffset !== undefined) ?"
             " window.pageYOffset : (document.documentElement ||"
             " document.body.parentNode || document.body);"))


def random_sleep(a, b):
    sleep_time = random.uniform(a, b)  # generates a random float number between 1 and 2
    time.sleep(sleep_time)


def get_driver_with_random_user_agent():
    # def get_desktop_user_agent():
    #     ua = UserAgent()
    #     desktop_browsers = ['chrome', 'firefox', 'safari', 'opera', 'ie']
    #     browser = random.choice(desktop_browsers)
    #     return getattr(ua, browser)
    options = Options()
    options.page_load_strategy = 'eager'  # Or 'none'
    # user_agent = get_desktop_user_agent()
    # options.add_argument('user-agent=' + user_agent)
    driver = webdriver.Firefox(options=options)
    # driver.set_window_size(1920, 1024)
    # driver.set_page_load_timeout(30)
    return driver


# def get_driver_with_random_user_agent():
#     def get_desktop_user_agent():
#         ua = UserAgent()
#         desktop_browsers = ['chrome', 'firefox', 'safari', 'opera', 'ie']
#         browser = random.choice(desktop_browsers)
#         return getattr(ua, browser)
#     options = webdriver.ChromeOptions()
#     # Adding argument to disable the AutomationControlled flag
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     # Exclude the collection of enable-automation switches
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     # Turn-off userAutomationExtension
#     options.add_experimental_option("useAutomationExtension", False)

#     options.add_experimental_option("detach", True)
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     user_agent = get_desktop_user_agent()
#     options.add_argument('user-agent=' + user_agent)
#     driver = webdriver.Chrome(options=options)
#     driver.set_window_size(1198, 1128)
#     # Changing the property of the navigator value for webdriver to undefined
#     driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
#     return driver

# def get_driver_with_random_user_agent():
#     options = webdriver.ChromeOptions()
#     # Adding argument to disable the AutomationControlled flag
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     # Exclude the collection of enable-automation switches
#     # options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     # Turn-off userAutomationExtension
#     # options.add_experimental_option("useAutomationExtension", False)

#     # options.add_experimental_option("detach", True)
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     driver = uc.Chrome(options=options)
#     driver.set_window_size(1198, 1128)
#     # Changing the property of the navigator value for webdriver to undefined
#     driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
#     return driver


mcab = mecab.MeCab()
ic.disable()


cleanb_text = []
with open("cleanb_contents.txt", "r") as f:
    for line in f:
        cleanb_text.append(line.strip())
cleanb_content_words = mcab.morphs(cleanb_text[-1])


def parse_domain_name(competitor_url):
    match = re.match(r"https?://(.[^/]+)/", competitor_url)
    if match:
        return match.group(1)
    else:
        return None


def get_urls_from_href(driver, result_links):
    competitor_urls = []
    for result_link in result_links:
        competitor_url = result_link.get_attribute("href")
        competitor_urls.append(competitor_url)
    return competitor_urls


competitor_domains = [
    "cleanb.life",
    "cleanbedding.kr",
    "youtube"
]

ignorable_text = [".pdf", ".ppt", ".hwp", "cleanbedding.kr", "google.com"]


# driver = webdriver.Firefox(options=options)
# Set timeout to 10 seconds


def ignore_url(url):
    for igtxt in ignorable_text:
        if igtxt in url:
            return True

    dname = parse_domain_name(url)
    for domain in competitor_domains:
        if domain in dname:
            return True
    return False


def check_last_element(driver):
    try:
        element = driver.find_element(By.XPATH, '//div[@class="ClPXac Pqkn2e"]')
        return True
    except NoSuchElementException:
        return False


def crawl_website(keyword, existing_competitors, driver):
    gdriver = get_driver_with_random_user_agent()
    gdriver.get("https://www.google.com/search?q=" + keyword)
    wait = WebDriverWait(gdriver, 10)
    wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
    random_sleep(5, 7)

    # time.sleep(1)
    print("keyword", keyword)
    competitor_urls = []
    domains = []
    meta_data = []
    title_text = []
    text_content = []
    detected = []
    while True:
        result_links = gdriver.find_elements(By.XPATH, '//*[@id="res"]//div[@class="MjjYud"]//a')
        all_urls = get_urls_from_href(gdriver, result_links)

        i = 0
        current_url = gdriver.current_url
        while i < len(all_urls):
            if i == 0:
                driver = get_driver_with_random_user_agent()
            text_of_this_site = ''
            competitor_url = all_urls[i]
            # Check if the URL is already in the DataFrame
            if competitor_url in existing_competitors['url'].values:
                print(f"ourlinks.csv 에 기존 추출한 정보 존재하여 Skip : {competitor_url} ")
                i += 1
                continue
            if competitor_url is None or ignore_url(competitor_url):
                i += 1
                continue

            try:
                driver.get(competitor_url)
                wait = WebDriverWait(driver, 10)
                wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
                time.sleep(0.1)
                element = driver.find_element(By.TAG_NAME, "body")
                element.send_keys(Keys.ESCAPE)  # time.sleep(2)
                time.sleep(0.1)
            except WebDriverException as e:
                i += 1
                print("페이지 찾을 수 없음")
                continue
            except UnexpectedAlertPresentException as e:
                element = driver.find_element(By.TAG_NAME, "html")
                element.send_keys(Keys.ESCAPE)  # time.sleep(2)
                time.sleep(0.1)
            except TimeoutException:
                print(f"timed out to get {competitor_url}")
                i += 1
                continue
            competitor_urls.append(competitor_url)
            dname = parse_domain_name(competitor_url)
            domains.append(dname)
            # print("page opened -------")

            try:
                title_text.append(driver.title)
            except UnexpectedAlertPresentException as e:
                print(e)
                title_text.append("")
            except NoSuchElementException as e:
                title_text.append("")
                print(e)

            try:
                text_content.append(driver.find_element(By.TAG_NAME, "body").text)
                # print('-----------------------------------------')
                # print('text_content', text_content)
                # print('text_content length', len(text_content))
                # print('-----------------------------------------')
            except NoSuchElementException as e:
                text_content.append("")
                print("text_content not found")
                print(e)
            # print('title_text:', title_text)
            try:
                meta_data.append(driver.find_element(By.XPATH, "//*[@name='description']").get_attribute("content"))
            except StaleElementReferenceException as e:
                meta_data.append("")
            except NoSuchElementException as e:
                meta_data.append("")
                print('description 발견 안됨', e)
            ic(meta_data)
            # text_content.append(meta_data[-1])  # ?????
            text_of_this_site = title_text[-1] + ' ' + text_content[-1] + ' ' + meta_data[-1]
            if not (
                "cleanbedding.kr" in text_of_this_site or
                "클린베딩" in text_of_this_site or
                "클린 베딩" in text_of_this_site
            ):
                # print('무관한 사이트', dname)
                detected.append("None")
            else:
                # print('후보 사이트 발견', dname)
                detected.append("Found")
            # print('text processing...')
            # text_content_words = mcab.morphs(text_content[-1])
            # ic.enable()
            # ic(one_content, text_content[-1])
            # ic.disable()
            print(keyword, '\t', dname, '\t', detected[-1], '\t', competitor_url)
            i += 1
        driver.close()
        try:
            scroll_to_end(gdriver)
            # driver = get_driver_with_random_user_agent()
            # driver.get(current_url)
            # wait = WebDriverWait(driver, 10)
            # wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
            print("방문중이던 페이지를 떠나 이전 Google 검색페이지로 돌아옴")
            # next_bttn = gdriver.find_element(By.XPATH, '//*[@id="pnnext"]')
            if check_last_element(gdriver):
                print("서치 결과 마지막이라 해당 키워드 탐색 종료")
                break
            else:
                next_bttn = WebDriverWait(gdriver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="pnnext"]'))
                )
                if next_bttn:
                    random_sleep(3, 6)
                    next_bttn.click()
                    print("####### Next button clicked ######## ")
                    wait = WebDriverWait(gdriver, 10)
                    wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
        except NoSuchElementException:
            print("Next 버튼을 찾지 못해 종료")
            break

    # driver.close()
    return domains, competitor_urls, title_text, meta_data, text_content, detected  # , relevancy_scores, similarity_scores, quality_scores


def main():

    keywords2 = ['호텔 이불', '이불 구독 서비스', '정기 이불 교체', '호텔 이불 구독', '호텔 이불 구독 서비스', '호텔이불 쇼핑몰'
                 '호텔 이불 렌탈 서비스', '편리한 이불 관리', '이불 세탁 서비스', '혼자 사는 사람을 위한 호텔 이불 구독',
                 '소형 주거 공간 거주자를 위한 호텔 이불 구독', '임시 거주자를 위한 호텔 이불 구독', '건강 및 위생을 위한 호텔 이불 구독',
                 '친환경적인 소비자를 위한 호텔 이불 구독', '계절에 따라 호텔 이불 구독', '합리적인 소비를 위한 호텔 이불 구독',
                 '손님이 오실 때 호텔 이불', '출산직후의 산모를 위한 호텔 이불', 'SUV 또는 캠핑카 소유자를 위한 호텔 이불 구독', '애완 동물 소유자를 위한 호텔 이불 구독',
                 '민감한 피부/여드름 환자를 위한 호텔 이불 구독', '에어비앤비 운영을 위한 호텔 이불 구독', '세컨하우스를 위한 호텔 이불 구독', '공유주거를 위한 호텔 이불 구독']

    keywords1 = ['호텔 침구', '침구 구독 서비스', '정기 침구 교체', '호텔 침구 클리닝 서비스', '호텔침구 쇼핑몰'
                 '호텔 침구 렌탈 서비스', '편리한 침구 관리', '침구 세탁 서비스', '혼자 사는 사람을 위한 호텔 침구 구독',
                 '소형 주거 공간 거주자를 위한 호텔 침구 구독', '임시 거주자를 위한 호텔 침구 구독', '건강 및 위생을 위한 호텔 침구 구독',
                 '친환경적인 소비자를 위한 호텔 침구 구독', '계절에 따라 호텔 침구 구독', '합리적인 소비를 위한 호텔 침구 구독',
                 '손님이 오실 때 호텔 침구', '출산직후의 산모를 위한 호텔 침구', 'SUV 또는 캠핑카 소유자를 위한 호텔 침구 구독', '애완 동물 소유자를 위한 호텔 침구 구독',
                 '민감한 피부/여드름 환자를 위한 호텔 침구 구독', '에어비앤비 운영을 위한 호텔 침구 구독', '세컨하우스를 위한 호텔 침구 구독', '공유주거를 위한 호텔 침구 구독']
    # keywords0 = ['클린베딩', 'cleanbedding', 'cleanbedding.kr', '이불 구독 서비스', '침구 구독 서비스', '호텔 이불 구독 서비스', '호텔 침구 구독 서비스']
    keywords0 = ['호텔 이불 구독 서비스', '호텔 침구 구독 서비스', '침구 구독 서비스']
    keywords = keywords0  # +keywords1 + keywords2
    domains, competitor_urls, title_text, meta_data, text_content, detected, = [], [], [], [], [], []
    competitors = []
    if os.path.exists('ourlinks.csv'):
        # Load the existing data
        existing_competitors = pd.read_csv('ourlinks.csv')
    else:
        # If the file doesn't exist, create an empty DataFrame
        existing_competitors = pd.DataFrame(
            columns=['keyword', 'domain', 'url', 'title_text', 'meta_data', 'text_content', 'detected'])
        existing_competitors.to_csv(
            "ourlinks.csv",
            header=True,
            columns=['keyword', 'domain', 'url', 'title_text', 'meta_data', 'text_content', 'detected'])
    df = pd.DataFrame(columns=['keyword', 'domain', 'url', 'title_text', 'meta_data', 'text_content', 'detected'])
    # 구글의 첫 페이지만 확인
    drv = get_driver_with_random_user_agent()

    for j, keyword in enumerate(keywords):
        # if j > 3:
        #     break
        ic(keyword)
        domains, competitor_urls, title_text, meta_data, text_content, detected = crawl_website(
            keyword, existing_competitors, drv)

        for i in range(len(competitor_urls)):
            competitor = {
                "keyword": keyword,
                "domain": domains[i],
                "url": competitor_urls[i],
                "title_text": title_text[i],
                "meta_data": meta_data[i],
                "text_content": text_content[i],
                "detected": detected[i]
            }
            # competitors.append(competitor)
            # df = df.append(competitor, ignore_index=True)
            competitor_df = pd.DataFrame([competitor])  # Convert dict to DataFrame
            df = pd.concat([df, competitor_df], ignore_index=True)
        df.to_csv(
            "ourlinks.csv",
            mode='a',
            header=False,
            columns=['keyword', 'domain', 'url', 'detected'])
        # columns=['keyword', 'domain', 'url', 'title_text', 'meta_data', 'text_content', 'detected'])
    # df = pd.DataFrame(competitors)
    # df.to_csv("ourlinks.csv", columns=['domain', 'title_text', 'url', 'meta_data', 'relevancy_score', 'similarity_score', 'quality_score', 'text_content'])


if __name__ == "__main__":
    main()
