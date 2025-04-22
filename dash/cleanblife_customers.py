import json
import re
from datetime import datetime
from decimal import Decimal

import gspread
import mysql.connector
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from gspread_formatting import *
from oauth2client.service_account import ServiceAccountCredentials
from plotly.subplots import make_subplots
from sqlalchemy import Float, Integer, String, create_engine, text
from user_agents import parse as ua_parse

# from django.utils.translation import ugettext_lazy as _


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def extract_details(session_token):
    if not isinstance(session_token, (str, bytes)):
        return None
    third_party_pattern = re.compile(
        r'(BizWebView[ ;]|KAKAOTALK.*?|NAVER\(.*?\))')

    pattern_ip = r's:2:"ip";s:\d+:"(.*?)";'
    pattern_ua = r's:2:"ua";s:\d+:"(.*?)";'

    match_ip = re.search(pattern_ip, session_token)
    match_ua = re.search(pattern_ua, session_token)

    if match_ip and match_ua:
        ip_address = match_ip.group(1)
        user_agent_string = match_ua.group(1)
        user_agent = ua_parse(user_agent_string)

        # Extract third-party info
        third_party_info = third_party_pattern.findall(user_agent_string)
        third_party_info_str = ', '.join(
            third_party_info) if third_party_info else None

        # Extract browser version, and supplement with third-party info if empty
        browser_version = user_agent.browser.version_string

        return {
            "IP Address": ip_address,
            "Browser Family": user_agent.browser.family,
            "Browser Version": browser_version or '',
            "OS Family": user_agent.os.family,
            "OS Version": user_agent.os.version_string,
            "Device Family": user_agent.device.family,
            "Third Party Info": third_party_info_str or ''
        }
    return None


scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    './cleanbedding-c9b48eb044cf-service-account-key.json', scope)
client = gspread.authorize(creds)


def format_date_with_korean_dow(date):
    # Day of the week in Korean
    korean_dow = ['월', '화', '수', '목', '금', '토', '일']
    return f"{date.strftime('%m/%d')} {korean_dow[date.weekday()]}"


def fetch_customer_data():
    # PostgreSQL 데이터베이스 연결 설정

    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    print('Postgresql connection open')
    df = pd.read_sql(text("SELECT * FROM da.cust03"), connection)
    # Infinity와 -Infinity 값을 NaN으로 대체
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna("")  # NaN 값을 "NA" 문자열로 대체
    df = df.rename(columns={'old_new': '기존고객'})
    connection.close()
    # df = pd.DataFrame(data_to_insert[1:], columns=data_to_insert[0])
    return df


def plot_customer_eda(df, start_date=None, end_date=None):
    print("start_date", start_date.year, start_date.month, start_date.day)
    # if start_date.year == 2023 and start_date.month < 8:
    #     start_date = start_date.replace(month=7, day=23)
    if df is None:
        df = fetch_customer_data()
        df['user_registered_seoul'] = pd.to_datetime(
            df['user_registered_seoul'])
        df['registration_date'] = df['user_registered_seoul'].dt.date

    # 신규 사이트의 전체 회원 수
    total_new_site_members_today = df.shape[0]

    # 오늘의 신규 회원 가입자 수
    new_members_today = df[df['기존고객'] == '신규'].shape[0]

    # 구 사이트에서 이전한 회원 수
    migrated_members = df[df['기존고객'] == '기존'].shape[0]

    # 'user_registered_seoul'의 날짜만 추출하여 새로운 컬럼에 저장

    # 날짜별로 신규 회원과 구사이트 회원의 가입 수치 계산
    # daily_new = df[df['기존고객'] == '신규'].groupby('registration_date').size()
    # daily_migrated = df[df['기존고객'] == '기존'].groupby('registration_date').size()
    daily_new = df[df['기존고객'] == '신규'].groupby('registration_date').size()
    daily_migrated = df[df['기존고객'] == '기존'].groupby('registration_date').size()

    # 누락된 날짜에 대한 데이터 추가 (0으로 채우기)
    # all_dates = pd.date_range(start=df['registration_date'].min(), end=df['registration_date'].max(), freq='D')
    all_dates = pd.date_range(start=df['registration_date'].min(
    ), end=df['registration_date'].max(), freq='D')
    daily_new = daily_new.reindex(all_dates, fill_value=0)
    daily_migrated = daily_migrated.reindex(all_dates, fill_value=0)

    # 차트 구성 재조정
    fig7 = make_subplots(
        rows=5, cols=5,
        subplot_titles=("최종현황", "기존:신규 회원수", "신규/기존 회원의 구독여부 비교", "구독 비율 파이차트", "최종 구독자수",
                        "일별 누적 신규/기존 회원의 가입수", "일별 신규/기존 가입수(DNU)", "일별 누적 구독자/미구독자수", "일별 신규/기존 구독자수", ""),
        specs=[[{"type": "indicator"}, {"type": "bar"}, {"type": "bar"}, {"type": "pie"}, {"type": "indicator"}],
               [{"colspan": 5}, None, None, None, None],
               [{"colspan": 5}, None, None, None, None],
               [{"colspan": 5}, None, None, None, None],
               [{"colspan": 5}, None, None, None, None]]
    )

    # 1-1. 신규 사이트의 전체 회원 수
    fig7.add_trace(
        go.Indicator(
            mode="number",
            value=total_new_site_members_today,
            title="가입완료 회원"
        ),
        row=1, col=1
    )

    # 1-2. 신규사이트의 신규 회원 가입자 대비 구사이트 회원 수 비교
    # New user
    fig7.add_trace(
        go.Bar(x=['신규'],
               y=[new_members_today],
               text=[new_members_today],
               textposition='auto',
               name='신규회원',
               showlegend=False),
        row=1, col=2
    )

    # Migrated Members
    fig7.add_trace(
        go.Bar(x=['기존'],
               y=[migrated_members],
               text=[migrated_members],
               textposition='auto',
               name='기존회원',
               showlegend=False),
        row=1, col=2
    )

    # df['subscription_count'] = pd.to_numeric(df['subscription_count'], errors='coerce')
    new_subscribed = df[(df['기존고객'] == '신규') & (df['구독상태'] == '구독중')].shape[0]
    migrated_subscribed = df[(df['기존고객'] == '기존') &
                             (df['구독상태'] == '구독중')].shape[0]

    new_non_subscribed = new_members_today - new_subscribed
    migrated_non_subscribed = migrated_members - migrated_subscribed
    fig7.add_trace(
        go.Bar(x=['신규'],
               y=[new_subscribed],
               text=[f'구독<br>{new_subscribed}'],
               textposition='auto',
               name='신규구독',
               showlegend=True),
        row=1, col=3
    )

    fig7.add_trace(
        go.Bar(x=['신규'],
               y=[new_non_subscribed],
               text=[f'미구독<br>{new_non_subscribed}'],
               textposition='auto',
               name='신규미구독',
               showlegend=True),
        row=1, col=3
    )

    fig7.add_trace(
        go.Bar(x=['기존'],
               y=[migrated_subscribed],
               text=[f'구독<br>{migrated_subscribed}'],
               textposition='auto',
               name='기존구독',
               showlegend=True),
        row=1, col=3
    )

    fig7.add_trace(
        go.Bar(x=['기존'],
               y=[migrated_non_subscribed],
               text=[f'미구독<br>{migrated_non_subscribed}'],
               textposition='auto',
               name='기존미구독',
               showlegend=True),
        row=1, col=3
    )

    total_subscribed = df[df['구독상태'] == '구독중'].shape[0]
    total_non_subscribed = df.shape[0] - total_subscribed

    fig7.add_trace(
        go.Pie(labels=['구독', '미구독'],
               values=[total_subscribed, total_non_subscribed],
               hole=0.3,
               textinfo='percent+label+value'),
        row=1, col=4
    )

    # 1-2-1 구독자 수 표현
    # 1. 일자별 구독자 수를 계산
    daily_subscribed = df[df['구독상태'] == '구독중'].groupby(
        'registration_date').size()
    # 2. diff() 함수를 사용하여 각 일자별 구독자 수의 증감을 계산
    daily_subscribed_diff = daily_subscribed.diff().fillna(0)
    # 3. 가장 최근의 값을 가져와서 어제 대비 오늘의 구독자 수의 증감을 구합니다
    subscription_diff = int(daily_subscribed_diff.iloc[-1])
    print(f'subscription_diff:{subscription_diff}')
    print(f'daily_subscribed_diff:{daily_subscribed_diff}')

    # "범례"의 위치에 구독자 수와 어제 대비 증감을 표시
    fig7.add_trace(
        go.Indicator(
            mode="number+delta",
            value=total_subscribed,
            delta={'reference': total_subscribed - subscription_diff,
                   'relative': False, 'valueformat': '.0f'},
            title="구독자 수",
            # domain={'x': [0.6, 0.8], 'y': [0.8, 1]}
        ),
        row=1, col=5
    )

    # df_filtered = df.copy()
    # if start_date and end_date:
    #     df_filtered = df_filtered[(df_filtered['registration_date'] >= start_date) & (df_filtered['registration_date'] <= end_date)]

    # 1-3. 누적 회원 가입 수치 스택바 차트

    # 일누적 가입 수치 계산
    cumulative_new_tmp = daily_new.cumsum()
    cumulative_migrated_tmp = daily_migrated.cumsum()

    # Filter based on the date range
    cumulative_new = cumulative_new_tmp[start_date:end_date]
    cumulative_migrated = cumulative_migrated_tmp[start_date:end_date]

    fig7.add_trace(
        go.Bar(x=cumulative_new.index,
               y=cumulative_new.values,
               name='일누적 신규회원 수',
               text=cumulative_new.values,
               textposition='auto'),
        row=2, col=1
    )

    fig7.add_trace(
        go.Bar(x=cumulative_migrated.index,
               y=cumulative_migrated.values,
               name='일누적 기존회원수 ',
               text=cumulative_migrated.values,
               textposition='auto'),
        row=2, col=1
    )

    # 1-4. 일별 스택바 차트 (누적이 아닌 값)
    daily_new_tmp = df[df['기존고객'] == '신규'].groupby('registration_date').size()
    daily_migrated_tmp = df[df['기존고객'] == '기존'].groupby(
        'registration_date').size()
    # Filter based on the date range
    daily_new = daily_new_tmp[start_date:end_date]
    daily_migrated = daily_migrated_tmp[start_date:end_date]

    fig7.add_trace(
        go.Bar(x=daily_new.index,
               y=daily_new.values,
               name='일별 신규회원 가입',
               text=daily_new.values,
               textposition='auto'),
        row=3, col=1
    )

    fig7.add_trace(
        go.Bar(x=daily_migrated.index,
               y=daily_migrated.values,
               name='일별 기존회원 가입',
               text=daily_migrated.values,
               textposition='auto'),
        row=3, col=1
    )
    # 모든 날짜에 대해 reindexing
    all_dates = pd.date_range(start=df['registration_date'].min(
    ), end=df['registration_date'].max(), freq='D')

    # 1. 일별 구독자 및 미구독자 가입 수 계산
    daily_subscribed = df[df['구독상태'] == '구독중'].groupby(
        'registration_date').size().reindex(all_dates, fill_value=0)
    daily_non_subscribed = df[df['구독상태'] != '구독중'].groupby(
        'registration_date').size().reindex(all_dates, fill_value=0)
    # daily_non_subscribed = daily_new.reindex(all_dates, fill_value=0) - daily_subscribed

    # 2. 일별 누적 가입 수치 계산
    cumulative_subscribed_tmp = daily_subscribed.cumsum()
    cumulative_non_subscribed_tmp = daily_non_subscribed.cumsum()

    # Filter based on the date range
    cumulative_subscribed = cumulative_subscribed_tmp[start_date:end_date]
    cumulative_non_subscribed = cumulative_non_subscribed_tmp[start_date:end_date]
    daily_cumulative_ratio = cumulative_subscribed / \
        (cumulative_non_subscribed + cumulative_subscribed)

    # 3. 그 결과를 바 차트로 추가
    fig7.add_trace(
        go.Bar(x=cumulative_subscribed.index,
               y=cumulative_subscribed.values,
               name='일누적 구독자',
               text=[f'{count}<br> {int((ratio * 100).round(0))}%' for count, ratio in zip(
                   cumulative_subscribed.values, daily_cumulative_ratio.values)],

               textposition='auto'),
        row=4, col=1
    )

    fig7.add_trace(
        go.Bar(x=cumulative_non_subscribed.index,
               y=cumulative_non_subscribed.values,
               name='일누적 미구독자',
               text=cumulative_non_subscribed.values,
               textposition='auto'),
        row=4, col=1
    )

    # 일별 구독자 수 계산
    daily_new_subscribed_tmp = df[(df['기존고객'] == '신규') & (df['구독상태'] == '구독중')].groupby(
        'registration_date').size().reindex(all_dates, fill_value=0)
    daily_migrated_subscribed_tmp = df[(df['기존고객'] == '기존') & (df['구독상태'] == '구독중')].groupby(
        'registration_date').size().reindex(all_dates, fill_value=0)

    # Filter based on the date range
    daily_new_subscribed = daily_new_subscribed_tmp[start_date:end_date]
    daily_migrated_subscribed = daily_migrated_subscribed_tmp[start_date:end_date]

    # 1. 일별 신규 구독자 수 바 차트
    fig7.add_trace(
        go.Bar(x=daily_new_subscribed.index,
               y=daily_new_subscribed.values,
               name='일별 신규 구독자',
               text=daily_new_subscribed.values,
               showlegend=True, legendgroup="group1",
               textposition='auto'),
        row=5, col=1
    )

    # 2. 일별 기존 구독자 수 바 차트
    fig7.add_trace(
        go.Bar(x=daily_migrated_subscribed.index,
               y=daily_migrated_subscribed.values,
               name='일별 기존 구독자',
               text=daily_migrated_subscribed.values,
               textposition='auto'),
        row=5, col=1
    )

    # 범례 위치 조정
    fig7.update_layout(
        title_text="cleanb.life 회원 가입 현황",
        barmode='stack',
        showlegend=False,
        # legend=dict(
        #     x=0.80,
        #     y=1.0,
        #     traceorder="normal",
        #     bgcolor="rgba(255, 255, 255, 0.8)",
        # ),
        height=1800,
        # yaxis=dict(domain=[0.74, 1]),   # Adjust the start and end points of the y-axis for the first row
        # yaxis2=dict(domain=[0.72, 1]),  # Adjust for the second row
        # yaxis3=dict(domain=[0.49, 0.73]),    # Adjust for the third row
        # yaxis4=dict(domain=[0.24, 0.48]),    # Adjust for the third row
        # yaxis5=dict(domain=[0, 0.23])    # Adjust for the third row
    )

    # 불필요한 축 제거
    fig7.update_yaxes(visible=True, showticklabels=True, row=1, col=3)
    fig7.update_xaxes(visible=True, showticklabels=True, row=1, col=3)

    formatted_dates = [format_date_with_korean_dow(
        date) for date in daily_new.index]
    fig7.update_xaxes(tickvals=daily_new.index,
                      ticktext=formatted_dates, row=2, col=1)
    fig7.update_xaxes(tickvals=daily_new.index,
                      ticktext=formatted_dates, row=3, col=1)
    fig7.update_xaxes(tickvals=daily_new.index,
                      ticktext=formatted_dates, row=4, col=1)
    fig7.update_xaxes(tickvals=daily_new.index,
                      ticktext=formatted_dates, row=5, col=1)
    return fig7
