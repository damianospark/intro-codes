import base64
import csv
import hashlib
import hmac
import io
import json
import os
import re
import time
import urllib
from datetime import datetime

import pandas as pd
import requests
from sqlalchemy import Float, Integer, String, create_engine, text


def replace_address_sido(address):
    sido_mapping = {
        "특별자치": "",
        "서울특별시": "서울",
        "부산광역시": "부산",
        "대구광역시": "대구",
        "인천광역시": "인천",
        "광주광역시": "광주",
        "대전광역시": "대전",
        "울산광역시": "울산",
        "세종시": "세종",
        "경기도": "경기",
        "강원도": "강원",
        "충청북도": "충북",
        "충청남도": "충남",
        "전라북도": "전북",
        "전라남도": "전남",
        "경상북도": "경북",
        "경상남도": "경남",
        "제주도": "제주",
    }
    for key, value in sido_mapping.items():
        address = address.replace(key, value)
    return address.strip()


def splilt_street_name_number(addr):
    """동/로 뒤에 숫자가 붙어서 표현되어 있어 스페이스를 추가해주는 로직

    Args:
        addr (str): 일반적인 주소

    Returns:
        str: 동/로 뒤에 스페이스가 추가된 문자열
    """
    target = re.sub(r"#.*", "", addr)
    target = re.sub(r"\t", r" ", target)
    target = re.sub(r" ([가-힣]+동)([0-9])", r" \1 \2", target)
    target = re.sub(r" ([가-힣]+로)([0-9])", r" \1 \2", target)
    return target


# Function to extract region from address

def extract_region(address):
    three_word_regions = {
        "경남 창원시", "경북 포항시", "경기 고양시", "경기 안산시", "전북 전주시",
        "충북 청주시", "충남 천안시", "경기 용인시", "경기 안양시", "경기 수원시", "경기 성남시"
    }
    words = address.split()
    if " ".join(words[:2]) in three_word_regions:
        return " ".join(words[:3])
    return " ".join(words[:2])


def get_lati_longi(addr):
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + addr
    headers = {"Authorization": "KakaoAK 1fe58e9d9c62369f81cdb65f851c7b18"}
    # print(requests.get(url, headers=headers).status_code)
    result = json.loads(str(requests.get(url, headers=headers).text))
    # print(result)
    location = result['documents'][0]['address']
    x1, y1 = location['x'], location['y']
    return [round(float(y1), 5), round(float(x1), 5)]


def get_old_addr(lat, lng):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'KakaoAK {}'.format(KAKAO_APIKEY)
    }
    p = urllib.parse.urlencode({'x': lng, 'y': lat})
    # result = requests.get("https://dapi.kakao.com/v2/local/search/address.json", headers=headers, params=p)
    res = requests.get(
        "https://dapi.kakao.com/v2/local/geo/coord2address.json?", headers=headers, params=p)
    result = json.loads(res.text)
    # print(result)
    addr = result['documents'][0]['address']['address_name']
    return splilt_street_name_number(replace_address_sido(addr))


def get_new_addr(lat, lng):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'KakaoAK {}'.format(KAKAO_APIKEY)
    }
    p = urllib.parse.urlencode({'x': lng, 'y': lat})
    res = requests.get(
        "https://dapi.kakao.com/v2/local/geo/coord2address.json?", headers=headers, params=p)
    result = json.loads(res.text)
    addr = result['documents'][0]['road_address']['address_name'] + \
        ' ' + result['documents'][0]['road_address']['building_name']
    # print(result)
    return splilt_street_name_number(replace_address_sido(addr))


def get_new_old_addrs(lat, lng):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'KakaoAK {}'.format(KAKAO_APIKEY)
    }
    p = urllib.parse.urlencode({'x': lng, 'y': lat})
    res = requests.get(
        "https://dapi.kakao.com/v2/local/geo/coord2address.json?", headers=headers, params=p)
    result = json.loads(res.text)
    if 'documents' in result and result['documents'] and 'road_address' in result['documents'][0] and result['documents'][0]['road_address']:
        addr = result['documents'][0]['road_address']['address_name'] + \
            ' ' + result['documents'][0]['road_address']['building_name']
    else:
        addr = "n/a"
    new_addr = splilt_street_name_number(replace_address_sido(addr))

    if 'documents' in result and result['documents'] and 'address' in result['documents'][0] and result['documents'][0]['address']:
        addr = result['documents'][0]['address']['address_name']
    else:
        addr = "n/a"
    old_addr = splilt_street_name_number(replace_address_sido(addr))
    return new_addr, old_addr

# naver cloud 요금 확인하기 : https://www.ncloud.com/product/applicationService/geoLocation




def make_signature(method, basestring, timestamp, access_key, secret_key):
    message = method + " " + basestring + "\n" + timestamp + "\n" + access_key
    signature = base64.b64encode(hmac.new(
        secret_key.encode(), message.encode(), digestmod=hashlib.sha256).digest())
    return signature


def request_nc_api(ip, timestamp, access_key, signature, hostname):
    uri = f"{hostname}/geolocation/v2/geoLocation?ip={ip}&ext=t&responseFormatType=json"
    headers = {'x-ncp-apigw-timestamp': timestamp,
               'x-ncp-iam-access-key': access_key,
               'x-ncp-apigw-signature-v2': signature}
    res = requests.get(uri, headers=headers)
    return res.content.decode('utf-8')


def get_all_addr_info_line(addr, user_registered_seoul, ip):
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + addr
    headers = {"Authorization": "KakaoAK 1fe58e9d9c62369f81cdb65f851c7b18"}
    # print(requests.get(url, headers=headers).status_code)
    result = json.loads(str(requests.get(url, headers=headers).text))
    # print(addr)
    # print(result)
    if not result['documents'] or not result['documents'][0]['address'] or not result['documents'][0]['address']['y']:
        return None
    location = result['documents'][0]['address']
    new_addr = result['documents'][0]['road_address']
    x1, y1 = location['x'], location['y']
    # TODO: 아래 내용에 해당하는 모든 정보를 받는다. 그래서 캐시에 남길 때 사용한다.
    # IP	Code	R1	R2	R3	Latitude	Longitude	Datetime	New Address	Old Address	vst_dt
    result_dict = {
        'IP': ip,
        'Code': location['b_code'],
        'R1': location['region_1depth_name'],
        'R2': location['region_2depth_name'],
        'R3': location['region_3depth_name'],
        'Latitude': round(float(y1), 5),
        'Longitude': round(float(x1), 5),
        'Datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'New Address': new_addr['address_name'] + ' ' + new_addr.get('building_name', '') if new_addr else '',
        'Old Address': location['address_name'],
        'vst_dt': user_registered_seoul
    }
    return result_dict


def write_to_file(rows):
    file_exists = os.path.isfile(IP_CACHE_FILE)  # 파일이 이미 존재하는지 확인
    file_empty = os.path.getsize(
        IP_CACHE_FILE) == 0 if file_exists else False  # 파일이 비어 있는지 확인
    print("file status ", file_exists, file_empty)
    print(f"=== 데이터 저장 : buffer size:{BUFF_SIZE}, {len(rows)}건 저장 ===")
    with open(IP_CACHE_FILE, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        if not file_exists or file_empty:  # 파일이 존재하지 않거나 비어 있으면 헤더를 씁니다.
            writer.writerow(['IP', 'Code', 'R1', 'R2', 'R3', 'Latitude',
                            'Longitude', 'Datetime', 'New Address', 'Old Address', 'vst_dt'])
        writer.writerows(rows)  # 행을 파일에 추가합니다.





def cache_addrs():
    # 데이터베이스에서 주소와 user_registered_seoul 가져오기
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    # query = 'SELECT shipping_address_1, user_registered_seoul, "IP Address" FROM cust02'
    query = '''
    (SELECT billing_address_1 as "shipping_address_1", user_registered_seoul, "IP Address" FROM cust02)
    UNION
    (SELECT
        "배송지 주소" AS shipping_address_1,
        "결제일시" AS user_registered_seoul,
        NULL AS "IP Address"
    FROM sales01);
    '''
    db_data = pd.read_sql(query, connection)
    connection.close()

    # 캐시된 주소 로드
    cache_df = pd.read_csv(IP_CACHE_FILE, sep='\t', header=0)
    print(cache_df)
    new_data = []
    for index, row in db_data.iterrows():
        addr, user_registered_seoul, ip = row['shipping_address_1'], row['user_registered_seoul'], row['IP Address']
        # addr이 None이라면 건너뜀
        if addr is None:
            continue
        pattern = re.compile(r'(.*) (\(.*, (.*)\)|\((.*)\))(.*)')
        addr = pattern.sub(r'\1 \3', addr)
        print("addr, user_registered_seoul, ip  ==>",
              addr, user_registered_seoul, ip)
        # 'New Address'와 'Old Address' 컬럼에서 주소를 검사
        if addr not in cache_df['New Address'].values and addr not in cache_df['Old Address'].values:
            result = get_all_addr_info_line(addr, user_registered_seoul, ip)
            if not result:
                continue
            new_data.append(result)

            if len(new_data) >= BUFF_SIZE:
                write_to_file([list(d.values()) for d in new_data])
                new_data = []

    # 나머지 데이터 저장
    if new_data:
        write_to_file([list(d.values()) for d in new_data])


if __name__ == "__main__":
    cache_addrs()
