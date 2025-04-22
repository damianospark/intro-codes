from datetime import datetime, timedelta

import pandas as pd
from pytz import timezone
from sqlalchemy import create_engine

# TSV 파일 읽기
df_org = pd.read_csv('./ip2addr_cache.tsv', sep='\t')


# MySQL connection details
connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
engine = create_engine(connection_string)
# Fetch distinct IPs from the database
query = """
SELECT
    ip,
    DATE_FORMAT(  MIN(CONVERT_TZ(FROM_UNIXTIME(dt), '+00:00', '-09:00')), '%%Y-%%m-%%d %%H:%%i:%%s') AS vst_dt
FROM
    wp_slim_stats
GROUP BY ip;
"""
wp_slim_stats = pd.read_sql(query, engine)


# 'dt' 컬럼의 UNIX Timestamp 값을 datetime 객체로 변환하고 시간대를 변환
# wp_slim_stats['vst_dt'] = pd.to_datetime(wp_slim_stats['vst_dt'], unit='s')
# wp_slim_stats['dt'] = wp_slim_stats['dt'].dt.tz_localize('UTC').dt.tz_convert(timezone('Etc/GMT+9'))

# IP별로 가장 빠른 방문 일자를 구함
min_dates = wp_slim_stats.groupby('ip')['vst_dt'].min().reset_index()

# 컬럼 이름 변경
min_dates.columns = ['IP', 'vst_dt']

# df_org와 min_dates를 IP 기준으로 조인하여 vst_dt 컬럼을 추가
df_org = pd.merge(df_org, wp_slim_stats, left_on='IP', right_on='ip', how='left').drop(columns='ip')

# 결과 DataFrame을 ip2addr_cache_dt.tsv 파일로 저장
df_org.to_csv('ip2addr_cache_dt.tsv', sep='\t', index=False)
