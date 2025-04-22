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
    ic(proxy, url)
    try:
        response = requests.get(
            url,
            proxies=proxy,
            headers={
                "Accept-Encoding": "gzip",
                "Host": "new.land.naver.com",

                        "Referer": "https://new.land.naver.com/complexes/" + complex_no,
                        # + "?ms=37.4830877,127.0579863,15",
                        # + "?ms=37.4830877,127.0579863,15&a=APT&b=A1&e=RETAIL",
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


def apt_price(complex_no, pyeong_no):
    pyeong_no = str(pyeong_no)
    complex_no = str(complex_no)
    # p_num = temp["complexPyeongDetailList"][index]["pyeongNo"]
    # p_num = str(index)
    down_url = (
        "https://new.land.naver.com/api/complexes/"
        + complex_no
        + "/prices?complexNo="
        + complex_no
        + "&tradeType=A1&year=5&priceChartChange=true&areaNo="
        + pyeong_no
        + "&areaChange=true&type=table"
    )
    r = fetch_data(down_url, complex_no)
    r.encoding = "utf-8-sig"
    print(r.text)  # Add this line
    if r.text is None or r.text.strip() == '':
        return None
    r.encoding = "utf-8-sig"
    temp_price = json.loads(r.text)
    data = []  # Initialize an empty list
    if (
        "marketPrices" in temp_price
        and isinstance(temp_price["marketPrices"], list)
        and len(temp_price["marketPrices"]) > 0
    ):
        # Iterate over each item in the 'marketPrices' list
        for item in temp_price["marketPrices"]:
            # Add 'complex_no' and 'pyeong_no' to the item
            item["complex_no"] = complex_no
            item["pyeong_no"] = pyeong_no
            # Append the item to the list
            data.append(item)
        # Convert the list to a DataFrame
        df = pd.DataFrame(data)
        df = df[
            ["complex_no", "pyeong_no"]
            + [col for col in df.columns if col not in ["complex_no", "pyeong_no"]]
        ]
        # Convert column names to snake case
        df.columns = [camel_to_snake(col) for col in df.columns]
        return df
    else:
        print(temp_price)
    return None


def main():
    global proxies_list
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('task_number', type=int, help='Task number')
    args = parser.parse_args()

    # Load the TSV file
    df = pd.read_csv(f'tasks{args.task_number:02}.tsv', sep='\t')

    proxies_list = get_proxies()

    # Initialize an empty list to store the results
    results = []
    last_cn = None
    last_pn = None
    # Iterate over each row in the DataFrame
    for _, row in df.iterrows():
        # Call apt_price and append the result to the list
        result = apt_price(row['complex_no'], row['pyeong_no'])
        last_cn = row['complex_no']
        last_pn = row["pyeong_no"]

        if result is not None:
            results.append(result)

        # If we have 100 results, insert them into the table and clear the list
        if len(results) == 50:
            insert_dataframe_into_table(pd.concat(results), "naver_complex_prices", if_exists="append")
            print(f"==> Insert complete apt_code,pyeong_no: {last_cn}, {last_pn}")
            results.clear()

    # If there are any remaining results, insert them into the table
    if results:
        insert_dataframe_into_table(pd.concat(results), "naver_complex_prices", if_exists="append")
        print(f"==> Insert complete apt_code,pyeong_no: {last_cn}, {last_pn}")


if __name__ == '__main__':
    main()
    # insert_dataframe_into_table(df_complex_prices, "naver_complex_prices", if_exists="append")
