import datetime
import json
import string
import warnings

import gspread
import ipywidgets as widgets
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objs as go
from gspread_dataframe import set_with_dataframe
from icecream import ic
from IPython.display import clear_output, display
from oauth2client.service_account import ServiceAccountCredentials
from plotly.offline import init_notebook_mode, iplot
from qrytool import (execute_query, insert_dataframe_into_table,
                     load_data_into_dataframe)
from sklearn.cluster import KMeans

warnings.simplefilter(action='ignore')


init_notebook_mode(connected=True)

recency_bounds = None
frequency_bounds = None
monetary_bounds = None
new_customers_only_checkbox = None
exclude_canceled_subscribers_checkbox = None
maratio_input = None
recency_input = None
frequency_input = None
monetary_input = None
df = None
rfm = None


def filter_no_subscr_users(src_df):
    flowmatrix_df = load_data_into_dataframe("SELECT * from flowmatrix")

    # '취소' 및 '복귀' 이벤트에 대한 데이터만 필터링
    events_df = flowmatrix_df[flowmatrix_df["이벤트 타입"].isin(["취소", "복귀"])]

    # 각 all_id별로 마지막 '취소' 및 '복귀' 이벤트의 최신 시점을 찾기
    last_events_df = events_df.sort_values(by=["all_id", "표시일자"]).groupby(["all_id", "이벤트 타입"]).last().reset_index()

    # '취소' 및 '복귀' 이벤트의 최신 시점을 갖는 DataFrame 생성
    last_cancel_df = last_events_df[last_events_df["이벤트 타입"] == "취소"][["all_id", "표시일자"]].rename(columns={"표시일자": "최근취소일"})
    last_return_df = last_events_df[last_events_df["이벤트 타입"] == "복귀"][["all_id", "표시일자"]].rename(columns={"표시일자": "최근복귀일"})

    # '취소'와 '복귀' 이벤트를 all_id로 병합
    merged_df = pd.merge(last_cancel_df, last_return_df, on="all_id", how="left")

    # 마지막 '취소' 이후에 '복귀'가 없는 all_id 찾기
    no_return_users = merged_df[(merged_df["최근복귀일"].isnull()) | (merged_df["최근취소일"] > merged_df["최근복귀일"])]["all_id"].unique()

    # 현재 구독이 유지되는 사용자들의 데이터 필터링
    result_df = src_df[~src_df["all_id"].isin(no_return_users)]
    return result_df


cluster_centers = None


def calculate_MA_grades(df, column='일대여비용'):
    kmeans = KMeans(n_clusters=4).fit(df[[column]])
    # df['MA_Score'] = kmeans.labels_
    cluster_centers = np.round(kmeans.cluster_centers_).astype(int)
    # 클러스터 중심을 정렬
    sorted_centers = np.sort(cluster_centers, axis=0)
    # 경계값 계산: 각 중심점 사이의 중간값
    cluster_boundaries = np.round((sorted_centers[:-1] + sorted_centers[1:]) / 2).astype(int)
    return df, cluster_boundaries


def add_age(src_df):
    global cluster_bounds
    flowmatrix_df = load_data_into_dataframe("SELECT * from flowmatrix")

    # '신규' 및 '취소' 이벤트에 대한 데이터만 필터링
    events_df = flowmatrix_df[flowmatrix_df["이벤트 타입"].isin(["신규", "취소"])]

    # 각 all_id별로 '신규' 및 '취소' 이벤트의 최신 시점을 찾기
    events_df['표시일자'] = pd.to_datetime(events_df['표시일자'])  # 표시일자를 Timestamp로 변환
    new_events = events_df[events_df["이벤트 타입"] == "신규"].groupby("all_id")["표시일자"].min().reset_index(name="최초신규일")
    cancel_events = events_df[events_df["이벤트 타입"] == "취소"].groupby("all_id")["표시일자"].max().reset_index(name="최종취소일")

    # '신규'와 '취소' 이벤트를 all_id로 병합
    age_df = pd.merge(new_events, cancel_events, on="all_id", how="left")

    # 날짜 차이 계산 ('취소' 이벤트가 없는 경우를 고려하여 fillna 사용)
    age_df["Age"] = (age_df["최종취소일"].fillna(pd.Timestamp('today')) - age_df["최초신규일"]).dt.days

    # src_df와 병합
    result_df = pd.merge(src_df, age_df[["all_id", "Age"]], on="all_id", how="left")
    result_df["일대여비용"] = result_df["Monetary"] / (result_df["Age"] + 1)
    result_df, cluster_bounds = calculate_MA_grades(result_df, '일대여비용')
    # result_df['MA등급'] = pd.qcut(result_df['일대여비용'], 4, labels=[4, 3, 2, 1])
    return result_df


def create_quantile_chart(df, column, title, xaxis_title, boundaries):
    # Use user-defined boundaries to create labels
    # boundaries = [float(b.replace(',', '')) for b in boundaries if b and b.strip() != '']
    labels = [f"<= {boundaries[0]}", f"{boundaries[0]} - {boundaries[1]}", f"{boundaries[1]} - {boundaries[2]}", f"> {boundaries[2]}"]
    # df[f"{column}Quartile"] = pd.cut(df[column], bins=[-np.inf] + boundaries + [np.inf], labels=labels)
    # boundaries = [float(b.replace(',', '')) for b in boundaries if b and b.strip()]
    df[f"{column}Quartile"] = pd.cut(df[column].squeeze(), bins=[-np.inf] + boundaries + [np.inf], labels=labels)
    counts = df[f"{column}Quartile"].value_counts().reindex(labels)

    # fig = go.Figure()
    fig = go.FigureWidget()
    for label, count in counts.items():
        fig.add_trace(go.Bar(x=[label], y=[count], name=label, text=[f"{count}명"], textposition='auto'))

    # Calculate the positions for the boundary lines
    positions = range(len(labels) - 1)

    # Add boundary lines and labels
    for i, pos in enumerate(positions):
        boundary_value = boundaries[i]
        # Add boundary lines
        fig.add_vline(x=pos + 0.5, line_dash="dash", line_color="lightgrey")
        # Add labels for boundary values
        annotation_text = ""
        if column == 'Recency':
            annotation_text = f"{boundary_value/7:.1f}주 - {boundary_value/30:.1f}개월"
        elif column == 'Frequency':
            annotation_text = f"{boundary_value:.0f}회"
        else:
            annotation_text = f"{boundary_value:.0f}원"

        fig.add_annotation(
    x=pos + 0.5,
    y=-0.01 * max(counts) * 1.1,
    text=annotation_text,
    showarrow=False,
    font=dict(
        color="blue",
        size=12),
         xshift=-15)

    fig.update_layout(title=title, xaxis_title=xaxis_title, yaxis_title='고객 수', bargap=0.2)
    return fig


# Function to generate and display the charts with user-defined boundaries
def display_charts_with_boundaries(recency_bounds, frequency_bounds, monetary_bounds, maratio_bounds):
    global chart_output, rfm
    fig_maratio = create_quantile_chart(rfm, '일대여비용', '일대여비용 분포 (Menetary/Age) - 사용자 정의 구간 및 고객 수', '일대여비용', maratio_bounds)
    fig_recency = create_quantile_chart(rfm, 'Recency', 'Recency 분포 - 사용자 정의 구간 및 고객 수', 'Recency (일)', recency_bounds)
    fig_frequency = create_quantile_chart(rfm, 'Frequency', 'Frequency 분포 - 사용자 정의 구간 및 고객 수', 'Frequency (횟수)', frequency_bounds)
    fig_monetary = create_quantile_chart(rfm, 'Monetary', 'Monetary 분포 - 사용자 정의 구간 및 고객 수', 'Monetary (금액)', monetary_bounds)

    with chart_output:
        clear_output(wait=True)  # 이전 출력을 명확하게 지우고 시작
        display(fig_maratio)
        display(fig_recency)
        display(fig_frequency)
        display(fig_monetary)


def on_button_clicked(b):
    global recency_bounds, frequency_bounds, monetary_bounds, cluster_bounds, rfm, new_customers_only_checkbox, exclude_canceled_subscribers_checkbox, df, rfm
    filtered_df = None
    # print("버튼 클릭 이벤트 실행")
    # 체크박스 상태에 따라 df 필터링
    if new_customers_only_checkbox.value:
        # filtered_df = df[df['all_id'] > 50000]
        filtered_df = df[df['결제일시'] > '2023-07-01']

    else:
        filtered_df = df
    # print(df.shape)
    # print(filtered_df.shape)
    # "구독취소고객 제외" 체크박스에 대한 처리는 여기에 구현할 수 있습니다.
    if exclude_canceled_subscribers_checkbox.value:
        filtered_df = filter_no_subscr_users(filtered_df)
        # pass  # 여기에 구독 취소 고객을 제외하는 로직을 추가할 수 있습니다.

    # 필터링된 데이터프레임을 사용하여 RFM 메트릭 계산
    NOW = datetime.datetime.now()
    rfm = filtered_df.groupby('all_id').agg({
        '결제일시': lambda x: (NOW - x.max()).days,
        '주문id': 'count',
        '결제액': 'sum'
    }).rename(columns={'결제일시': 'Recency', '주문id': 'Frequency', '결제액': 'Monetary'})
    # print(rfm.shape)
    rfm = add_age(rfm)
    # print(rfm.shape)

    # Convert input values to integers and sort them
    maratio_bounds = sorted(list(map(int, maratio_input.value.split(','))))
    recency_bounds = sorted([int(x) for x in recency_input.value.split(',')])
    frequency_bounds = sorted([int(x) for x in frequency_input.value.split(',')])
    monetary_bounds = sorted([int(x) for x in monetary_input.value.split(',')])

    # Generate and display new charts
    display_charts_with_boundaries(recency_bounds, frequency_bounds, monetary_bounds, maratio_bounds)


def calculate_rfm():
    global new_customers_only_checkbox, exclude_canceled_subscribers_checkbox, df, maratio_input, recency_input, frequency_input, monetary_input, chart_output, rfm
    qry = """
        SELECT all_id, 주문id,결제일시::date,MAX(세후순결제금액) as 결제액
    FROM salesmatrix
    WHERE all_id IS NOT NULL AND 결제일시::date >= TO_DATE('2018-01-01', 'YYYY-MM-DD') AND 정산='합산' AND cb주문종류!='상품주문'
    GROUP BY all_id,주문id,결제일시::date;
        """
    df = load_data_into_dataframe(qry)

    # Convert '결제일시' to datetime
    df['결제일시'] = pd.to_datetime(df['결제일시'])

    # Calculate RFM metrics
    NOW = datetime.datetime.now()
    rfm = df.groupby('all_id').agg({
        '결제일시': lambda x: (NOW - x.max()).days,
        '주문id': 'count',
        '결제액': 'sum'
    }).rename(columns={'결제일시': 'Recency', '주문id': 'Frequency', '결제액': 'Monetary'})
    rfm = add_age(rfm)

    # Placeholder for the checkboxes' state
    new_customers_only_checkbox = widgets.Checkbox(value=True, description='신규 고객만')
    exclude_canceled_subscribers_checkbox = widgets.Checkbox(value=True, description='구독취소고객 제외')

    # Create input widgets
    cluster_bounds_str = ', '.join(map(str, cluster_bounds.flatten()))
    maratio_input = widgets.Text(value=cluster_bounds_str, description='일대여비용')
    recency_input = widgets.Text(value='30,90,180', description='Recency:')
    frequency_input = widgets.Text(value='1,5,10', description='Frequency:')
    monetary_input = widgets.Text(value='10000,50000,100000', description='Monetary:')

    chart_output = widgets.Output()

    button = widgets.Button(description="Generate Charts")
    button.on_click(on_button_clicked)

    # Display widgets and the placeholder output for charts
    display(widgets.VBox([new_customers_only_checkbox, exclude_canceled_subscribers_checkbox,
            recency_input, frequency_input, monetary_input, maratio_input, button]))
    display(chart_output)


def show_ma_distribution(ht=1200, cost_limit=50000):
    global rfm, new_customers_only_checkbox, exclude_canceled_subscribers_checkbox

    # def filter_options(src_df):
    #     global rfm, new_customers_only_checkbox, exclude_canceled_subscribers_checkbox
    #     if new_customers_only_checkbox.value:
    #         filtered_df = src_df[src_df['결제일시'] > '2023-07-01']
    #     else:
    #         filtered_df = src_df
    #     if exclude_canceled_subscribers_checkbox.value:
    #         filtered_df = filter_no_subscr_users(filtered_df)
    #     return filtered_df

    filtered_df = rfm
    # KMeans 클러스터링을 사용하여 4개의 그룹 생성
    kmeans = KMeans(n_clusters=4).fit(filtered_df[['일대여비용']])
    filtered_df['Cluster'] = kmeans.labels_

    # 각 그룹의 중심 계산
    centers = kmeans.cluster_centers_

    # 스캐터 차트 생성
    fig = go.Figure()

    # 각 클러스터에 대한 스캐터 플롯 추가
    for i in range(4):
        cluster_data = filtered_df[filtered_df['Cluster'] == i]
        fig.add_trace(go.Scatter(y=cluster_data.index, x=cluster_data['일대여비용'], mode='markers'))

    # 각 그룹의 중심에 붉은 세로선 추가
    for i, center in enumerate(centers):
        fig.add_shape(
            type='line',
            x0=center[0],
            x1=center[0],
            y0=0,
            y1=1,
            yref='paper',
            line=dict(
                color='Red',
                width=1
            )
        )
        # ic(i, center)
        fig.add_annotation(
            x=center[0],
            y=0 + (i * 0.01),
            xref="x",
            yref="paper",
            text=f"{int(center[0]):,}원",
            showarrow=False,
            font=dict(
                size=9,
                color="Red"
            ),
        )
    # 축의 타이틀 추가
    fig.update_layout(
        height=ht,  # 차트의 높이를 1200px로 설정
        xaxis_title="일대여비용 (단위: 원)",
        yaxis_title="고객 번호",
        hovermode="x unified",  # x축 값에 따라 호버 정보 표시
        xaxis=dict(tickformat=',d'),  # x축의 수치를 정수 형태로 표시
        yaxis=dict(tickformat=',d')   # y축의 수치를 정수 형태로 표시

    )
    fig.show()

    filtered_df = filtered_df[filtered_df['일대여비용'] <= cost_limit]
    # KMeans 클러스터링을 사용하여 4개의 그룹 생성
    kmeans = KMeans(n_clusters=4).fit(filtered_df[['일대여비용']])
    filtered_df['Cluster'] = kmeans.labels_

    # 각 그룹의 중심 계산
    centers = kmeans.cluster_centers_

    # 스캐터 차트 생성
    fig = go.Figure()

    # 각 클러스터에 대한 스캐터 플롯 추가
    for i in range(4):
        cluster_data = filtered_df[filtered_df['Cluster'] == i]
        fig.add_trace(go.Scatter(y=cluster_data.index, x=cluster_data['일대여비용'], mode='markers'))

    # 각 그룹의 중심에 붉은 세로선 추가
    for i, center in enumerate(centers):
        fig.add_shape(
            type='line',
            x0=center[0],
            x1=center[0],
            y0=0,
            y1=1,
            yref='paper',
            line=dict(
                color='Red',
                width=1
            )
        )
        # ic(i, center)
        fig.add_annotation(
            x=center[0],
            y=0 + (i * 0.01),
            xref="x",
            yref="paper",
            text=f"{int(center[0]):,}원",
            showarrow=False,
            font=dict(
                size=9,
                color="Red"
            ),
        )
    # 축의 타이틀 추가
    fig.update_layout(
        height=ht,  # 차트의 높이를 1200px로 설정
        xaxis_title="일대여비용 (단위: 원)",
        yaxis_title="고객 번호",
        hovermode="x unified",  # x축 값에 따라 호버 정보 표시
        xaxis=dict(tickformat=',d'),  # x축의 수치를 정수 형태로 표시
        yaxis=dict(tickformat=',d')   # y축의 수치를 정수 형태로 표시

    )
    fig.show()


rfm_level_colors = {
    '1등급(Green)': 'green',
    '2등급(Blue)': 'blue',
    '3등급(Orange)': 'orange',
    '4등급(Red)': 'red'
}


def assign_ma_level(df):
    if df['MA_Score'] > 3:
        return '1등급(Green)'
    elif df['MA_Score'] > 2:
        return '2등급(Blue)'
    elif df['MA_Score'] > 1:
        return '3등급(Orange)'
    else:
        return '4등급(Red)'


def ma_score(x):
    global cluster_bounds
    if x <= cluster_bounds[0]:
        return 1
    elif x <= cluster_bounds[1]:
        return 2
    elif x <= cluster_bounds[2]:
        return 3
    else:
        return 4


def show_ma_grade():
    global rfm, cluster_bounds
    # 점수 부여
    rfm['MA_Score'] = rfm['일대여비용'].apply(ma_score)
    rfm['MA_Level'] = rfm.apply(assign_ma_level, axis=1)

    rfm_level_summary = rfm['MA_Level'].value_counts().sort_index()
    # 전체 고객 수 계산
    total_customers = rfm_level_summary.sum()
    rfm_level_counts = rfm['MA_Level'].value_counts().sort_index()
    rfm_level_percent = (rfm_level_counts / total_customers * 100).round(2)
    # 요약된 데이터 프레임 생성
    summary_df = pd.DataFrame({
        'Count': rfm_level_counts,
        'Percent': rfm_level_percent
    })

    # 요약된 데이터 프린트
    print("MA 등급별 요약:")
    print(summary_df)

    # 바 차트 생성
    fig = go.Figure()
    for level in rfm_level_counts.index:
        count = rfm_level_counts[level]
        percent = rfm_level_percent[level]
        fig.add_trace(go.Bar(
            x=[level],
            y=[count],
            name=level,
            marker_color=rfm_level_colors[level],  # 색상 적용
            text=f"{count}명 ({percent}%)",  # 총 고객 수 및 퍼센트 표시
            textposition='outside'  # 텍스트 위치
        ))
    # 차트 레이아웃 설정
    fig.update_layout(
        title='MA등급별 고객 수',
        xaxis=dict(title='MA등급'),
        yaxis=dict(title='고객 수'),
        bargap=0.2,
        yaxis_range=[0, max(rfm_level_counts) * 1.2]

    )

    fig.show()


def gen_rfm_level():
    global rfm, rfm_level_counts, rfm_level_percent, rfm_level_colors

    def assign_rfm_level(df):
        if df['RFM_Score'] > 3:
            return '1등급(Green)'
        elif df['RFM_Score'] > 2:
            return '2등급(Blue)'
        elif df['RFM_Score'] > 1:
            return '3등급(Orange)'
        else:
            return '4등급(Red)'

    rfm_level_colors = {
        '1등급(Green)': 'green',
        '2등급(Blue)': 'blue',
        '3등급(Orange)': 'orange',
        '4등급(Red)': 'red'
    }

    # R, F, M 각 요소별 점수 구간 표 생성에 사용자 정의 경계값 반영
    def r_score(x):
        global recency_bounds, frequency_bounds, monetary_bounds
        if x > recency_bounds[2]:
            return 1
        elif x > recency_bounds[1]:
            return 2
        elif x > recency_bounds[0]:
            return 3
        else:
            return 4

    def fm_score(x, bounds):
        if x <= bounds[0]:
            return 1
        elif x <= bounds[1]:
            return 2
        elif x <= bounds[2]:
            return 3
        else:
            return 4

    # 점수 부여
    rfm['R_Score'] = rfm['Recency'].apply(r_score)
    rfm['F_Score'] = rfm['Frequency'].apply(fm_score, args=(frequency_bounds,))
    rfm['M_Score'] = rfm['Monetary'].apply(fm_score, args=(monetary_bounds,))

    # 종합 RFM 점수 계산
    rfm['RFM_Score'] = rfm[['R_Score', 'F_Score', 'M_Score']].mean(axis=1)

    # 점수에 따른 고객 등급 분류
    rfm['RFM_Level'] = rfm.apply(assign_rfm_level, axis=1)
    # all_id를 인덱스에서 컬럼으로 변환
    rfm = rfm.reset_index()

    # all_id 컬럼의 데이터 타입을 정수형으로 변환
    rfm['all_id'] = rfm['all_id'].astype(int)

    # display(rfm)

    # RFM_Level 별로 고객 수 계산
    rfm_level_summary = rfm['RFM_Level'].value_counts().sort_index()

    # 전체 고객 수 계산
    total_customers = rfm_level_summary.sum()
    # RFM_Level 별 고객 수 및 퍼센트 계산
    rfm_level_counts = rfm['RFM_Level'].value_counts().sort_index()
    rfm_level_percent = (rfm_level_counts / total_customers * 100).round(2)

    # 요약된 데이터 프레임 생성
    summary_df = pd.DataFrame({
        'Count': rfm_level_counts,
        'Percent': rfm_level_percent
    })

    # 요약된 데이터 프린트
    print("RFM 등급별 요약:")
    print(summary_df)
    # RFM_Level 별 고객 수 계산
    rfm_level_counts = rfm['RFM_Level'].value_counts().sort_index()


def show_rfm_grade():
    global rfm_level_counts, rfm_level_percent, rfm_level_colors

    # 바 차트 생성
    fig = go.Figure()

    # RFM_Level 별로 반복하여 바 추가 및 텍스트 설정
    for level in rfm_level_counts.index:
        count = rfm_level_counts[level]
        percent = rfm_level_percent[level]
        fig.add_trace(go.Bar(
            x=[level],
            y=[count],
            name=level,
            marker_color=rfm_level_colors[level],  # 색상 적용
            text=f"{count}명 ({percent}%)",  # 총 고객 수 및 퍼센트 표시
            textposition='outside'  # 텍스트 위치
        ))

    # 차트 레이아웃 설정
    fig.update_layout(
        title='RFM 등급별 고객 수',
        xaxis=dict(title='RFM 등급'),
        yaxis=dict(title='고객 수'),
        bargap=0.2,
        yaxis_range=[0, max(rfm_level_counts) * 1.2]

    )

    fig.show()


def colnum_string(n):
    alphabet = string.ascii_uppercase
    strng = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        strng = alphabet[remainder] + strng
    return strng


def update_google_spread():
    global rfm
    customatrix_df = load_data_into_dataframe("SELECT * from customatrix")
    # rfm 데이터프레임에서 특정 컬럼 제외
    rfm_reduced_df = rfm.drop(columns=["RecencyQuartile", "FrequencyQuartile", "MonetaryQuartile"])
    # rfm_reduced_df와 customatrix_df를 all_id 기준으로 조인
    rfm_customatrix_joined = pd.merge(rfm_reduced_df, customatrix_df, on="all_id")

    df = rfm_customatrix_joined

    # 컬럼 순서 재배치: 'RFM_Level', '이름(Name)', '결제전화(Payment Phone)'을 'all_id' 바로 다음에 배치
    # 먼저 모든 컬럼 목록을 가져온 후, 해당 컬럼들을 제거합니다.
    columns = list(df.columns)
    columns_to_relocate = ['RFM_Level', '이름', '결제전화']  # 실제 컬럼 이름으로 대체 필요
    for column in columns_to_relocate:
        if column in columns:
            columns.remove(column)

    # 'all_id' 컬럼 인덱스를 찾습니다.
    all_id_index = columns.index('all_id')

    # 'all_id' 바로 다음 위치에 위에서 제거한 컬럼들을 순서대로 삽입
    for column in reversed(columns_to_relocate):
        columns.insert(all_id_index + 1, column)

    # 재배치된 컬럼 순서로 데이터프레임을 재구성
    df = df[columns]

    # Function to convert column number to column letter


    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        './cleanbedding-c9b48eb044cf-service-account-key.json', scope)

    client = gspread.authorize(creds)

    # Open the spreadsheet and select the sheet
    spreadsheet = client.open_by_url(spreadsheet_url)
    worksheet = spreadsheet.worksheet("노트북실행결과")

    # Clear the existing data in the worksheet
    worksheet.clear()

    # Update the worksheet with the DataFrame
    set_with_dataframe(worksheet, df)

    # Get the number of columns in the DataFrame
    num_cols = len(df.columns)
    num_rows = len(df)
    # Dynamically create the range for the header based on the number of columns
    header_range = f"A1:{colnum_string(num_cols)}1"

    # Apply formatting to the header range
    worksheet.format(header_range, {'textFormat': {'bold': True}, 'backgroundColor': {
        'red': 0.9, 'green': 0.9, 'blue': 0.9}})

    # Here's how you can freeze the first row i.e., the header row such that it is always visible
    worksheet.freeze(rows=1)

    worksheet_id = worksheet._properties['sheetId']
    requests = [{
        "setBasicFilter": {
            "filter": {
                "range": {
                    "sheetId": worksheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": num_rows + 1
                }
            }
        }
    }]
    batch_update_spreadsheet_request_body = {
        'requests': requests
    }
    response = spreadsheet.batch_update(batch_update_spreadsheet_request_body)

    print(f'DataFrame uploaded to Google Spreadsheet with {len(df)} rows.')


def copy_db_to_google_spread(sql_query, sheet_name):
    df = load_data_into_dataframe(sql_query)

    # Use creds to create a client to interact with the Google Drive API
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        './cleanbedding-c9b48eb044cf-service-account-key.json', scope)
    client = gspread.authorize(creds)

    # Open the spreadsheet
    spreadsheet = client.open_by_url(spreadsheet_url)

    # Try to get the worksheet with the given name
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        # If the worksheet does not exist, create a new one
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")

    # Clear the existing data in the worksheet
    worksheet.clear()

    # Update the worksheet with the DataFrame
    set_with_dataframe(worksheet, df)

    # Get the number of columns in the DataFrame
    num_cols = len(df.columns)
    num_rows = len(df)
    # Dynamically create the range for the header based on the number of columns
    header_range = f"A1:{colnum_string(num_cols)}1"

    # Apply formatting to the header range
    worksheet.format(header_range, {'textFormat': {'bold': True}, 'backgroundColor': {
        'red': 0.9, 'green': 0.9, 'blue': 0.9}})

    # Here's how you can freeze the first row i.e., the header row such that it is always visible
    worksheet.freeze(rows=1)

    worksheet_id = worksheet._properties['sheetId']
    requests = [{
        "setBasicFilter": {
            "filter": {
                "range": {
                    "sheetId": worksheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": num_rows + 1
                }
            }
        }
    }]
    batch_update_spreadsheet_request_body = {
        'requests': requests
    }
    response = spreadsheet.batch_update(batch_update_spreadsheet_request_body)

    display(f'DataFrame uploaded to Google Spreadsheet with {len(df)} rows.')
    worksheet_link = f'{spreadsheet_url}#gid={worksheet.id}'
    return worksheet_link
