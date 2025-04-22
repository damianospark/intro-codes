import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver

from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# import mychrome_driver as chromedriver
from webdriver_manager.chrome import ChromeDriverManager
import urllib3

# 참고 사이트 : https://goodthings4me.tistory.com/903


def get_random_time():
    return random.uniform(1, 3)


def read_proxies_from_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    proxies = [
        {"ip": line.split(":")[0].strip(), "port": line.split(":")[1].strip()}
        for line in lines
    ]
    return proxies


def get_proxies():
    proxies = read_proxies_from_file("./proxies.txt")
    proxy_list = []
    for proxy in proxies:
        if proxy is not None:
            # print("Found proxy: %s" % proxy)
            proxy_list.append(proxy)
    return proxy_list


def get_random_proxy():
    global proxies_list
    proxy = random.choice(proxies_list)
    time.sleep(get_random_time())
    return {"http": f"http://{proxy['ip']}:{proxy['port']}"}


def ext_apt_ho(aptnum, proxy):
    chrome_options = Options()
    # chrome_options.add_argument("--user-data-dir=" + self.profile_path)
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--remote-debugging-port=9222")
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')

    print("urllib3 version:", urllib3.__version__)

    # Use ChromeDriverManager to download and install ChromeDriver.
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    url = f'https://new.land.naver.com/complexes/{aptnum}'
    driver.get(url)
    # driver.implicitly_wait(5)
    # time.sleep(3)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'complexTitle')))

    # 아파트 버튼 옆 건물명칭
    bld_title = driver.find_element(By.ID, 'complexTitle').text.strip()

    # 좌측 단지정보 버튼 클릭
    driver.find_elements(By.CLASS_NAME, 'complex_link')[0].click()
    time.sleep(0.5)

    # 세대별 평형정보 추출하는 부분 ##
    dongs = driver.find_element(By.CLASS_NAME, 'detail_contents_inner').find_elements(By.CLASS_NAME, 'tab_item')
    for dong in dongs:
        # print(dong.text[:3])
        if dong.text.strip()[:3] == '동호수':
            dong.click()
            time.sleep(0.5)

    # 동 이름이 많은 경우 꺽쇠가 있음. 꺽쇠를 찾아 클릭하는 코드이며 class="btn_moretab_inner" 없는 경우를 대비하여 예외 처리함
    try:
        btn_moretab = driver.find_element(By.CSS_SELECTOR, '#detailContents4 > div.detail_sorting_tabs > div > div.btn_moretab_box > button > span > i')
        time.sleep(0.5)
        btn_moretab.click()
    except BaseException:
        pass
    time.sleep(0.5)

    # 동 이름 클릭
    dongs_a = driver.find_elements(By.CSS_SELECTOR, '#detailContents4 > div > div > div.detail_sorting_tablist > span > a')
    for dong in dongs_a:
        try:
            dong.click()  # 동 이름 클릭 시 하단 '아파트 세대' 변경시킴
        except BaseException:
            driver.execute_script('arguments[0].click();', dong)
        time.sleep(0.5)

        # 개발자도구에서 동이름 클릭하면 나오는 호수 부분의 class 속성인 detail_tabpanel_inner 클릭
        page_src = driver.find_element(By.CLASS_NAME, 'detail_tabpanel_inner')
        page_src.click()
        time.sleep(0.5)

        # page_src html 소스코드를 변수에 저장
        # 해당 소스코드 대상으로 bs4와 requests 사용하여 세대별 면적 추출함
        html_src = page_src.get_attribute('innerHTML')
        # print(html_src)

        soup = BeautifulSoup(html_src, 'html.parser')
        house_floors = soup.select('div.detail_box--housenumber div.table_inner div.house_floor')  # 층
        print(f'\n{bld_title} 아파트 {dong.text} (전체 층수: {len(house_floors)})')

        for floor in house_floors:  # 층별로 구분하고 있음.
            # 해당 동의 라인별 같은 층의 호(세대)를 span으로 분리하고 그 하위에 input과 div로 호와 면적을 구분하고 있음
            ho_spans = floor.find_all('span')
            for span in ho_spans:
                # 빈 span <span class="house_number is-blank"></span> 으로 인해 TypeError: 'NoneType' 발생 예외 처리
                try:
                    ho = span.find('input')['value']  # 호 추출
                    py = span.find('div', class_='tooltip_wrap').text.split(' ')[1].strip().replace('㎡', '')  # 공급 106.51㎡ 형태에서 ㎡ 제거
                    print(f'{ho}호 {py}')
                except BaseException:
                    continue
        # break
    driver.quit()


if __name__ == '__main__':
    proxies_list = get_proxies()
    proxy = get_random_proxy()

    # apt_no = 146482
    # apt_no = 45
    apt_no = 12076

    # ext_apt_ho(apt_no, proxy)
    ext_apt_ho(apt_no, None)
