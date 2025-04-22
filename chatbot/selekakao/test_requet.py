from pydantic import BaseModel
from typing import Optional
import requests
import json
import datetime


class Ask(BaseModel):
    name: str
    ask_time: str
    ask_text: str
    answer_text: Optional[str] = ''
    answer_time: Optional[str] = ''

url = 'http://localhost:8888/ask/'
now = datetime.datetime.now()
ask = Ask(name='진상손님',ask_time=now.strftime('%m%d_%H%M%S'),ask_text= "배송기사 오늘 안오셨어요")

print('json',ask.json())
headers = {'Content-type': 'application/json', 'Accept': 'json/plain'}
response = requests.post(url, data=ask.json(), headers=headers)

print(response.status_code)
print(response.text)