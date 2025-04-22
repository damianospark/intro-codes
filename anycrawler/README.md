# 1. 초기 세팅

## 1. font 설치

2024/01/08 현재 '/' 경로가  /usr/share/nginx/html 로 되어 있어서  이 아래 /static/media 에 tms에서 사용하는 폰트를 다움 받아둠.

```bash
sudo wget https://tms.teamfresh.co.kr/static/media/Nunito-Bold.a2299071.woff
sudo wget https://tms.teamfresh.co.kr/static/media/Nunito-SemiBold.03392c01.woff
sudo wget https://tms.teamfresh.co.kr/static/media/Nunito-Regular.328e9506.woff
sudo wget https://tms.teamfresh.co.kr/static/media/materialdesignicons-webfont.d48b5ff6.woff2
sudo wget https://tms.teamfresh.co.kr/static/media/materialdesignicons-webfont.66e3254e.woff
sudo wget https://tms.teamfresh.co.kr/static/media/unicons.b5ae9656.woff2
sudo wget https://tms.teamfresh.co.kr/static/media/unicons.31bc3765.woff
```

## 2. cron 등록 및 동작 로직 요약

- 매일 아침 8시에 동작
- 배송은 1일 전 보고서 수집-
- 수거는 2일 전 보고서 수집
- 배포 위치 : /var/www/better/tms

## 3. html rendoring error

- 중요하지 않은 파일은 따로 수집안함
- 이로 인해 페이지 로딩시 오류가 다수 발생해 /usr/share/nginx/html/static/js 아래에 더미 js 파일들 생성해둠.

```bash
sudo touch main.d0ab3ca4.chunk.js
sudo touch 6.a498a252.chunk.js
sudo touch 10.bdb404d1.chunk.js
sudo touch 2.965aca18.chunk.js
sudo touch 1.76a59755.chunk.js
sudo touch 0.ce3e1691.chunk.js
```

## 4. crontab 에서 오동작시 다음 코드 보완

chrome driver 자동 설치로인한 권한 및 누락된 리소스 등으로 인한 오류 발생시 아래 로직 적용 검토 필요

```python
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
import subprocess

def get_chrome_version():
    # Chrome 버전을 가져오는 함수
    try:
        # Linux 및 MacOS의 경우
        output = subprocess.run(['google-chrome', '--version'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        version = output.split(' ')[2].split('.')[0]
    except:
        # Windows의 경우 (경로에 따라 수정 가능)
        output = subprocess.run(['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        version = output.split(' ')[-1].split('.')[0]
    return version

def check_driver_exists(version):
    # ChromeDriver가 이미 설치되어 있는지 확인하는 함수
    driver_path = f"/home/max/.wdm/drivers/chromedriver/{os.name}{os.sep}{version}/"
    if os.path.exists(driver_path):
        return driver_path
    return None

# 메인 로직
profile_path = "/home/max/.config/google-chrome/Default"
chrome_options = Options()
chrome_options.add_argument("--user-data-dir=" + profile_path)
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

chrome_version = get_chrome_version()
driver_path = check_driver_exists(chrome_version)

if driver_path:
    driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
else:
    chrome_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
```

# 2. 주요 기능의 명령 설명 방법

```bash
# anycrawler/run_daily.sh
python tms_result_crawler.py YYYY-mm-dd 배송
python tms_result_crawler.py YYYY-mm-dd 수거
python tms_result_crawler.py YYYY-mm-dd 모두

python tms_result_crawler.py YYYY-mm-dd 수거 리스트
```

- 수집하기위한 날짜는 반드시 주어야 하며 수집할 보고서 종류(배송/수거/모두)중 하나를 지정 해야함.

- cron이 제대로 돌지 않았을 때 별도로 돌리는 용도로 사용해야함
- html수집은 아니고 요약 테이블을 수집해야할 경우 "리스트" 라는 인자를 마지막에 주면 html 수집은 수행하지 않고 마침.

# 3. cron 을 통한 실행 및 cross check

## 1. cron 등록을 위한 스크립트

- run_daily.sh 에 기록돼 있음

- 매일 실행해야할 명령행 이 명시돼 있음
- 실행후 웹서비스 중인 위치로 deploy 진행

```bash
# 배송의 경우 접수일 기준이므로 어제 날짜 계산
yesterday=$(date -d "-1 day" +%Y-%m-%d)
python tms_result_crawler.py "$yesterday" 배송
python tms_result_crawler.py "$yesterday" 수거

/home/max/cleanbeding/anycrawler/deploy.sh missing
```

## 2. cross check

```bash
# 수치로만 점검
python crawl-cross-check.py YYYY-mm-dd

# 로그인/배송리포트/수거리포트 화면의 변화점검
python needle/cawl-screen-check.py
# 또는
needle/run_tms_screen_checker.sh
```

- 위 예제 코드에서 deploy.sh 실행시 파일 복제 이후 다음의 명령어가 실행됨 `python crawl-cross-check.py $yesterday`

- 각 날짜별 취합이 제대로 됐는 지 요약 테이블의 수치와 html의 수치가 맞는 지를 점검해줌.
- TMS측에서 화면에 변화를 줄 경우 크롤링에 문제 발생할 수 있어 화면의 변화도 감지할 수 있도록 스크립트 준비해둠.
  - 매일 실행해서 평상시의 화면 차이가 어느 정도인지 기록해야함.
  - 30일 치 변화 기록이 되고 나면 이후부터는 상황에 따라 한 두 번씩 실행

- 수치 점검 및 화면 비교 결과는 해당 스크립트 실행직후 #webhook-monitoring-alert 채널에 리포트 됨

## 3. 슬랙 noti 대상

- daily 리포팅
  - run_daily.sh 실행 시 결과 리포팅
  - deploy.sh 실행시  crawl-cross-check.py 의 수치 비교 결과 리포팅

- 필요시 리포팅
  - needle/run_tms_screen_checker.sh 실행시마다 (첫 30일은 매일)
  - 수집 오류로 tms_result_crawler.py 추가 실행시 마다
