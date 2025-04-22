#!/home/damianos/miniconda3/bin/python
# -*- coding: utf-8 -*-

import traceback  # traceback 모듈 임포트
from markdownify import markdownify as md
import re
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import csv
import os
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# pip install webdriver-manager

# 이미지 링크를 추출하고 저장하는 함수


def download_html_image(image_url, img_root):
    image_path = ""
    if image_url:
        response = requests.get(image_url)
        if response.status_code == 200:
            image_folder = img_root
            os.makedirs(image_folder, exist_ok=True)
            image_name = "-".join(image_url.split("/")[-2:])  # URL에서 파일명 생성
            image_path = os.path.join(image_folder, image_name)

            with open(image_path, "wb") as f:
                f.write(response.content)
    return image_path


def download_images_from_markdown(markdown_content, img_root):
    image_links = re.findall(r"!\[.*?\]\((.*?)\)", markdown_content)
    saved_images = {}

    for image_link in image_links:
        # 이미지 URL에서 파일명 추출
        image_url_parts = image_link.split("/")
        image_name = "-".join(image_url_parts[2:])  # 도메인을 제외한 나머지 URL을 연결하여 파일명 생성

        # 이미지 다운로드 및 저장
        response = requests.get(image_link)
        if response.status_code == 200:
            image_folder = img_root
            os.makedirs(image_folder, exist_ok=True)
            image_path = os.path.join(image_folder, image_name)

            with open(image_path, "wb") as f:
                f.write(response.content)

            saved_images[image_link] = image_path

    return saved_images


def html_to_markdown(html_content, img_root):
    markdown_content = md(html_content)
    # 이미지 다운로드 및 링크 교체 로직
    downloaded_images = download_images_from_markdown(markdown_content, img_root)
    for original_link, saved_path in downloaded_images.items():
        refer_path = saved_path[5:]
        print('saved_path:', saved_path)
        print('refer_path:', refer_path)
        markdown_content = markdown_content.replace(original_link, refer_path)
    return markdown_content


def save_markdown_content(extracted_data):
    title = extracted_data.get("title", "Untitled").replace(" ", "-")
    filename = "./md/" + title + ".md"
    markdown_content = f"# {extracted_data.get('title', 'Title not found')}\n\n"
    if extracted_data.get("banner_image"):
        markdown_content += f"![Banner Image]({extracted_data['banner_image'][5:]})\n\n"
    # Keywords 섹션을 가로로 나열하고 백틱으로 각 키워드 강조
    if extracted_data.get("keywords"):
        keywords_formatted = " ".join(
            f"`{keyword}`" for keyword in extracted_data["keywords"]
        )
        markdown_content += f"## Keywords\n\n{keywords_formatted}\n\n"
    markdown_content += "---\n\n"  # 구분선 추가
    markdown_content += extracted_data.get("md_content", "")
    os.makedirs("md", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(markdown_content)
    print(f"Markdown content saved to '{filename}'")


class DataCrawler:
    def __init__(
        self,
        profile_path,
        list_page_url,
        link_to_detail_page_xpath,
        detail_page_structure,
        data_fields,
        list_page_wait_xpath,
        list_page_wait_sec,
        detail_page_wait_xpath,
        detail_page_wait_sec,
        img_root,
        file_to_save

    ):
        self.profile_path = profile_path
        self.list_page_url = list_page_url
        self.link_to_detail_page_xpath = link_to_detail_page_xpath
        self.detail_page_structure = detail_page_structure
        self.data_fields = data_fields
        self.list_page_wait_xpath = list_page_wait_xpath
        self.detail_page_wait_xpath = detail_page_wait_xpath
        self.list_page_wait_sec = list_page_wait_sec
        self.detail_page_wait_sec = detail_page_wait_sec
        self.data_list = []
        self.img_root = img_root
        self.file_name = file_to_save

        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=" + self.profile_path)
        chrome_service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    def navigate_to_page(self, url, wait_xpath, sec_to_wait=10):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, sec_to_wait).until(
                EC.presence_of_element_located((By.XPATH, wait_xpath))
            )
            time.sleep(sec_to_wait)
        except Exception as e:
            print(f"Error navigating to {url}: {e}")

    def collect_data_from_detail_page(self, detail_page_url):
        self.navigate_to_page(detail_page_url, self.detail_page_wait_xpath, 5)
        data = {}
        for key, value in self.detail_page_structure.items():
            data[key] = self.collect_data_from_element(key, value)
        self.data_list.append(data)
        save_markdown_content(data)

    def collect_data_from_element(self, key, value):
        try:
            elements = self.driver.find_elements(By.XPATH, value["selector"])
            if not elements and "selector_bak" in value:
                elements = self.driver.find_elements(By.XPATH, value["selector_bak"])

            if value["attribute"] == "text":
                return elements[0].text if elements else ""
            elif value["attribute"] == "img_src":
                img_url = elements[0].get_attribute("src") if elements else ""
                return download_html_image(img_url, self.img_root)
            elif value["attribute"] == "markdown":
                html_content = elements[0].get_attribute("innerHTML") if elements else ""
                return html_to_markdown(html_content, self.img_root)
            elif value["attribute"] == "html":
                return elements[0].get_attribute("innerHTML") if elements else ""
            elif value["attribute"] == "text_list":
                return [element.text for element in elements] if elements else []
        except Exception as e:
            print(f"Error collecting data from element {key}: {e}")
            traceback.print_exc()  # 스택 트레이스 출력
            return ''  # 오류 발생시 빈 문자열 반환

    def scroll_to_bottom(self):
        """페이지 끝까지 스크롤하는 함수"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(3)  # 페이지 로드를 기다리는 시간
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def process_link_new_window(self, main_window):
        # 새 창에서 열린 링크 처리 로직
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.collect_data_from_detail_page(self.driver.current_url)
        self.driver.close()
        self.driver.switch_to.window(main_window)

    def process_link_same_window(self):
        # 같은 창에서 열린 링크 처리 로직
        self.collect_data_from_detail_page(self.driver.current_url)
        self.driver.back()  # 이전 페이지(리스트 페이지)로 돌아감

    def process_link(self, link):
        main_window = self.driver.current_window_handle
        # 링크를 클릭하여 처리
        link.click()
        time.sleep(3)  # 페이지 로딩 대기
        # 새 창이 열렸는지 확인
        if len(self.driver.window_handles) > 1:
            # 새 창에서 링크 처리
            self.process_link_new_window(main_window)
        else:
            # 같은 창에서 링크 처리
            self.process_link_same_window()

    def collect_data_from_list_page(self):
        self.navigate_to_page(self.list_page_url, self.list_page_wait_xpath, self.list_page_wait_sec)
        self.scroll_to_bottom()
        last_processed = self.load_last_processed()
        while True:
            links = self.driver.find_elements(By.XPATH, self.link_to_detail_page_xpath)
            if last_processed >= len(links):
                break  # 모든 링크를 처리했으면 반복 중지
            link = links[last_processed]
            href = link.get_attribute("href")  # 링크의 href 속성 저장
            try:
                self.process_link(link)
            except Exception as e:
                print(f"Error processing link {href}: {e}")
            finally:
                self.save_temporary_data()
                self.save_last_processed(last_processed)
                last_processed += 1
                # 원래 페이지로 돌아와서 다음 링크를 찾음
                self.navigate_to_page(self.list_page_url, self.list_page_wait_xpath, self.list_page_wait_sec)
                self.scroll_to_bottom()

    def save_data(self):
        with open(self.file_name, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # 헤더 작성 예시
            writer.writerow(
                ["title", "date", "keywords", "banner_image", "content", "md_content"]
            )
            for row in self.data_list:
                writer.writerow(
                    [
                        row["title"],
                        row["date"],
                        row["keywords"],
                        row["banner_image"],
                        row["content"],
                        row["md_content"],
                    ]
                )

    def save_temporary_data(self):
        with open("temporary_data.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                ["title", "date", "keywords", "banner_image", "content", "md_content"]
            )
            for row in self.data_list:
                writer.writerow(
                    [
                        row["title"],
                        row["date"],
                        row["keywords"],
                        row["banner_image"],
                        row["content"],
                        row["md_content"],
                    ]
                )

    def save_last_processed(self, index):
        with open("last_processed.txt", "w") as file:
            file.write(str(index))

    def load_last_processed(self):
        if os.path.exists("last_processed.txt"):
            with open("last_processed.txt", "r") as file:
                return int(file.read())
        return -1


list_page_url = "https://velog.io/@damianos/posts"
data_fields = ["title", "date", "keywords", "banner_image", "content", "md_content"]
# header_xpath =
list_page_wait_xpath = '//*[@id="html"]/body/div/div[1]/div[2]/main/div[1]/div[1]/div/div/div[1]/a'
list_page_wait_sec = 2
detail_page_wait_xpath = '//*[@id="root"]/div[2]/div[3]/div/div[1]/div[1]/span[1]/a'
detail_page_wait_sec = 1
profile_path = "~/.config/google-chrome/Profile 4"
link_to_detail_page_xpath = '//*[@id="html"]/body/div/div[1]/div[2]/main/section/div[2]/div[2]/div/a[@class="VLink_block__Uwj4P"]'
detail_page_structure = {
    "title": {"selector": '//*[@id="root"]/div[2]/div[3]/div/h1', "attribute": "text"},
    "date": {
        "selector": '//*[@id="root"]/div[2]/div[3]/div/div[1]/div[1]/span[3]',
        "attribute": "text",
    },
    "keywords": {
        "selector": '//*[@id="root"]/div[2]/div[3]/div/div[2]/a',
        "attribute": "text_list",  # 여러 요소의 텍스트를 리스트로 수집
    },
    "banner_image": {
        "selector": '//*[@id="root"]/div[2]/div[3]/img',
        "attribute": "img_src",  # 이미지의 src 속성
    },
    "content": {
        "selector": '//*[@id="root"]/div[2]/div[4]/div/div',
        "selector_bak": '//*[@id="root"]/div[2]/div[5]/div/div',
        "attribute": "html",  # HTML 컨텐츠를 그대로 수집
    },
    "md_content": {
        "selector": '//*[@id="root"]/div[2]/div[4]/div/div',
        "selector_bak": '//*[@id="root"]/div[2]/div[5]/div/div',
        "attribute": "markdown",  # HTML 컨텐츠를 그대로 수집
    },
}
imgroot = "./md/img"
file_to_save = 'velog_data.csv'
# 사용 예시
crawler = DataCrawler(
    profile_path,
    list_page_url,
    link_to_detail_page_xpath,
    detail_page_structure,
    data_fields,
    list_page_wait_xpath,
    list_page_wait_sec,
    detail_page_wait_xpath,
    detail_page_wait_sec,
    imgroot,
    file_to_save
)
crawler.collect_data_from_list_page()
crawler.save_data()
