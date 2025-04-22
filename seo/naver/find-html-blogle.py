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


def random_sleep(a, b):
    sleep_time = random.uniform(a, b)  # generates a random float number between 1 and 2
    time.sleep(sleep_time)


def get_driver_with_random_user_agent():
    options = Options()
    options.page_load_strategy = 'eager'  # Or 'none'
    driver = webdriver.Firefox(options=options)
    return driver


mcab = mecab.MeCab()
ic.disable()


# cleanb_text = []
# with open("cleanb_contents.txt", "r") as f:
#     for line in f:
#         cleanb_text.append(line.strip())
# cleanb_content_words = mcab.morphs(cleanb_text[-1])


def parse_domain_name(article_url):
    match = re.match(r"https?://(.[^/]+)/", article_url)
    if match:
        return match.group(1)
    else:
        return None


def get_urls_from_href(driver, result_links):
    article_urls = []
    for result_link in result_links:
        article_url = result_link.get_attribute("href")
        article_urls.append(article_url)
    return article_urls


competitor_domains = [
    "cleanb.life",
    "cleanbedding.kr",
    "youtube"
]

ignorable_text = []


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


def crawl_website():
    gdriver = get_driver_with_random_user_agent()
    local_html = r'file:///home/damianos/cleanbeding/seo/naver/naver_blog_articles.html'
    gdriver.get(local_html)
    wait = WebDriverWait(gdriver, 10)
    wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
    random_sleep(2, 3)

    article_urls = []
    domains = []
    meta_data = []
    title_text = []
    text_content = []
    detected = []
    blogger_name = []
    blogger_url = []
    # while True:

    existing_blog_articles = None
    if os.path.exists('naver_blogs.csv'):
        # Load the existing data
        existing_blog_articles = pd.read_csv('naver_blogs.csv')
    else:
        # If the file doesn't exist, create an empty DataFrame
        existing_blog_articles = pd.DataFrame(
            columns=['url', 'title_text', 'meta_data', 'detected', 'blogger_name', 'blogger_url'])
        existing_blog_articles.to_csv(
            "naver_blogs.csv",
            header=True,
            columns=['url', 'title_text', 'meta_data', 'detected', 'blogger_name', 'blogger_url'])
    df = pd.DataFrame(columns=['url', 'title_text', 'meta_data', 'detected', 'blogger_name', 'blogger_url'])

    result_links = gdriver.find_elements(By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/section[2]/html-persist/div/more-contents/div/ul/li/div/div/a')
    all_urls = get_urls_from_href(gdriver, result_links)

    elms = gdriver.find_elements(By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/section[2]/html-persist/div/more-contents/div/ul/li/div/div/div[1]/div[2]/span/span/span[2]/a')
    blogger_name = [elm.text for elm in elms]
    blogger_url = [elm.get_attribute('href') for elm in elms]
    print(all_urls)
    print(blogger_name)
    print(blogger_url)
    i = 0
    # current_url = gdriver.current_url
    while i < len(all_urls):
        if i == 0:
            driver = get_driver_with_random_user_agent()
        text_of_this_site = ''
        article_url = all_urls[i]
        # Check if the URL is already in the DataFrame
        if article_url in existing_blog_articles['url'].values:
            print(f"naver_blogs.csv 에 기존 추출한 정보 존재하여 Skip : {article_url} ")
            i += 1
            continue
        if article_url is None or ignore_url(article_url):
            i += 1
            continue

        try:
            driver.get(article_url)
            wait = WebDriverWait(driver, 10)
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
            time.sleep(0.1)
            # element = driver.find_element(By.TAG_NAME, "body")
            # element.send_keys(Keys.ESCAPE)  # time.sleep(2)
            random_sleep(1, 3)

        except WebDriverException as e:
            i += 1
            print("페이지 찾을 수 없음")
            continue
        except UnexpectedAlertPresentException as e:
            element = driver.find_element(By.TAG_NAME, "html")
            element.send_keys(Keys.ESCAPE)  # time.sleep(2)
            time.sleep(0.1)
        except TimeoutException:
            print(f"timed out to get {article_url}")
            i += 1
            continue
        article_urls.append(article_url)
        dname = parse_domain_name(article_url)
        domains.append(dname)

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
        # text_content.append(meta_data[-1])  # ?????
        text_of_this_site = title_text[-1] + ' ' + text_content[-1] + ' ' + meta_data[-1]
        keywords = ["cleanbedding.kr", "클린베딩", "클린 베딩"]
        detected.append("None")

        for keyword in keywords:
            if keyword in text_of_this_site:
                detected[-1] = keyword
                break
        print(i, ':', title_text[-1], '\t', detected[-1], '\t', article_urls[-1])

        blog_article = {
            "url": article_urls[-1],
            "title_text": title_text[-1],
            "meta_data": meta_data[-1],
            "detected": detected[-1],
            "blogger_name": blogger_name[i],
            "blogger_url": blogger_url[i]
        }
        article_df = pd.DataFrame([blog_article])  # Convert dict to DataFrame
        df = pd.concat([df, article_df], ignore_index=True)
        df.to_csv(
            "naver_blogs.csv",
            mode='a',
            header=False,
            columns=['url', 'title_text', 'meta_data', 'detected', 'blogger_name', 'blogger_url'])
        i += 1

    # driver.close()
    return domains, article_urls, title_text, meta_data, text_content, detected  # , relevancy_scores, similarity_scores, quality_scores


if __name__ == "__main__":
    domains, article_urls, title_text, meta_data, text_content, detected, = [], [], [], [], [], []
    domains, article_urls, title_text, meta_data, text_content, detected = crawl_website()

    # columns=['url', 'title_text', 'meta_data', 'detected'])
    # df = pd.DataFrame(blog_articles)
    # df.to_csv("naver_blogs.csv", columns=['domain', 'title_text', 'url', 'meta_data', 'relevancy_score', 'similarity_score', 'quality_score', 'text_content'])
