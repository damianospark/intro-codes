# -*- coding: utf-8 -*-

import random
import requests
from qrytool import load_data_into_dataframe, insert_dataframe_into_table
import json
import time
import pandas as pd
from icecream import ic
import re


def get_random_time():
    return random.uniform(1, 3)


def camel_to_snake(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def get_sido_info():
    down_url = "https://new.land.naver.com/api/regions/list?cortarNo=0000000000"
    r = requests.get(
        down_url,
        data={"sameAddressGroup": "false"},
        headers={
            "Accept-Encoding": "gzip",
            "Host": "new.land.naver.com",
            "Referer": "https://new.land.naver.com/complexes/102378?ms=37.5018495,127.0438028,16&a=APT&b=A1&e=RETAIL",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        },
    )
    r.encoding = "utf-8-sig"
    temp = json.loads(r.text)
    # temp = list(pd.DataFrame(temp["regionList"])["cortarNo"])
    df = pd.DataFrame(temp["regionList"])
    return df


def get_gungu_info(sido_code):
    down_url = "https://new.land.naver.com/api/regions/list?cortarNo=" + sido_code
    r = requests.get(
        down_url,
        data={"sameAddressGroup": "false"},
        headers={
            "Accept-Encoding": "gzip",
            "Host": "new.land.naver.com",
            "Referer": "https://new.land.naver.com/complexes/102378?ms=37.5018495,127.0438028,16&a=APT&b=A1&e=RETAIL",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        },
    )
    r.encoding = "utf-8-sig"
    temp = json.loads(r.text)
    # temp = list(pd.DataFrame(temp["regionList"])["cortarNo"])
    df = pd.DataFrame(temp["regionList"])
    return df


def get_dong_info(gungu_code):
    down_url = "https://new.land.naver.com/api/regions/list?cortarNo=" + gungu_code
    r = requests.get(
        down_url,
        data={"sameAddressGroup": "false"},
        headers={
            "Accept-Encoding": "gzip",
            "Host": "new.land.naver.com",
            "Referer": "https://new.land.naver.com/complexes/102378?ms=37.5018495,127.0438028,16&a=APT&b=A1&e=RETAIL",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        },
    )
    r.encoding = "utf-8-sig"
    temp = json.loads(r.text)
    # temp = list(pd.DataFrame(temp["regionList"])["cortarNo"])
    df = pd.DataFrame(temp["regionList"])
    return df


# get_sido_info 호출
sido_info = get_sido_info()
# 결과를 naver_regions 테이블에 삽입
sido_info.columns = [camel_to_snake(col) for col in sido_info.columns]
sido_info["parent_id"] = ""

insert_dataframe_into_table(sido_info, "naver_regions", if_exists="append")

# get_sido_info에서 얻은 cortarNo 값으로 get_gungu_info 호출
for cortarNo_sido in sido_info["cortar_no"]:
    gungu_info = get_gungu_info(cortarNo_sido)
    gungu_info.columns = [camel_to_snake(col) for col in gungu_info.columns]
    gungu_info["parent_id"] = cortarNo_sido

    # 결과를 naver_regions 테이블에 삽입
    insert_dataframe_into_table(gungu_info, "naver_regions", if_exists="append")
    time.sleep(get_random_time())

    # get_gungu_info에서 얻은 cortarNo 값으로 get_dong_info 호출
    for cortarNo_gungu in gungu_info["cortar_no"]:
        # 2초 지연
        time.sleep(get_random_time())
        dong_info = get_dong_info(cortarNo_gungu)
        dong_info.columns = [camel_to_snake(col) for col in dong_info.columns]
        dong_info["parent_id"] = cortarNo_gungu
        # 결과를 naver_regions 테이블에 삽입
        insert_dataframe_into_table(dong_info, "naver_regions", if_exists="append")
