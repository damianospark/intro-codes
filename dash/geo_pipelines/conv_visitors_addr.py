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

import mysql.connector
import pandas as pd
import requests
from sqlalchemy import create_engine, text


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
    res = requests.get("https://dapi.kakao.com/v2/local/geo/coord2address.json?", headers=headers, params=p)
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
    res = requests.get("https://dapi.kakao.com/v2/local/geo/coord2address.json?", headers=headers, params=p)
    result = json.loads(res.text)
    addr = result['documents'][0]['road_address']['address_name'] + ' ' + result['documents'][0]['road_address']['building_name']
    # print(result)
    return splilt_street_name_number(replace_address_sido(addr))


def get_new_old_addrs(lat, lng):
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'KakaoAK {}'.format(KAKAO_APIKEY)
    }
    p = urllib.parse.urlencode({'x': lng, 'y': lat})
    res = requests.get("https://dapi.kakao.com/v2/local/geo/coord2address.json?", headers=headers, params=p)
    result = json.loads(res.text)
    if 'documents' in result and result['documents'] and 'road_address' in result['documents'][0] and result['documents'][0]['road_address']:
        addr = result['documents'][0]['road_address']['address_name'] + ' ' + result['documents'][0]['road_address']['building_name']
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


BUFF_SIZE = 100


def make_signature(method, basestring, timestamp, access_key, secret_key):
    message = method + " " + basestring + "\n" + timestamp + "\n" + access_key
    signature = base64.b64encode(hmac.new(secret_key.encode(), message.encode(), digestmod=hashlib.sha256).digest())
    return signature


def request_nc_api(ip, timestamp, access_key, signature, hostname):
    uri = f"{hostname}/geolocation/v2/geoLocation?ip={ip}&ext=t&responseFormatType=json"
    headers = {'x-ncp-apigw-timestamp': timestamp,
               'x-ncp-iam-access-key': access_key,
               'x-ncp-apigw-signature-v2': signature}
    res = requests.get(uri, headers=headers)
    return res.content.decode('utf-8')


def write_to_file(rows):
    print(f"=== 데이터 저장 : buffer size:{BUFF_SIZE}, {len(rows)}건 저장 ===")
    with open(IP_CACHE_FILE, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(rows)


def cache_addrs():
    # Check if the result.tsv file exists and is empty
    write_header = False
    try:
        if os.path.getsize(IP_CACHE_FILE) == 0:
            write_header = True
    except BaseException:
        write_header = True
        raise

    # If the file is empty, write headers
    if write_header:
        print("=== file이 존재하지 않아 헤더를 기록함 ===")
        with open(IP_CACHE_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            headers = ["IP", "Code", "R1", "R2", "R3", "Latitude", "Longitude", "Datetime", "New Address", "Old Address"]
            writer.writerow(headers)

    # Check existing IPs
    existing_ips = set()
    with open(IP_CACHE_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # skip header
        for row in reader:
            existing_ips.add(row[0])  # Assuming IP is the first column
        print(f"=== 캐시된 파일 발견 : {len(existing_ips)}건 존재 ===")

    # # Process IPs
    # with open('ips.txt', 'r', encoding='utf-8') as f:
    #     ips = f.read().splitlines()

    # MySQL connection details
    # Connect to MySQL
    # connection = mysql.connector.connect(**mysql_config)
    # cursor = connection.cursor()
    connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    engine = create_engine(connection_string)
    connection = engine.connect()

    # Fetch distinct IPs from the database
    query = """
    SELECT
        ip,
        DATE_FORMAT(  MIN(CONVERT_TZ(FROM_UNIXTIME(dt), '+00:00', '-09:00')), '%%Y-%%m-%%d %%H:%%i:%%s') AS vst_dt
    FROM
        wp_slim_stats
    GROUP BY ip;
    """
    # cursor.execute(query)

    wp_slim_stats = pd.read_sql(text(query), connection)
    ips = wp_slim_stats['ip'].tolist()
    # ips = [row[0] for row in cursor.fetchall()]
    # Close the connection
    # cursor.close()
    # connection.close()
    print(f"=== DB에서 발견된 IP 주소 : {len(ips)}건 ===")
    # Convert the 'ip' and 'vst_dt' columns of wp_slim_stats into a dictionary
    ip_to_vst_dt = dict(zip(wp_slim_stats['ip'], wp_slim_stats['vst_dt']))

    buffered_rows = []
    for ip in ips:
        if ip not in existing_ips:
            timestamp = str(int(time.time() * 1000))
            basestring = f"/geolocation/v2/geoLocation?ip={ip}&ext=t&responseFormatType=json"
            signature = make_signature("GET", basestring, timestamp, NC_ACCESS_KEY, NC_SECRET_KEY)
            response = json.loads(request_nc_api(ip, timestamp, NC_ACCESS_KEY, signature, NC_HOSTNAME))
            geo_data = response.get("geoLocation", {})
            lat, lng = geo_data.get("lat", ""), geo_data.get("long", "")
            print("finding -->", ip, lat, lng)
            new_addr, old_addr = get_new_old_addrs(lat, lng)
            # Get vst_dt for the current ip or set a default value (e.g., empty string)
            vst_dt_for_ip = ip_to_vst_dt.get(ip, "")
            # Extracting relevant data
            data = [
                ip,
                geo_data.get("code", ""),
                geo_data.get("r1", ""),
                geo_data.get("r2", ""),
                geo_data.get("r3", ""),
                lat, lng,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                new_addr, old_addr,
                vst_dt_for_ip   # Add the vst_dt value here
            ]
            # Append data to the buffer
            buffered_rows.append(data)
            # Check if buffer has reached 100 rows
            if len(buffered_rows) >= BUFF_SIZE:
                write_to_file(buffered_rows)
                # Clear the buffer
                buffered_rows = []

    # Write any remaining rows in the buffer to the file
    if buffered_rows:
        write_to_file(buffered_rows)


if __name__ == "__main__":
    cache_addrs()
