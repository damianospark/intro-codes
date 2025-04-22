import base64
import io


import sqlite3
import json
import requests

import sqlite3
import zlib
import gzip
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


def replace_address_sido(address):
    for key, value in sido_mapping.items():
        address = address.replace(key, value)
    return address.strip()


three_word_regions = {
    "경남 창원시", "경북 포항시", "경기 고양시", "경기 안산시", "전북 전주시",
    "충북 청주시", "충남 천안시", "경기 용인시", "경기 안양시", "경기 수원시", "경기 성남시"
}


def extract_region(address):
    words = address.split()
    if " ".join(words[:2]) in three_word_regions:
        return " ".join(words[:3])
    return " ".join(words[:2])


# def getLatLng(addr):
#     headers = {
#         'Content-Type': 'application/json; charset=utf-8',
#         'Authorization': 'KakaoAK {}'.format('1fe58e9d9c62369f81cdb65f851c7b18')
#     }
#     doc = None
#     rdict = None
#     while True:
#         address = addr.encode("utf-8")
#         p = urllib.parse.urlencode({'query': address})
#     result=requests.get(f"https://localhost:50001/v2/local/geo/transcoord.json?x={x1}&y={y1}&output_coord=WGS84", headers=headers)

#         # result = requests.get(f"http://{os.environ['CACHE_HOST']}:{os.environ['CACHE_PORT']}/v2/local/search/address.json", headers=headers, params=p)
#         rdict = result.json()
#         if 'documents' not in rdict:
#             print('documents is not in the result:', rdict)
#         doc = rdict['documents']
#         # print(len(doc),addr, doc)
#         if len(doc) == 0:
#             addr = addr.rsplit(' ', 1)[0]
#             # print(' retry>', end=' ')
#             address = addr.encode("utf-8")
#             continue
#         break
#     location = rdict['documents'][0]['address']
#     # EPSG:5181 를  WGS84
#     # x1,y1=float(location['x']),float(location['y'])
#     x1, y1 = location['x'], location['y']
#     # result=requests.get(f"https://localhost:50001/v2/local/geo/transcoord.json?x={x1}&y={y1}&output_coord=WGS84", headers=headers)
#     # rdict=result.json()
#     # doc=rdict['documents'][0]
#     # x2,y2=doc['x'],doc['y']
#     return pd.Series({'addr': addr, 'location': [float(y1), float(x1)]})
#     # return row['name'], addr, (float(y2), float(x2))

def getLatLng(addr):
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + addr
    headers = {"Authorization": "KakaoAK 1fe58e9d9c62369f81cdb65f851c7b18"}
    print(requests.get(url, headers=headers).status_code)
    result = json.loads(str(requests.get(url, headers=headers).text))
    print(result)
    match_first = result['documents'][0]['address']
    return float(match_first['y']), float(match_first['x'])
# getLatLng('서울 마포구 모래내로1길 20')

# def getLatLngFromAddr(x):
#     trm_addr=x['주소'].split('(')[0]
#     url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + trm_addr
#     headers = {"Authorization": "KakaoAK 1fe58e9d9c62369f81cdb65f851c7b18"}
#     result=json.loads(str(requests.get(url, headers=headers).text))
#     if len(result['documents']) == 0:
#         print('다음의 주소가 검색되지 않습니다==> ', x['주소'], trm_addr)
#         print(result)
#         x['can_proc']='N'
#     else:
#         match_first = result['documents'][0]['address']
#         x['latitude']= float(match_first['y'])
#         x['longitude']=float(match_first['x'])
#         x['can_proc']='Y'
#     return x


# 데이터베이스에 연결
conn = sqlite3.connect('kakao_cache.sqlite')  # your_database_name.db를 데이터베이스 파일 이름으로 대체하세요.
cursor = conn.cursor()

# "redirects" 테이블의 첫 번째 row의 "value" 필드 값을 선택
cursor.execute("SELECT value FROM responses LIMIT 1;")
value = cursor.fetchone()

# 값이 있으면 출력
if value:
    print(value[0], type(value[0]))
else:
    print("No data found.")


# load content as JSON
json_data = json.loads(value[0])
# get the value of the "_content" key
_content = json_data['_content']
# ic(_content.decode('zlib'))
# decompress gzip-encoded content
# content = zlib.decompress(_content.encode('utf-8'), 16 + zlib.MAX_WBITS)
# content = brotli.decompress(_content.encode('utf-8'))


try:
    decoded_content = base64.b64decode(_content).decode('utf-8')
    print(decoded_content)
except Exception as e:
    print(f"Error decoding: {e}")

# with io.BytesIO(_content.encode('ISO-8859–1')) as f:
#     gzip_file = gzip.GzipFile(fileobj=f)
#     content = gzip_file.read()
# print(conent)


# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()

# # 테이블 이름 출력
# for table in tables:
#     print(table[0])


# 연결 종료
conn.close()
