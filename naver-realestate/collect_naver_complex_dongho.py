# -*- coding: utf-8 -*-
import argparse
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
    return random.uniform(0.5, 1.1)


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


def fetch_data(url, apt_code):
    proxy = get_random_proxy()
    ic(proxy, url)
    try:
        response = requests.get(
            url,
            proxies=proxy,
            headers={
                "Accept-Encoding": "gzip",

                "Host": "new.land.naver.com",
                        "Referer": "https://new.land.naver.com/complexes/" + apt_code + "?ms=37.482968,127.0634,16&a=APT&b=A1&e=RETAIL",
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


def get_dong_list(apt_code):
    apt_code = str(apt_code)
    down_url = f"https://new.land.naver.com/api/complexes/{apt_code}/buildings/list"
    r = fetch_data(down_url, apt_code)
    r.encoding = "utf-8-sig"
    print(r.text)  # Add this line
    if r.text is None or r.text.strip() == '':
        return None
    apt_dong_list = json.loads(r.text)
    print(apt_dong_list)
    return apt_dong_list


def get_dong_info(apt_code, dong_no):
    apt_code = str(apt_code)
    down_url = f"https://new.land.naver.com/api/complexes/{apt_code}/buildings/pyeongtype?dongNo={dong_no}&complexNo={apt_code}"
    r = fetch_data(down_url, apt_code)
    r.encoding = "utf-8-sig"
    if r.text is None or r.text.strip() == '':
        return None
    temp = json.loads(r.text)
    print(temp)
    return temp


last_inserted = None
if __name__ == "__main__":
    global proxies_list
    parser = argparse.ArgumentParser()
    parser.add_argument('task_number', type=int, help='Task number')
    args = parser.parse_args()

    # Load the TSV file
    df = pd.read_csv(f'complex_cluster_{args.task_number:02}.tsv', sep='\t')

    proxies_list = get_proxies()
    # df = load_data_into_dataframe("SELECT * FROM naver_complexes ORDER BY complex_no ASC")

    for apt_code in df['complex_no']:
        if last_inserted:
            if apt_code == last_inserted:
                last_inserted = None
                print(f"####### Insert Started {apt_code}")
            elif last_inserted is not None:
                print(f"@@@@@@@ Skip inserting {apt_code}")
                continue
        dong_list = get_dong_list(apt_code)
        if dong_list is None or 'buildingList' not in dong_list:
            continue
        for dong in dong_list['buildingList']:
            print(dong)
            dongNo = dong['dongNo']
            bildName = dong['bildName']
            temp = get_dong_info(apt_code, dongNo)
            if temp is None or 'hoListOnFloor' not in temp:
                continue
            data = []
            for floor in temp["hoListOnFloor"]:
                # ... rest of your code ...
                for item in floor["pyeongHoList"]:
                    if item is None or "hoNo" not in item:
                        continue
                    data.append(
                        {
                            "complex_no": str(apt_code),
                            "dong_no": dongNo,
                            "build_name": bildName,
                            "ho_no": item.get("hoNo", None),
                            "ho_name": item.get("hoName", None),
                            "ho_floor": item.get("hoFloor", None),
                            "pyeong_no": item.get("pyeongNo", None),
                            "pyeong_content": item.get("pyeongContent", None),
                            "supply_area": item.get("supplyArea", None),
                            "total_area": item.get("totalArea", None),
                            "pyeong_class_string": item.get("pyeongClassString", None),
                            "line_no": item.get("lineNo", None),
                            "piloti_yn": item.get("pilotiYn", None),
                            "exist_ho": item.get("existHo", None),
                            "pyeong_name": item.get("pyeongName", None),
                            "pyeong_name_decimal": item.get("pyeongNameDecimal", None),
                        }
                    )

            # Create a DataFrame from the data
            df_dongho_info = pd.DataFrame(data)
            # Insert the DataFrame into the table
            insert_dataframe_into_table(df_dongho_info, 'naver_complex_dongho', if_exists='append')
            print("Insert complete apt_code,dongNo:", apt_code, dongNo)
            # 테이블 생성 완료후 아래와 같이 인덱스 생성 필요.
            # CREATE INDEX idx_complex_dongho_new ON naver_complex_dongho(complex_no, dong_no, ho_no)
