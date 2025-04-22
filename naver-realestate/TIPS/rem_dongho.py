from qrytool import load_data_into_dataframe, insert_dataframe_into_table
import pandas as pd
import re

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.max_colwidth", None)


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
            # print(
            #     f"{ match.group(1)} | {group2}|{group3}|{group4}|{group5}|{group6}|"
            # )
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
            print("No match :" + address)
            ret1 = address
            ret2 = None
    return ret1, ret2


addresses_df = load_data_into_dataframe(
    """
SELECT all_id, 회원주소, 회원lati, 회원longi
FROM customatrix
WHERE 가입일시::date < '2024-06-03' AND 회원주소 IS NOT NULL AND 회원lati IS NOT NULL AND 회원longi IS NOT NULL
"""
)
for index, row in addresses_df.iterrows():
    addr1, addr2 = split_address(row["회원주소"])
    addresses_df.at[index, '회원주소1'] = addr1
    addresses_df.at[index, '회원주소2'] = addr2

# print(addresses_df.head())
patterns = [
    r'([\dA-Za-z]+동)\s*(\w+[호]{0,1})\s*$',
    r'\)\s*(\w+호)\s*$',
    r'\)\s*[가-힣A-Za-z\.\,]+(\w+호)\s*$',
    r'\s*(\d+호)\s*$',
    r'\)\s*(\w+)\s*[-ㅡ]\s*(\w+호*)\s*$'
]
cnt = 0
for index, row in addresses_df.iterrows():
    cnt += 1
    dong = ""
    ho = ""
    temp_addr2 = ""
    for idx, pattern in enumerate(patterns):
        if not row["회원주소2"] or row["회원주소2"].strip() == "":
            continue
        # print(row['회원주소2'])
        match = re.search(pattern, row["회원주소2"])
        if match:
            if len(match.groups()) == 1:
                ho = match.group(1)  # 호만 추출될 경우
                temp_addr2 = row["회원주소2"].replace(ho, '')
                if '호' not in ho:
                    ho = ho + '호'
            elif len(match.groups()) >= 2:
                dong = match.group(1)  # 동 추출
                if '빌리브파비오더까사오피스텔' in row["회원주소2"]:
                    print('dong => ' + dong)
                ho = match.group(2)  # 호 추출
                if '호' not in ho:
                    ho = ho + '호'
                if '동' not in dong:
                    dong = dong + '동'
                row["회원주소2"] = row["회원주소2"].replace(ho, '')
                temp_addr2 = row["회원주소2"].replace(dong, '')
                if idx == 3:
                    temp_addr2 = temp_addr2.replace('-', '')
            break
    temp_addr2 = temp_addr2.strip()

    addresses_df.at[index, "동"] = dong
    addresses_df.at[index, "호"] = ho
    addresses_df.at[index, "회원주소_reduced"] = temp_addr2
    # print(cnt)
    # if cnt >= 10:
    #     break
# addresses_df.head(10).to_csv("marked_동호_건물명후보.tsv", sep="\t", index=False)
addresses_df.to_csv("marked_동호_건물명후보.tsv", sep="\t", index=False)
