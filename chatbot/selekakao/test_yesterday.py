
from datetime import datetime, timedelta
from icecream import ic

def in_yesterday(kakao_date_str,ask_ts_in_sheet):
    ymd = kakao_date_str.split()
    y = int(ymd[0].replace('년', '') if len(ymd) == 3 else 0)
    mi = 1 if len(ymd) == 3 else 0  # 년월일이 아닐 때는 0 년월일 때는 1
    m = int(ymd[mi].replace('월', ''))
    d = int(ymd[mi + 1].replace('일', ''))
    # ymd = kakao_date_str.strptime('%Y-%m-%d %H:%M')
    # y=ymd.year
    # m=ymd.m
    # d=ymd.d
    now = datetime.now()
    given_date = datetime(year=now.year if not y else y, month=m, day=d).date()
    yesterday = now.date() - timedelta(days=1)
    ic(given_date)
    ic(yesterday)
    ic(given_date == yesterday)
    return given_date == yesterday


def is_same_ts(kakao_ts_in_sheet, kakao_ts_from_ui):
    ic(kakao_ts_in_sheet)
    ic(kakao_ts_from_ui)
    return kakao_ts_in_sheet == kakao_ts_from_ui or ('월' in kakao_ts_in_sheet and in_yesterday(kakao_ts_in_sheet))

print(is_same_ts('5월 18일', '오후 9:58'))