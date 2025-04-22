# -*- coding: utf-8 -*-

import random
import requests
from qrytool import load_data_into_dataframe, insert_dataframe_into_table
import json
import time
import pandas as pd
from icecream import ic


async def show(proxies):
    while True:
        proxy = await proxies.get()
        if proxy is None:
            break
        print("Found proxy: %s" % proxy)


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


def camel_to_snake(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def fetch_data(url):
    proxy = get_random_proxy()
    ic(proxy, url)
    try:
        response = requests.get(
            url,
            proxies=proxy,
            data={"sameAddressGroup": "false"},
            headers={
                "Accept-Encoding": "gzip",
                "Host": "new.land.naver.com",

                "Referer": "https://new.land.naver.com/complexes/102378?ms=37.5018495,127.0438028,16&b=A1&e=RETAIL",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
            },
        )
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed with proxy {proxy}. Retrying... Error: {e}")
        return fetch_data(url)  # 재시도


def get_apt_offctl_list(dong_code):
    down_url = (
        "https://new.land.naver.com/api/regions/complexes?cortarNo="
        + dong_code
        # + "&realEstateType=APT&order="
        + "&realEstateType=ALL&order="
    )
    r = fetch_data(down_url)
    r.encoding = "utf-8-sig"
    temp = json.loads(r.text)
    df = pd.DataFrame(temp["complexList"])
    return df


# proxies_list = asyncio.run(get_proxies())
proxies_list = get_proxies()

df_regions = load_data_into_dataframe(
    """select * from naver_regions where cortar_type='sec'"""
)

for cortarNo in df_regions["cortar_no"]:
    df = get_apt_offctl_list(cortarNo)
    df.columns = [camel_to_snake(col) for col in df.columns]

    insert_dataframe_into_table(df, "naver_complexes", if_exists="append")
# df = get_apt_offctl_list("1168010800")
# df
