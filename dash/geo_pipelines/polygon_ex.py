import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# 폴리곤 영역 표현하기 예제 데이터
df = pd.DataFrame({
    '접근날짜': ['2023-01-01', '2023-01-02', '2023-01-03'],
    '지역구분': ['A', 'B', 'C'],
    '접근목적': ['탐색', '탐색', '방문'],
    'lat': [37.5, 37.6, 37.7],
    'lon': [127, 127.1, 127.2],
    '주소': ['주소1', '주소2', '주소3']
})

app = dash.Dash(__name__)

# ... [중략] ...


@app.callback(
    Output('map', 'figure'),
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('region-dropdown', 'value'),
        Input('purpose-dropdown', 'value')
    ]
)
def update_map(start_date, end_date, regions, purpose):
    # ... [중략] ...

    # 지역별 폴리곤 데이터 생성 (실제로는 이렇게 임의로 생성하지 않고, 실제 지리 데이터를 사용해야 함)
    region_centers = df.groupby('지역구분').mean()
    polygons = {
        region: [
            [lon - 0.05, lat - 0.05],
            [lon + 0.05, lat - 0.05],
            [lon + 0.05, lat + 0.05],
            [lon - 0.05, lat + 0.05],
            [lon - 0.05, lat - 0.05]
        ] for region, (lat, lon) in region_centers.iterrows()
    }

    trace = go.Choroplethmapbox(
        geojson={
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'properties': {'region': region},
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [polygon]
                    }
                } for region, polygon in polygons.items()
            ]
        },
        locations=df['지역구분'],
        z=np.ones(len(df)),
        colorscale=[[0, 'blue'], [1, 'blue']],
        showscale=False,
        marker_opacity=0.5
    )

    # ... [중략] ...

    return {'data': [trace], 'layout': layout}

# ... [중략] ...


#
#
# 반투명한 색상 입히기
#
#

  # ...

    trace = go.Choroplethmapbox(
        geojson={
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'properties': {'region': region},
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [polygon]
                    }
                } for region, polygon in polygons.items()
            ]
        },
        locations=df['지역구분'],
        z=np.ones(len(df)),
        colorscale=[[0, 'rgba(0, 0, 255, 0.5)'], [1, 'rgba(0, 0, 255, 0.5)']],  # 반투명한 파란색 설정
        showscale=False,
        marker_opacity=0.5  # 투명도 설정 (0이 완전 투명, 1이 완전 불투명)
    )

    # ...
