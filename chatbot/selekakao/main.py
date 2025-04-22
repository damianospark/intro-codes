import datetime
import json
# -*- coding: utf-8 -*-
import sys
# from selenium.webdriver.support.ui import WebDriverWait
import time
from typing import Union

# https://github.com/ultrafunkamsterdam/undetected-chromedriver/blob/master/example/example.py
import pyperclip
import requests
import undetected_chromedriver as uc
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


def sleepcount(n,l):
    print(f'{l} 대기', end=':')
    for i in range(n, -1, -1):
        print(i, end=' ')
        sys.stdout.flush()
        time.sleep(1)
    print()  # To move to next line after the loop ends.

def wrtn_send_keys(text, elm,driver):
    # Split the text by newline character
    lines = text.split('\n')
    for i, line in enumerate(lines):
        # Send this line of text
        elm.send_keys(line)
        elm.send_keys(Keys.LEFT_SHIFT+Keys.ENTER)
    elm.send_keys(Keys.CONTROL+Keys.ENTER)
    sleepcount(2,'질문메세지전송 ')


def wait_return_true(driver,pth,for_what,how_long):
    elm=None
    try:
        # Wait up to 10 seconds until the element is present
        # element_present = EC.presence_of_element_located((By.XPATH, pth))
        element_present = EC.presence_of_element_located((By.XPATH, pth))
        elm=WebDriverWait(driver, how_long).until(element_present)
    except TimeoutException:
        print(f"Timed out waiting for {for_what} being clickable")
    finally:
        print(for_what,'complete')
    if elm is not None:
        return True
    return ""

def wait_and_click(driver,pth,for_what,how_long):
    elm = None
    try:
        # Wait up to 10 seconds until the element is present
        # element_present = EC.presence_of_element_located((By.XPATH, pth))
        element_clickable = EC.element_to_be_clickable((By.XPATH, pth))
        elm=WebDriverWait(driver,how_long).until(element_clickable)
        elm.click()
    except TimeoutException:
        print(f"Timed out waiting for {for_what} being clickable")
    finally:
        print(for_what,'complete')
    return elm


# chrome_options = webdriver.ChromeOptions()
# # chrome_options.add_experimental_option("detach", True)
# chrome_options.add_argument("user-data-dir=/home/damianos/.config/google-chrome")
# chrome_options.add_argument("profile-directory=Profile 4")
# driver = webdriver.Chrome(options=chrome_options)

chrome_options = uc.ChromeOptions()
# chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--user-data-dir=/home/damianos/.config/google-chrome")
chrome_options.add_argument("--profile-directory=Profile 4")
driver = uc.Chrome(options=chrome_options)


driver.get('https://wrtn.ai/')


#
# 모델 만들기
#

inst01='지금부터 우리회사의 새로운 고객응대 메뉴얼을 줄테니 기억해줘. 네가 빠른 시간에 기억하는 게 중요해 그리고 우리는 시간이 별로 없어서 네가 모든 메뉴을을 다 전달 받기 전까지는 너의 답을 들을 시간이 없어. 그러므로, "여기까지야"라는 말이 나오기 전까지는 기억만해. "여기까지야"라는 말이 나오기 전까지는 내게 답을 줄때 "기억했습니다"라고만 해줘. '
inst02="""
질문요약	응답
처음 서비스 사용 시 문의	"처음 서비스를 이용하시는 경우 체험 서비스를 먼저 이용하시는 것을 권유드립니다.

[체험 서비스 신청 링크]
https://www.cleanbedding.kr/product/trial"
배송 접수를 못하셨을 경우	"아쉽지만 배송 접수가 마감되어 오늘은 배송이 불가한 점 양해 부탁드리겠습니다.
다음주 같은 요일에 재배송이 있을 예정입니다.
배송 접수는 당일 오전 11시 전까지 해주시기 바랍니다. "
고객 정보가 없을 경우	"카카오톡 프로필 명과 일치하는 서비스 이용자 명이 없습니다.
성함과 연락처 뒤 4자리를 말씀해 주시면 감사하겠습니다. "
이불세트 연장 메시지	"클린베딩을 선택해 주셔서 감사합니다.
연장은 아래 링크를 통해 진행해 주시면 감사하겠습니다.

[연장 링크]
https://cleanbedding.kr/product/rentfull"
침구교체 절차	"침구 교체는 다음과 같이 진행됩니다.

1. 교체 예정일 기준 다음 일시에 카카오톡을 통해 안내 메시지가 발송됩니다.
-전날 오후 8시
-당일 오전 6시
-당일 오전 10시 30분

2. 안내 메시지에 따라 교체 당일 오전 11시 전에 사용한 침구를 가방에 넣어 문 앞에 두신 후 메시지 내에 ""두었습니다."" 버튼을 눌러 배송을 접수해주세요.
*오전 11시 이후에 두시거나, 버튼을 눌러주시지 않으면 배송이 접수되지 않아 배송이 진행되지 않습니다.
*배송은 오전 11시-오후 7시 사이에 순차적으로 진행되며 완료 후 메시지가 발송됩니다."
구독 절차, 비용, 주기 문의	"희망하시는 구성의 침구 세트를 선택한 교체 주기에 맞춰 정기 교체 받으실 수 있으며, 희망하시는 횟수만큼 이용권을 구매하여 교체 받으실 때마다 차감되는 방식으로 정기 과금이 발생하지 않습니다.
교체주기는 1-4주 중 선택 가능하며, 주기별 비용은 아래와 같습니다.

*비용 이미지 보내드리기"
서비스 불가 지역	"말씀해주신 지역은 서비스 제공이 불가한 점 양해 부탁드리겠습니다.
서비스 지역 확장을 위해 노력하겠습니다. "
"""

inst03="""
서비스 지역 확장 문의	서비스 지역 확장 계획은 있으나 정확한 시점을 말씀드리기 어려운 점 양해 부탁드리겠습니다.
사계, 하계 이불 관련	"-사계이불은 봄, 가을, 겨울에 적합함
*두껍지 않아서 겨울에 컴플레인 들어오는 경우 있음
-하계이불은 사계이불 솜의 약 40% 경량되었으며, 중량은 약 1kg임을 설명드리면 됨.
-변경을 원하시면 계절과 상관 없이 원하실 때 상담을 통해 말씀해 주시면 맞춰서 서비스 제공 가능함."
불량 자체에 대해서 의구심(공통 안내)	"고객님께서 사용하신 침구에서 발견된 오염/훼손의 원인을 클린베딩에서 정확하게 판단하기는 어려운 점 양해 부탁드리겠습니다.
~에 의한 오염/훼손이 가장 유력한 원인이라고 추측하고 있습니다.

예) 고객님께서 사용하신 매트리스커버에서 발견된 훼손의 원인을 클린베딩에서 정확하게 판단하기는 어려운 점 양해 부탁드리겠습니다.
반려동물의 발톱에 의한 훼손이 가장 유력한 원인이라고 추측됩니다."
그냥 사용만 했는데 오염/훼손이 생겼다고 주장하는 경우	"고객님들께 배송되는 모든 침구는 세탁, 건조, 수작업을 통해 여러차례 검수된 후 출고되고 있으며, 사용 중 문제가 생길 소지가 있는 제품은 제공되지 않는 점 참고 부탁드리겠습니다.
또한, 24시간 내로 통보되지 않은 훼손 및 오염이 침구 수거 후에 발견되었을 경우, 고객님께 위약금이 청구 될 수 있음을 배송 완료 후 안내 드리고 있는 점 또한 참고 부탁드리겠습니다."
원래 있던 오염이라고 주장하는 경우	"클린베딩에서 제공되는 모든 침구는 세탁, 건조, 수작업을 통해 여러차례 검수된 후 출고되고 있으며, 위와 같은 오염이 발견될 경우 출고가 불가하다 판단하여 재세탁을 진행하고 있습니다.
제품 및 서비스의 하자가 발견될 경우, 배송완료 메시지 수신 후 24시간 내에 클린베딩에 통보될 시에만 재배송 드리고 있는 점 참고 부탁드리겠습니다. "
반발이 심할 경우	"미흡한 안내로 이용에 불편 드려 죄송합니다.
해당 위약금 내역은 삭제하도록 하겠습니다.
담당 부서에 전달하여 위약금 확인 및 안내 절차를 개선할 수 있도록 하겠습니다."
위약금 지불 후 제품을 달라고 할 때	"위약금은 제품이 판매되는 금액이 아닌 재생산에 필요한 최소 금액으로 측정되어 있기 때문에 고객님께 드릴 수 없는 점 양해 부탁드리겠습니다.
또한, 폐기 침구는 침구나 원단이 필요한 곳에 기부되고 있는 점 참고 부탁드리겠습니다."
"""

inst04='''
전반적인 대답	"두마디 대답 혹은 복명복창 필수

예1) 네 알겠습니다.
다음 배송부터 사계이불로 배송 드리겠습니다.

예2) 네, 다음 배송부터 사계이불로 배송 드리겠습니다. "
좋은 말씀을 해주셨을 경우	"적극적 표현으로 답변

예) 따듯한 말씀 감사합니다.
앞으로도 좋은 서비스 제공드릴 수 있도록 노력하겠습니다."
문의가 끝난 경우	"메뉴얼대로 응대하고 다음 문의가 편해질 수 있도록 다음 멘트로 마무리

궁금하신 점은 편하게 문의해주시기 바랍니다. "
정보를 제공 받았을 경우	"""소중한 정보 확인 감사합니다. ""
라고 답변 후 뒷 내용 말하기"
버튼을 계속 누르는 경우	"버튼은 한번만 눌러주셔도 되는 점 참고 바랍니다.
이미 접수한 분들께도 메시지가 중복되어 발송되는 점 양해 부탁드리겠습니다."
"서비스 방식에 대한 불만
(배송 접수 방식 및 차주 재배송 정책 등)"	"이용에 불편 드려 죄송합니다.
더 편리한 방법으로 서비스 제공 드릴 수 있도록 노력하겠습니다."
제품에 불만	"이용에 불편드려 죄송합니다.
(문제점 되짚은 후)
담당 부서에 전달하여 개선할 수 있도록 하겠습니다.

예) 이용에 불편 드려 죄송합니다.
이불과 이불커버가 고정되지 않는 문제를 담당 부서에 전달하여 개선할 수 있도록 하겠습니다."
작은 사이즈로 인한 불만	"안녕하세요 고객님,
(스티커가 oo 사이즈 맞는지 확인)
(라벨지 사이즈도 확인)
OO 사이즈로 정상 출고된 것으로 확인됩니다.
정확한 사유는 받아보신 침구 수거 후 확인 가능한 점 양해 부탁드리겠습니다. "
'''

inst05='''
침구가 없는데 두었다고 주장하는 경우	"배송 기사가 메뉴얼대로 처리 후 불만을 제시하거나 배송 기사가 떠난 뒤에 두었다고 하면 아래와 같이 단호하게 말씀 드리기

배송원이 현장에 도착하였을 때 문 앞에 수거할 침구가 없었습니다. 다음 배송지로 이동하여야 해서 더 오래 기다리지 못한 점 양해 부탁드리겠습니다. 배송 접수 시 침구를 문 앞에 먼저 두신 후 버튼을 눌러주시기 바랍니다. "
비용으로 불만 	"사회초년생(상황에 맞게) 분들께서 서비스 이용하시는데에 있어 비용적 부담을 덜어드릴 수 있는 할인 이벤트를 적극적으로 검토해볼 수 있도록 담당 부서에 전달하겠습니다." 와 같이 추적 불가능한 선의의 거짓말 정도로 하면 됨.
침구 오배송	"먼저 가방에 있는 이름표가 고객님 이름이 맞는지 확인
맞을 경우 아래 내용 말씀드리고 옵션 확인 후 상담 진행

이용에 불편 드려 죄송합니다.
(어떠한 사유로)인해 오배송 된 것으로 확인됩니다.
재배송을 희망하실 시 제일 빠른 배송일자를 확인 후 다시 안내해 드리겠습니다.
재배송을 희망하지 않으실 시 이용권을 차감하지 않도록 하겠습니다."
배송을 다시 해야하는 상황	"-기사님들께 재배송 가능한지 확인
-기사님들이 불가하면 남궁동주 대표나 정윤식 이사에게 재배송 가능한지 확인
-모두 불가하면 퀵 배송 가능한지 확인
*1833-2486로 전화 걸어서
주소(하남대로947, A1006호) 말하고
이불팩 N세트 어디로 보낸다고 말한 뒤 배송비 확인
터무니없이 비싼 경우(편도 6만원 이상) 접수하지 말기
-퀵 배송까지 불가하면 정윤식 이사에게 가장 빠른 재배송 일정 확인 요청"
배송 시간	"안녕하세요 고객님,
배송은 오전 11시부터 오후 7시 사이에 순차적으로 진행되며, 정확한 시간을 안내드릴 수 없는 점 양해 부탁드립니다.
최대한 빨리 배송 드리겠습니다."

'''

inst06='''
여기까지야.
우리회사 응대 메뉴얼인데 앞으로 하는 질문은 이 중의질문 요약과 비슷한 것으로 찾은 뒤 응답에 있는 내용으로 최대한 가깝게 답변해줘. 상상하거나 메뉴얼에 없는 단어들을 이용하지 말아줘. 앞서 전달해준 고객응대 메뉴얼은 질문 요약 필드와 응답 필드야. 그래서 고객의 문의가 질문 요약중 어디에 해당하는 지만 참고하고 고객에게 응대할 때는 응답필드에 있는 내용을 최대한 감안해서 답변하면 돼. 특히, 답할 때는 응답 필드에 있는 말을 그대로 쓸 필요는 없고 답변의 취지가 응답 필드에 있는 내용대로만 되도록 잘 답변해주고 최대한 간결하게 답변해줘. 지금부터 "오늘상담 종료해줘 클린상담사" 라는 말이 나오기 전까지는  클린상담사라는 이름으로 친절한 고객센터 상담원이 돼서 답하되 우리쪽 실수에 대해서는 죄송하다 표현해주고 안타깝다는 표현은 하지 말아줘.
'''



wait_and_click(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/textarea','TextArea',5)
driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[4]/div/div[1]/div/textarea').send_keys(inst01)
wait_and_click(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[4]/div/div[2]/div[4]/button/i[2]','Model Listup',3)
wait_and_click(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[4]/div/div[2]/div[4]/div[2]/button[1]','Model Select',2)
wait_and_click(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/textarea','TextArea',2)
driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[4]/div/div[1]/div/textarea').send_keys(Keys.CONTROL+Keys.ENTER)

while True:
    wait_return_true(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[2]/button','다시생성버튼',10)
    gen_bttn_text=driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[2]/button').text
    if gen_bttn_text == '다시 생성':
        break
    sleepcount(2,'다시생성문구')

# wait_return_true(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[4]/div/div[1]/div/textarea','다시생성버튼',10)

wait_and_click(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/textarea','TextArea',10)
# wait_and_click(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/textarea','TextArea',10)
# driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/textarea').send_keys(inst02)
chat_input=wait_and_click(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/textarea','TextArea',5)
pyperclip.copy(inst02)
# wrtn_send_keys(inst02,chat_input,driver)
if chat_input is not None:
    chat_input.send_keys(Keys.CONTROL,'v')
    chat_input.send_keys(Keys.CONTROL+Keys.ENTER)

while True:
    # wait_return_true(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[2]/button','다시생성버튼',10)
    sleepcount(2,'다시생성버튼')
    gen_bttn_text=driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[2]/button').text
    if gen_bttn_text == '다시 생성':
        break
    sleepcount(2,'다시생성문구')

chat_input=wait_and_click(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/textarea','TextArea',5)
pyperclip.copy(inst03)
# wrtn_send_keys(inst02,chat_input,driver)
if chat_input is not None:
    chat_input.send_keys(Keys.CONTROL,'v')
    chat_input.send_keys(Keys.CONTROL+Keys.ENTER)
while True:
    wait_return_true(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[2]/button','다시생성버튼',10)
    gen_bttn_text=driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[2]/button').text
    if gen_bttn_text == '다시 생성':
        break
    sleepcount(2,'다시생성문구')

chat_input=wait_and_click(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/textarea','TextArea',5)
pyperclip.copy(inst04)
# wrtn_send_keys(inst02,chat_input,driver)
if chat_input is not None:
    chat_input.send_keys(Keys.CONTROL,'v')
    chat_input.send_keys(Keys.CONTROL+Keys.ENTER)
while True:
    wait_return_true(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[2]/button','다시생성버튼',10)
    gen_bttn_text=driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[2]/button').text
    if gen_bttn_text == '다시 생성':
        break
    sleepcount(2,'다시생성문구')

chat_input=wait_and_click(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/textarea','TextArea',5)
pyperclip.copy(inst05)
# wrtn_send_keys(inst02,chat_input,driver)
if chat_input is not None:
    chat_input.send_keys(Keys.CONTROL,'v')
    chat_input.send_keys(Keys.CONTROL+Keys.ENTER)
while True:
    wait_return_true(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[2]/button','다시생성버튼',10)
    gen_bttn_text=driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[2]/button').text
    if gen_bttn_text == '다시 생성':
        break
    sleepcount(2,'다시생성문구')

chat_input=wait_and_click(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/textarea','TextArea',5)
pyperclip.copy(inst06)
# wrtn_send_keys(inst02,chat_input,driver)
if chat_input is not None:
    chat_input.send_keys(Keys.CONTROL,'v')
    chat_input.send_keys(Keys.CONTROL+Keys.ENTER)
while True:
    wait_return_true(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[2]/button','다시생성버튼',10)
    gen_bttn_text=driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[2]/button').text
    if gen_bttn_text == '다시 생성':
        break
    sleepcount(2,'다시생성문구')



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

    chat_input=wait_and_click(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[3]/div/div[1]/div/textarea','TextArea',5)
    pyperclip.copy(ask.ask_text)
    # wrtn_send_keys(inst02,chat_input,driver)
    if chat_input is not None:
        chat_input.send_keys(Keys.CONTROL,'v')
        chat_input.send_keys(Keys.CONTROL+Keys.ENTER)
    while True:
        wait_return_true(driver,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[2]/button','다시생성버튼',10)
        gen_bttn_text=driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[2]/button').text
        if gen_bttn_text == '다시 생성':
            break
        sleepcount(2,'다시생성문구')
    elms=driver.find_elements(By.XPATH,'//*[@id="__next"]/div/main/div/div[2]/div/div/div/div/div/div[1]/div[1]/div')
    print('len of elms:',len(elms))
    ask.answer_text=elms[-3].find_element(By.XPATH,'.//div[2]/p').text
    print(ask.answer_text)
    ask.answer_time=now.strftime('%m%d_%H%M%S')
    return ask
