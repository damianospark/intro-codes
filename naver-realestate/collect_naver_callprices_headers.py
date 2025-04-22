import argparse
import numpy as np
import random
import requests
from qrytool import load_data_into_dataframe, insert_dataframe_into_table
import json
import time
import pandas as pd
from icecream import ic
import re


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def get_random_time():
    return random.uniform(0.1, 0.8)


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


def fetch_data(url, complex_no):
    proxy = get_random_proxy()
    # ic(proxy, url)
    try:
        response = requests.get(
            url,
            proxies=proxy,
            headers={
                "Accept-Encoding": "gzip",
                "Host": "new.land.naver.com",

                        "Referer": "https://new.land.naver.com/complexes/" + complex_no + "?ms=37.474847,127.10508,17&a=OPST:OBYG:PRE&e=RETAIL",
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


# def apt_call_price(complex_no):
#     # pyeong_no = str(pyeong_no)
#     complex_no = str(complex_no)
#     pn = 1
#     # p_num = temp["complexPyeongDetailList"][index]["pyeongNo"]
#     # p_num = str(index)
#     # down_url = f"https://new.land.naver.com/api/articles/complex/{complex_no}?realEstateType=OPST%3AAPT%3APRE&tradeType=&tag=%3A%3A%3A%3A%3A%3A%3A%3A&rentPriceMin=0&rentPriceMax=900000000&priceMin=0&priceMax=900000000&areaMin=0&areaMax=900000000&oldBuildYears&recentlyBuildYears&minHouseHoldCount&maxHouseHoldCount&showArticle=false&sameAddressGroup=false&minMaintenanceCost&maxMaintenanceCost&priceType=RETAIL&directions=&page=1&complexNo={complex_no}&buildingNos=&areaNos=&type=list&order=rank"
#     down_url = f"https://new.land.naver.com/api/articles/complex/{complex_no}?realEstateType=OPST%3AAPT%3APRE&tradeType=&oldBuildYears&recentlyBuildYears&minHouseHoldCount&maxHouseHoldCount&showArticle=false&sameAddressGroup=false&minMaintenanceCost&maxMaintenanceCost&priceType=RETAIL&directions=&page={pn}&complexNo={complex_no}&buildingNos=&areaNos=&type=list&order=rank"
#     #    f"https://new.land.naver.com/api/articles/complex/{complex_no}?realEstateType=OPST%3AAPT%3APRE&tradeType=&tag=%3A%3A%3A%3A%3A%3A%3A%3A&rentPriceMin=0&rentPriceMax=900000000&priceMin=0&priceMax=900000000&areaMin=0&areaMax=900000000&oldBuildYears&recentlyBuildYears&minHouseHoldCount&maxHouseHoldCount&showArticle=false&sameAddressGroup=false&minMaintenanceCost&maxMaintenanceCost&priceType=RETAIL&directions=&page=1&complexNo=106710&buildingNos=&areaNos=&type=list&order=rank"
#     r = fetch_data(down_url, complex_no)
#     r.encoding = "utf-8-sig"
#     print(r.text)  # Add this line
#     if r.text is None or r.text.strip() == '':
#         return None
#     r.encoding = "utf-8-sig"
#     temp_price = json.loads(r.text)
#     return temp_price
def apt_call_price(complex_no):
    complex_no = str(complex_no)
    pn = 1
    data = []

    while True:
        down_url = f"https://new.land.naver.com/api/articles/complex/{complex_no}?realEstateType=OPST%3AAPT%3APRE&tradeType=&oldBuildYears&recentlyBuildYears&minHouseHoldCount&maxHouseHoldCount&showArticle=false&sameAddressGroup=false&minMaintenanceCost&maxMaintenanceCost&priceType=RETAIL&directions=&page={
            pn}&complexNo={complex_no}&buildingNos=&areaNos=&type=list&order=rank"
        r = fetch_data(down_url, complex_no)
        r.encoding = "utf-8-sig"
        if r.text is None or r.text.strip() == '':
            break
        temp_price = json.loads(r.text)
        data.extend(temp_price['articleList'])
        if not temp_price['isMoreData']:
            break
        pn += 1

    return data


# proxies_list = get_proxies()

# temp = apt_call_price(106710)
# print(temp, len(temp))

# if __name__ == "__main__":
#     global proxies_list
#     parser = argparse.ArgumentParser()
#     parser.add_argument('task_number', type=int, help='Task number')
#     args = parser.parse_args()

#     # Load the TSV file
#     df = pd.read_csv(f'complex_cluster_{args.task_number:02}.tsv', sep='\t')

#     proxies_list = get_proxies()
#     # df = load_data_into_dataframe("SELECT * FROM naver_complexes ORDER BY complex_no ASC")
#     # data = []
#     for apt_code in df['complex_no']:
#         temp = apt_call_price(apt_code)
#         print(temp)
#         df_callprices = pd.DataFrame(temp)
#         df_callprices.columns = [camel_to_snake(col) for col in df_callprices.columns]
#         df_callprices['complex_no'] = apt_code
#         df_callprices = df_callprices[['complex_no'] + [col for col in df_callprices.columns if col != 'complex_no']]
#         try:
#             insert_dataframe_into_table(df_callprices, 'naver_complex_callprices', if_exists='append')
#         except Exception as e:
#             print(f"Error occurred: {e}. Inserting into 'naver_complex_callprices2' instead.")
#             insert_dataframe_into_table(df_callprices, 'naver_complex_callprices2', if_exists='append')
if __name__ == "__main__":
    global proxies_list
    parser = argparse.ArgumentParser()
    parser.add_argument('task_number', type=int, help='Task number')
    args = parser.parse_args()
    proxies_list = get_proxies()

    # Load the TSV file
    df = pd.read_csv(f'complex_cluster_{args.task_number:02}.tsv', sep='\t')
    all_headers = set()
    all_data = []
    # cnt = 0
    for apt_code in df['complex_no']:
        temp = apt_call_price(apt_code)
        # print(temp)
        df_callprices = pd.DataFrame(temp)
        # df_callprices.loc[:, 'complexNo'] = apt_code
        df_callprices['complexNo'] = apt_code
        all_data.append(df_callprices)
        all_headers.update(df_callprices.columns)
        print(f"all_headers[camel]{apt_code} ==>", all_headers)
        # cnt += 1
        # if cnt > 10:
        #     break

    all_headers = [camel_to_snake(col) for col in all_headers]
    print(f"all_headers[snake] ==>", all_headers)

    for df_callprices in all_data:
        df_callprices.columns = [camel_to_snake(col) for col in df_callprices.columns]
        missing_cols = set(all_headers) - set(df_callprices.columns)
        for col in missing_cols:
            df_callprices[col] = None
        df_callprices = df_callprices[all_headers]
        df_callprices = df_callprices[['complex_no'] + [col for col in df_callprices.columns if col != 'complex_no']]

        chunk_size = 500  # adjust this value based on your needs
        chunks = [df_callprices[i:i + chunk_size] for i in range(0, df_callprices.shape[0], chunk_size)]

        for chunk in chunks:
            try:
                insert_dataframe_into_table(chunk, 'naver_complex_callprices', if_exists='append')
            except Exception as e:
                print(f"Error occurred: {e}. Inserting into 'naver_complex_callprices2' instead.")
                insert_dataframe_into_table(chunk, 'naver_complex_callprices2', if_exists='append')
