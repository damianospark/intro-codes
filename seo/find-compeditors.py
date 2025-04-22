# -*- coding: utf-8 -*-
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from icecream import ic
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.firefox.options import Options


# import MeCab
import mecab
import re
import hgtk

import pandas as pd

import string
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

mcab = mecab.MeCab()
ic.disable()


cleanb_text = []
with open("cleanb_contents.txt", "r") as f:
    for line in f:
        cleanb_text.append(line.strip())
cleanb_content_words = mcab.morphs(cleanb_text[-1])


# def similarity_score(cleanb_text_contents, text_context_words):
#     stop_words = set(stopwords.words('korean'))
#     stemmer = PorterStemmer()

#     tagger = Tagger()

#     cleanb_text_words = []
#     for word in cleanb_text_contents:
#         if word not in stop_words:
#             cleanb_text_words.append(stemmer.stem(word))

#     cleanb_text_morphs = []
#     with open("cleanb_contents.txt", "r") as f:
#         for line in f:
#             cleanb_text_morphs.extend(tagger.parse(line).split(" "))

#     text_context_words = []
#     for word in text_context_words:
#         if word not in stop_words:
#             text_context_words.append(stemmer.stem(word))

#     similarity_score = len(set(cleanb_text_morphs) & set(text_context_words)) / len(set(cleanb_text_morphs))

#     return similarity_score


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
    "cleanb",
    "cleanbedding",
    "naver",
    "wefun",
    "google",
    "news.mt",
    "chosun",
    "khan.co.kr",
    "tistory",
    "youtube",
    "facebook",
    "instagram",
    "sedaily",
    "koreadaily",
    "hanhyung",
    "nate.com",
    "booking.com",
    "hankookilbo",
    "economist",
    "go.kr",
    "newsis",
    "sentv",
    "korea.kr",
    "etoday",
    "hotels.com",
    "womansense", "hankyung", "knews", "hotel-all.ru",
    "hani", "yakup", "or.kr", "iammini", "joongang", "it.donga.com", "kbs.co.kr"]

ignorable_text = [".pdf", ".ppt", ".hwp"]

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_experimental_option("detach", True)
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-gpu")
# driver = webdriver.Chrome(options=chrome_options)
# driver.set_page_load_timeout(30)  # Set timeout to 10 seconds


driver = webdriver.Firefox()
options = Options()
options.page_load_strategy = 'eager'  # Or 'none'
driver = webdriver.Firefox(options=options)
driver.set_page_load_timeout(30)  # Set timeout to 10 seconds


def ignore_url(url):
    for igtxt in ignorable_text:
        if igtxt in url:
            return True

    dname = parse_domain_name(url)
    for domain in competitor_domains:
        if domain in dname:
            return True
    return False


def crawl_website(keyword, existing_competitors):
    driver.get("https://www.google.com/search?q=" + keyword)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
    # time.sleep(1)
    result_links = driver.find_elements(By.XPATH, "//*[@id='rso']//a")
    all_urls = get_urls_from_href(driver, result_links)

    competitor_urls = []
    domains = []
    meta_data = []
    title_text = []
    text_content = []
    relevancy_scores = []
    similarity_scores = []
    quality_scores = []
    i = 0
    while i < len(all_urls):
        text_of_this_site = ''
        competitor_url = all_urls[i]
        # Check if the URL is already in the DataFrame
        if competitor_url in existing_competitors['url'].values:
            print(f"competitors.csv 에 기존 추출한 정보 존재하여 Skip : {competitor_url} ")
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
        print(keyword, '\t', dname, '\t', competitor_url)
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
            print('-----------------------------------------')
            print('text_content', text_content)
            print('text_content length', len(text_content))
            print('-----------------------------------------')
        except NoSuchElementException as e:
            text_content.append("")
            print("text_content not found")
            print(e)
        # print('title_text:', title_text)
        try:
            meta_data.append(driver.find_element(By.XPATH, "//*[@name='description']").get_attribute("content"))
        except NoSuchElementException as e:
            meta_data.append("")
            print('description 발견 안됨', e)
        ic(meta_data)
        # text_content.append(meta_data[-1])  # ?????
        text_of_this_site = title_text[-1] + ' ' + text_content[-1] + ' ' + meta_data[-1]

        # print('text processing...')
        text_content_words = mcab.morphs(text_of_this_site)
        # ic.enable()
        # ic(one_content, text_content[-1])
        # ic.disable()
        similarity_score = 0
        quality_score = 0
        relevancy_score = sum([1 for word in keyword if word in text_content_words]) / len(keyword)
        if len(text_content_words) > 0:
            similarity_score = sum([1 for word in text_content_words if word in text_content_words]) / len(text_content_words)
        if len(text_content_words) > 0:
            quality_score = sum([1 for word in text_content_words if hgtk.checker.is_hangul(word)]) / len(text_content_words)

        relevancy_scores.append(relevancy_score)
        similarity_scores.append(similarity_score)
        quality_scores.append(quality_score)
        ic(relevancy_score, similarity_score, quality_score)
        i += 1
    # driver.close()
    return domains, competitor_urls, title_text, meta_data, text_content, relevancy_scores, similarity_scores, quality_scores


def main():
    # List of keywords
    keywords2 = ['호텔 이불','이불 구독 서비스', '정기 이불 교체', '호텔 이불 구독','호텔 이불 구독 서비스', '호텔이불 쇼핑몰'
                 '호텔 이불 렌탈 서비스', '편리한 이불 관리', '이불 세탁 서비스', '혼자 사는 사람을 위한 호텔 이불 구독',
                 '소형 주거 공간 거주자를 위한 호텔 이불 구독', '임시 거주자를 위한 호텔 이불 구독', '건강 및 위생을 위한 호텔 이불 구독',
                 '친환경적인 소비자를 위한 호텔 이불 구독', '계절에 따라 호텔 이불 구독', '합리적인 소비를 위한 호텔 이불 구독',
                 '손님이 오실 때 호텔 이불', '출산직후의 산모를 위한 호텔 이불', 'SUV 또는 캠핑카 소유자를 위한 호텔 이불 구독', '애완 동물 소유자를 위한 호텔 이불 구독',
                 '민감한 피부/여드름 환자를 위한 호텔 이불 구독', '에어비앤비 운영을 위한 호텔 이불 구독', '세컨하우스를 위한 호텔 이불 구독', '공유주거를 위한 호텔 이불 구독']

    keywords1 = ['호텔 침구', '침구 구독 서비스', '정기 침구 교체', '호텔 침구 클리닝 서비스','호텔침구 쇼핑몰'
                 '호텔 침구 렌탈 서비스', '편리한 침구 관리', '침구 세탁 서비스', '혼자 사는 사람을 위한 호텔 침구 구독',
                 '소형 주거 공간 거주자를 위한 호텔 침구 구독', '임시 거주자를 위한 호텔 침구 구독', '건강 및 위생을 위한 호텔 침구 구독',
                 '친환경적인 소비자를 위한 호텔 침구 구독', '계절에 따라 호텔 침구 구독', '합리적인 소비를 위한 호텔 침구 구독',
                 '손님이 오실 때 호텔 침구', '출산직후의 산모를 위한 호텔 침구', 'SUV 또는 캠핑카 소유자를 위한 호텔 침구 구독', '애완 동물 소유자를 위한 호텔 침구 구독',
                 '민감한 피부/여드름 환자를 위한 호텔 침구 구독', '에어비앤비 운영을 위한 호텔 침구 구독', '세컨하우스를 위한 호텔 침구 구독', '공유주거를 위한 호텔 침구 구독']
    keywords = keywords1 + keywords2
    domains, competitor_urls, title_text, meta_data, text_content, relevancy_scores, similarity_scores, quality_scores = [], [], [], [], [], [], [], []
    competitors = []
    if os.path.exists('competitors.csv'):
        # Load the existing data
        existing_competitors = pd.read_csv('competitors.csv')
    else:
        # If the file doesn't exist, create an empty DataFrame
        existing_competitors = pd.DataFrame(
            columns=['keyword', 'domain', 'url', 'title_text', 'meta_data', 'relevancy_score', 'similarity_score', 'quality_score', 'text_content'])
        existing_competitors.to_csv(
            "competitors.csv",
            header=True,
            columns=['keyword', 'domain', 'url', 'title_text', 'meta_data', 'relevancy_score', 'similarity_score', 'quality_score', 'text_content'])
    df = pd.DataFrame(columns=['keyword', 'domain', 'url', 'title_text', 'meta_data', 'text_content', 'relevancy_score', 'similarity_score', 'quality_score'])
    # 구글의 첫 페이지만 확인
    for j, keyword in enumerate(keywords):
        ic(keyword)
        domains, competitor_urls, title_text, meta_data, text_content, relevancy_scores, similarity_scores, quality_scores = crawl_website(
            keyword, existing_competitors)

        for i in range(len(competitor_urls)):
            competitor = {
                "keyword": keyword,
                "domain": domains[i],
                "url": competitor_urls[i],
                "title_text": title_text[i],
                "meta_data": meta_data[i],
                "text_content": text_content[i],
                "relevancy_score": relevancy_scores[i],
                "similarity_score": similarity_scores[i],
                "quality_score": quality_scores[i],
            }
            # competitors.append(competitor)
            df = df.append(competitor, ignore_index=True)
        df.to_csv(
            "competitors.csv",
            mode='a',
            header=False,
            columns=['keyword', 'domain', 'url', 'title_text', 'meta_data', 'relevancy_score', 'similarity_score', 'quality_score', 'text_content'])
    # df = pd.DataFrame(competitors)
    # df.to_csv("competitors.csv", columns=['domain', 'title_text', 'url', 'meta_data', 'relevancy_score', 'similarity_score', 'quality_score', 'text_content'])


if __name__ == "__main__":
    main()
