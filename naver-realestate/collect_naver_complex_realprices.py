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
    return random.uniform(0.07, 0.63)


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
        return fetch_data(url, complex_no)  # 재시도


prev_columns = None


def apt_realprice(complex_no, pyeong_no, trade_type):
    total_cnt = None
    added_row_cnt = None
    pyeong_no = str(pyeong_no)
    complex_no = str(complex_no)
    data = []  # Initialize an empty list
    df = None

    while total_cnt is None or added_row_cnt < total_cnt:
        down_url = (f"https://new.land.naver.com/api/complexes/{complex_no}/prices/real?complexNo={complex_no}&tradeType={trade_type}&year=5&priceChartChange=false&areaNo={pyeong_no}"
                    + (f"&addedRowCount={added_row_cnt}" if added_row_cnt is not None else "")
                    + f"&areaChange={'false' if added_row_cnt is not None else 'true'}&type=table"
                    )
        # ic(down_url)
        r = fetch_data(down_url, complex_no)
        r.encoding = "utf-8-sig"
        # print(r.text)  # Add this line
        if r.text is None or r.text.strip() == '':
            return None
        r.encoding = "utf-8-sig"
        temp_price = json.loads(r.text)
        if 'totalRowCount' in temp_price:
            total_cnt = temp_price['totalRowCount']
        if 'addedRowCount' in temp_price:
            added_row_cnt = temp_price['addedRowCount']
        if ("realPriceOnMonthList" in temp_price and isinstance(temp_price["realPriceOnMonthList"], list) and len(temp_price["realPriceOnMonthList"]) > 0):
            # Iterate over each item in the 'marketPrices' list
            for item in temp_price["realPriceOnMonthList"]:
                # Add 'complex_no' and 'pyeong_no' to the item
                item["complex_no"] = complex_no
                item["pyeong_no"] = pyeong_no
                # item["trade_type"] = trade_type
                for rpl_item in item['realPriceList']:
                    rpl_item["complex_no"] = complex_no
                    rpl_item["pyeong_no"] = pyeong_no
                    # rpl_item["trade_type"] = trade_type
                    rpl_item["tradeBaseYear"] = item["tradeBaseYear"]
                    rpl_item["tradeBaseMonth"] = item["tradeBaseMonth"]
                    # Append the item to the list
                    data.append(rpl_item)
            if total_cnt is None or added_row_cnt is None:
                break
            # ic(len(data))
        else:
            print('api response:', temp_price)
            return None
        # ic(added_row_cnt, total_cnt)

    if len(data) > 0:
        df = pd.DataFrame(data)
        df = df[["complex_no", "pyeong_no"] + [col for col in df.columns if col not in ["complex_no", "pyeong_no"]]]
        # Convert column names to snake case
        df.columns = [camel_to_snake(col) for col in df.columns]
        if 'delete_yn' not in df.columns:
            df['delete_yn'] = None
        # if 'lease_price' not in df.columns:
        #     df['lease_price'] = None
        # if 'rent_price' not in df.columns:
        #     df['rent_price'] = None
        # ic(len(data))
        print('Before return df : len of df =>', len(df))
    return df


def main():
    global proxies_list

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('task_number', type=int, help='Task number')
    parser.add_argument('target_trade_type', type=str, help='Target trade type: A1, B1, B2')
    parser.add_argument('target_complex_no', type=int, help='Target complex number')
    parser.add_argument('target_pyeong_no', type=int, help='Target pyeong number')
    args = parser.parse_args()
    # Load the TSV file
    df = pd.read_csv(f'realprice_tasks{args.task_number:02}.tsv', sep='\t')

    proxies_list = get_proxies()

    # Initialize an empty list to store the results
    results = pd.DataFrame()  # Initialize an empty DataFrame
    last_cn = None
    last_pn = None
    # Iterate over each row in the DataFrame
    go_ahead = False
    for ttype in ['A1', 'B1', 'B2']:  # A1:매매, B1:전세, B2:월세
        # cnt = 0
        for _, row in df.iterrows():
            # Call apt_realprice and append the result to the list
            # cnt += 1
            # if cnt <= 5:
            #     continue
            if not go_ahead and (ttype != args.target_trade_type or int(row['complex_no']) != args.target_complex_no or int(row['pyeong_no']) != args.target_pyeong_no):
                print('Parameters of Trade type, complex_no, pyeong_no =>', ttype, int(row['complex_no']), int(row['pyeong_no']), ':', args.target_trade_type, args.target_complex_no, args.target_pyeong_no)
                continue
            else:
                print('Trade type, complex_no, pyeong_no ===>', ttype, int(row['complex_no']), int(row['pyeong_no']))
                go_ahead = True
            print('--------------------------------------------')
            result = apt_realprice(row['complex_no'], row['pyeong_no'], ttype)
            last_cn = row['complex_no']
            last_pn = row["pyeong_no"]

            # if result is not None:
            #     print(result.isnull().sum())  # Check for missing values
            #     result['unique_id'] = result['complex_no'].astype(str) + '_' + result['pyeong_no'].astype(str) + '_' + result['trade_type'].astype(str) + '_' + result['trade_year'].astype(str) + '_' + result['trade_month'].astype(str) + '_' + result['floor'].astype(str)
            #     result = result.set_index('unique_id')
            #     results = pd.concat([results, result])
            #     # results = results.set_index('unique_id')

            if result is not None:
                results = pd.concat([results, result], ignore_index=True, axis=0)
                # ic(len(results))
                # print(results)
            else:
                continue
            print(results.columns)
            # If we have more than 100 results, insert them into the table and clear the list
            if len(results) > 100:
                insert_dataframe_into_table(results, "naver_complex_realprices", if_exists="append")
                print(f"==> Insert complete apt_code,pyeong_no: {last_cn}, {last_pn}")
                results = pd.DataFrame()

        # If there are any remaining results, insert them into the table
        if not results.empty:
            insert_dataframe_into_table(results, "naver_complex_realprices", if_exists="append")
            print(f"==> Insert complete apt_code,pyeong_no: {last_cn}, {last_pn}")


if __name__ == '__main__':
    main()
    # insert_dataframe_into_table(df_complex_prices, "naver_complex_realprices", if_exists="append")
