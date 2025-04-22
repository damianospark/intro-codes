# -*- coding: utf-8 -*-

import gzip
import hashlib
import io
import json
import math
import re
import sqlite3
import time
# from sqlalchemy import text, Integer, String
import traceback
import zlib
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import hashids
import numpy as np
import pandas as pd
import requests
from fuzzywuzzy import fuzz
from icecream import ic
from logging_config import configure_logging
from qrytool import (execute_query, insert_dataframe_into_table,
                     load_data_into_dataframe, upsert_dataframe_into_table)
from requests_cache import CachedSession

logger = configure_logging(__file__)


def haversine(coord1, coord2):
    # 두 위치 좌표간 직선 거리 구하기
    # 좌표는 (위도, 경도) 튜플 형태로 입력
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # 라디안으로 변환
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # 위도와 경도 차이
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # 헤버사인 공식 사용
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    # 지구의 반지름 (킬로미터 단위)
    r = 6371

    # 최종 거리 계산
    return c * r


def replace_address_sido(address):
    sido_mapping = {
        "특별자치": "",
        "서울시": "서울",
        "부산시": "부산",
        "대구시": "대구",
        "인천시": "인천",
        "대전시": "대전",
        "울산시": "울산",
        "창원시": "창원",
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
        "  ": " ",
        "세종 세종": "세종"
    }

    if address is None:
        return None
    for key, value in sido_mapping.items():
        address = address.replace(key, value)
    return address.strip()


def extract_region(address):
    three_word_regions = {
        "경남 창원시", "경북 포항시", "경기 고양시", "경기 안산시", "전북 전주시",
        "충북 청주시", "충남 천안시", "경기 용인시", "경기 안양시", "경기 수원시", "경기 성남시"
    }
    if address is None:
        return None
    words = address.split()
    if " ".join(words[:2]) in three_word_regions:
        return " ".join(words[:3])
    return " ".join(words[:2])


def process_sub_building_no(x):
    try:
        # NaN 또는 무한대인지 확인
        if pd.notna(x) and not np.isinf(float(x)):
            return f'{int(x):d}'
    except ValueError:
        # x를 float로 변환할 수 없는 경우 (예: 문자열)
        pass
    return None


def is_similar_to_old(given_str, old_str, new_str):
    # given_str과 old_str 간의 유사도 점수 계산
    old_similarity = fuzz.ratio(given_str, old_str)
    # given_str과 new_str 간의 유사도 점수 계산
    new_similarity = fuzz.ratio(given_str, new_str)

    # old_str의 점수가 new_str의 점수보다 높거나 같으면 True 반환
    return old_similarity >= new_similarity


def get_kr_addr_type(address, unclear_mark="지번"):
    address = re.sub(r"\(.*?\)", "", address)
    road_address_pattern = re.compile(r"(로|길)\b")
    jibun_address_pattern = re.compile(r"(동|리|가)(?!\d)\b")

    if jibun_address_pattern.search(address):
        return "지번"
    elif road_address_pattern.search(address):
        return "도로"
    else:
        return unclear_mark


def get_old_addr_from_addressalls_clbe(addr):
    # 도로명 주소만 있고 그 뒤 주소는 없는 주소여야함. 즉, 회원주소1 에 해당하는 값.
    if get_kr_addr_type(addr) == "지번":
        return addr
    df = load_data_into_dataframe(f"SELECT old_addr FROM addressalls WHERE new_addr='{addr}'")
    if len(df) > 0:
        old_addr = df.iloc[0]
    else:
        old_addr_dict = get_naver_coordinates(addr)
        old_addr = old_addr_dict['old_addr'] if old_addr_dict else ''
        if not old_addr_dict or old_addr_dict['old_addr'] == '':
            print(f'old_addr is None:{addr} => {str(old_addr_dict)}')
    return old_addr


def split_address(address):
    match = None
    group2 = None
    group3 = None
    group4 = None
    group5 = None
    group6 = None
    addr1 = None
    addr2 = None
    if pd.notnull(address):
        pattern = re.compile(
            r"\s[\-0-9]+\s(\([가-힣a-zA-Z0-9,\s]+\)\s)?(.*)|.*구.*동\s(.*\s아파트)(.*)|[\s로길동]+[\-0-9번지]+(\([가-힣a-zA-Z0-9,\s]+\))?([,\s].*)"
        )
        match = pattern.search(address)  # search를 사용하여 전체 문자열에서 패턴 매치

        if match:
            group2 = match.group(2)
            group3 = match.group(3)
            group4 = match.group(4)
            group5 = match.group(5)
            group6 = match.group(6)
            logger.error(
                f"{ match.group(1)} | {group2}|{group3}|{group4}|{group5}|{group6}|"
            )
            if group2:
                addr1 = address.replace(group2, "")
                addr2 = group2
            elif group3:
                if "아파트" in group3:
                    addr1 = address.replace(group4, "")
                    addr2 = group4
                else:
                    addr1 = address.replace(group3, "")
                    addr2 = group3
            elif group6.strip():
                addr1 = address.replace(group6, "")
                addr2 = group6.replace(",", "").strip()
            else:
                addr1 = address
                addr2 = None
            ret1 = addr1
            ret2 = addr2
        else:
            logger.info("No match")
            ret1 = address
            ret2 = None
    return ret1, ret2


def process_addresses(row, address_col='billing_address'):
    match = None
    group2 = None
    group3 = None
    group4 = None
    group5 = None
    group6 = None
    addr1 = None
    addr2 = None
    address = row[address_col]
    if pd.notnull(address) and pd.isnull(row[f'{address_col}2']):
        pattern = re.compile(
            r"\s[\-0-9]+\s(\([가-힣a-zA-Z0-9,\s]+\)\s)?(.*)|.*구.*동\s(.*\s아파트)(.*)|[\s로길동]+[\-0-9번지]+(\([가-힣a-zA-Z0-9,\s]+\))?([,\s].*)")
        match = pattern.search(address)  # search를 사용하여 전체 문자열에서 패턴 매치
        try:
            if match:
                group2 = match.group(2)
                group3 = match.group(3)
                group4 = match.group(4)
                group5 = match.group(5)
                group6 = match.group(6)
                if group2:
                    addr1 = address.replace(group2, "")
                    addr2 = group2
                elif group3:
                    if "아파트" in group3:
                        addr1 = address.replace(group4, "")
                        addr2 = group4
                    else:
                        addr1 = address.replace(group3, "")
                        addr2 = group3
                elif group6.strip():
                    addr1 = address.replace(group6, "")
                    addr2 = group6.replace(",", "").strip()
                else:
                    addr1 = address
                    addr2 = None
                row[f'{address_col}1'] = addr1.strip() if addr1 else addr1
                row[f'{address_col}2'] = addr2.strip() if addr2 else addr2
            else:
                row[f'{address_col}1'] = address.strip()
                row[f'{address_col}2'] = None
        except Exception:
            logger.error(address)
            if match:
                logger.error(f"{ match.group(1)} | {group2} | {group3} | {group4} | {group5} | {group6}  ")

    return row


def get_naver_rcode(lati, longi):
    # API setup for reverse geocoding
    reverse_geocode_url = (
        "https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc"
    )
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }
    reverse_geocode_params = {
        "coords": f"{longi},{lati}",
        "output": "json",
        "orders": "legalcode,admcode,addr,roadaddr",
    }

    # Reverse geocoding request
    response = requests.get(
        reverse_geocode_url, headers=headers, params=reverse_geocode_params
    )
    if response.status_code == 200:
        reverse_geocode_result = response.json()
        results = reverse_geocode_result.get("results", [])
        additional_info = {}

        for result in results:
            if result["name"] == "legalcode":
                additional_info["bcode"] = result["code"]["id"]
            elif result["name"] == "admcode":
                additional_info["hcode"] = result["code"]["id"]
            elif result["name"] == "addr":
                additional_info["old_addr"] = (
                    result["region"]["area1"]["name"]
                    + " "
                    + result["region"]["area2"]["name"]
                    + " "
                    + result["region"]["area3"]["name"]
                    + " "
                    + result["land"]["number1"]
                    + (
                        "-" + result["land"]["number2"]
                        if result["land"]["number2"]
                        else ""
                    )
                )
                additional_info["r1"] = result["region"]["area1"]["name"]
                additional_info["r2"] = result["region"]["area2"]["name"]
                additional_info["r3"] = result["region"]["area3"]["name"]
            elif result["name"] == "roadaddr":
                additional_info["new_addr"] = (
                    result["region"]["area1"]["name"]
                    + " "
                    + result["region"]["area2"]["name"]
                    + " "
                    + result["region"]["area3"]["name"]
                    + " "
                    + result["land"]["name"]
                    + " "
                    + result["land"]["number1"]
                )
                additional_info["building_name"] = result["land"]["addition0"]["value"]
                additional_info["sub_building_no"] = result["land"]["addition1"][
                    "value"
                ]

        return additional_info
    return None


def get_naver_coordinates(address):
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
    }
    params = {"query": address}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        result = response.json()
        if result["addresses"]:
            address_info = result["addresses"][0]

            # Fetch additional information using reverse geocoding
            additional_info = get_naver_rcode(address_info["y"], address_info["x"])

            return {
                "old_addr": replace_address_sido(additional_info.get("old_addr", "")),
                "new_addr": replace_address_sido(additional_info.get("new_addr", "")),
                "building_name": additional_info.get("building_name", ""),
                "sub_building_no": additional_info.get("sub_building_no", ""),
                "lati": round(float(address_info["y"]), 5),
                "longi": round(float(address_info["x"]), 5),
                "hcode": additional_info.get("hcode", ""),
                "r1": replace_address_sido(additional_info.get("r1", "")),
                "r2": additional_info.get("r2", ""),
                "r3": additional_info.get("r3", ""),
                "bcode": additional_info.get("bcode", ""),
            }
    return None


def failover_to_naver(addr):
    naver_addr_info = get_naver_coordinates(addr)
    if naver_addr_info:

        tmp_old = replace_address_sido(naver_addr_info['old_addr'])
        tmp_new = replace_address_sido(naver_addr_info['new_addr'])
        old_addr1, _ = split_address(tmp_old)
        new_addr1, _ = split_address(tmp_new)

        addr_similar_to_old = is_similar_to_old(addr, old_addr1, new_addr1)
        naver_addr_info['old_addr'] = old_addr1 if not addr_similar_to_old else addr
        naver_addr_info['new_addr'] = new_addr1 if addr_similar_to_old else addr
        return naver_addr_info
    return None


def get_kakao_coordinates(addr):
    content_dict = None
    response = None
    try:
        time.sleep(0.05)
        url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + addr
        # headers = {"Authorization": "KakaoAK 1fe58e9d9c62369f81cdb65f851c7b18"} # clean go 용
        headers = {"Authorization": "KakaoAK 7af15957ce2e9690d8f437d310fd9bdd"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            # API 요청 실패 시 예외 발생
            return "API request failed with status code {}".format(response.status_code)
        content_dict = json.loads(response.text)
        if not content_dict or len(content_dict["documents"]) == 0:
            return None
        logger.info(f"조회 성공 =>{addr}")
        old_addr = (
            replace_address_sido(content_dict["documents"][0]["address"]["address_name"])
            if content_dict["documents"][0]["address"]
            else None
        )
        new_addr = replace_address_sido(content_dict["documents"][0]["road_address"]["address_name"]
                                        ) if content_dict["documents"][0]["road_address"] else None
        hcode = content_dict["documents"][0]["address"]["h_code"] if content_dict["documents"][0]["address"] else None
        bcode = content_dict["documents"][0]["address"]["b_code"]
        r1 = content_dict["documents"][0]["address"]["region_1depth_name"]
        r2 = content_dict["documents"][0]["address"]["region_2depth_name"]
        r3 = content_dict["documents"][0]["address"]["region_3depth_name"]
        y = content_dict["documents"][0]["address"]["y"]
        x = content_dict["documents"][0]["address"]["x"]
        building_name = content_dict["documents"][0]["road_address"]["building_name"] if new_addr else None
        sub_building_no = content_dict["documents"][0]["road_address"]["sub_building_no"] if new_addr else None

        addr_similar_to_old = is_similar_to_old(addr, old_addr, new_addr)
        return {
            "old_addr": old_addr if not addr_similar_to_old else addr,
            "new_addr": new_addr if addr_similar_to_old else addr,
            "building_name": building_name,
            "sub_building_no": sub_building_no,
            "lati": round(float(y), 5),
            "longi": round(float(x), 5),
            "hcode": hcode,
            "r1": replace_address_sido(r1),
            "r2": r2,
            "r3": r3,
            "bcode": bcode,
        }
    except Exception as e:
        print("Error occurred: ", e)
        print("response:", response.text, f" addr:{addr}|")
        print("response:", response.status_code, " addr:", addr)
        traceback.print_exc()
        return None


def get_lati_longi(addr, retry_call=False):
    content_dict = None
    response = None
    try:
        time.sleep(0.05)
        url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + addr
        # headers = {"Authorization": "KakaoAK 1fe58e9d9c62369f81cdb65f851c7b18"} # clean go 용
        headers = {"Authorization": "KakaoAK 7af15957ce2e9690d8f437d310fd9bdd"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            # API 요청 실패 시 예외 발생
            raise Exception(
                "API request failed with status code {}".format(response.status_code)
            )
        content_dict = json.loads(response.text)
        if not content_dict or len(content_dict["documents"]) == 0:
            logger.info(f"failover_to_naver => {addr}")
            ret = failover_to_naver(addr)
            ret_text = "조회 실패" if not ret else "조회 성공"
            logger.info(f"{ret_text}=> {addr}")
            return ret

        logger.info(f"조회 성공 =>{addr}")
        old_addr = (
            replace_address_sido(content_dict["documents"][0]["address"]["address_name"])
            if content_dict["documents"][0]["address"]
            else None
        )
        new_addr = (
            replace_address_sido(content_dict["documents"][0]["road_address"]["address_name"])
            if content_dict["documents"][0]["road_address"]
            else None
        )
        hcode = (
            content_dict["documents"][0]["address"]["h_code"]
            if content_dict["documents"][0]["address"]
            else None
        )
        bcode = content_dict["documents"][0]["address"]["b_code"]
        r1 = content_dict["documents"][0]["address"]["region_1depth_name"]
        r2 = content_dict["documents"][0]["address"]["region_2depth_name"]
        r3 = content_dict["documents"][0]["address"]["region_3depth_name"]
        y = content_dict["documents"][0]["address"]["y"]
        x = content_dict["documents"][0]["address"]["x"]
        building_name = (
            content_dict["documents"][0]["road_address"]["building_name"]
            if new_addr
            else None
        )
        sub_building_no = (
            content_dict["documents"][0]["road_address"]["sub_building_no"]
            if new_addr
            else None
        )

        addr_similar_to_old = is_similar_to_old(addr, old_addr, new_addr)
        return {
            "old_addr": old_addr if not addr_similar_to_old else addr,
            "new_addr": new_addr if addr_similar_to_old else addr,
            "building_name": building_name,
            "sub_building_no": sub_building_no,
            "lati": round(float(y), 5),
            "longi": round(float(x), 5),
            "hcode": hcode,
            "r1": replace_address_sido(r1),
            "r2": r2,
            "r3": r3,
            "bcode": bcode,
        }
    except Exception as e:
        print("Error occurred: ", e)
        print("response:", response.text, f" addr:{addr}|")
        print("response:", response.status_code, " addr:", addr)
        traceback.print_exc()
        return None


def extract_kakao_cache():
    def create_key(request: requests.PreparedRequest, **kwargs) -> str:
        """Generate a custom cache key for the given request"""
        parsed_url = urlparse(request.url)
        # ic(parsed_url.path, parsed_url.params)
        src = f"{parsed_url.path}{parsed_url.query}{parsed_url.params}"
        # ic(src)
        # create a hashids object
        hashids_object = hashids.Hashids()
        # create a hash of the input string
        input_string = src
        input_string_hash = int(hashlib.sha256(input_string.encode()).hexdigest(), 16)
        # encode the hash of the input string to a short string
        short_id = hashids_object.encode(input_string_hash)
        return short_id

    cache = CachedSession(
        "./kakao_cache",
        backend="sqlite",
        serializer="json",
        use_cache_dir=False,  # Save files in the default user cache dir
        # Use Cache-Control response headers for expiration, if available
        cache_control=True,
        # Otherwise expire responses after one day
        expire_after=timedelta(days=60),
        # Cache 400 responses as a solemn reminder of your failures
        allowable_codes=[200, 400],
        allowable_methods=["GET", "POST"],  # Cache whatever HTTP methods you want
        # Don't match this request param, and redact if from the cache
        ignored_parameters=["api_key"],
        # Cache a different response per language
        match_headers=["Accept-Language"],
        # In case of request errors, use stale cache data if possible
        stale_if_error=True,
        key_fn=create_key,
    ).cache

    #
    # h_code : 행정코드 마지막 두자리가 항상 00 읍면동까지만
    # b_code : 법정코드 마지막 두 자리까지 숫자로 채워짐.  마지막 두자리로 리까지 표현
    # 네이버 ip2주소 API는 행정동 코드를 리턴하고 있음.
    #
    cnt = 0
    # CSV 라인을 저장할 리스트
    csv_lines = []
    # 파일 번호를 위한 카운터
    file_counter = 1

    for response in cache.responses.values():
        cnt += 1
        content_dict = json.loads(str(response.content, "utf-8"))
        parsed_url = urlparse(response.request.url)
        query_parameters = parse_qs(parsed_url.query)
        query_value = query_parameters.get("query", [None])[0]
        if (not query_value or "documents" not in content_dict or not content_dict["documents"]):
            continue

        old_addr = content_dict["documents"][0]["address"]["address_name"]
        new_addr = (
            content_dict["documents"][0]["road_address"]["address_name"]
            if content_dict["documents"][0]["road_address"]
            else None
        )

        hcode = content_dict["documents"][0]["address"]["h_code"]
        bcode = content_dict["documents"][0]["address"]["b_code"]
        r1 = content_dict["documents"][0]["address"]["region_1depth_name"]
        r2 = content_dict["documents"][0]["address"]["region_2depth_name"]
        r3 = content_dict["documents"][0]["address"]["region_3depth_name"]
        y = content_dict["documents"][0]["address"]["y"]
        x = content_dict["documents"][0]["address"]["x"]
        building_name = (
            content_dict["documents"][0]["road_address"]["building_name"]
            if new_addr
            else None
        )
        sub_building_no = (
            content_dict["documents"][0]["road_address"]["sub_building_no"]
            if new_addr
            else None
        )

        csvline = f'{old_addr},{new_addr},"{building_name}",{sub_building_no},{round(float(y), 5)},{round(float(x), 5)},{hcode},{r1},{r2},{r3},{bcode}\n'.replace(
            '"None"', ""
        ).replace(
            "None", ""
        )

        csv_lines.append(csvline)

        # 리스트가 100개의 라인을 담으면 파일에 저장
        if file_counter == 1:
            with open(f"latilongi_pool.csv", "w", encoding="utf-8") as file:
                file.writelines(
                    "old_addr,new_addr,building_name,sub_building_no,lati,longi,hcode,r1,r2,r3,bcode\n"
                )

        if len(csv_lines) == 100:  # 100
            with open(f"latilongi_pool.csv", "a", encoding="utf-8") as file:
                file.writelines(csv_lines)
            # 파일 카운터 증가 및 리스트 초기화
            file_counter += 1
            csv_lines = []

    # 남은 라인들을 마지막 파일에 저장
    if csv_lines:
        with open(f"latilongi_pool.csv", "a", encoding="utf-8") as file:
            file.writelines(csv_lines)
