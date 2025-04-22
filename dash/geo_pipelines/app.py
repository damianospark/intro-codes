import datetime
import json
import logging
import os
import re
import warnings

import folium
import geopandas as gpd
import gspread
import pandas as pd
import plotly.graph_objs as go
import pytz
# import dash_bootstrap_components as dbc
import requests
from branca.colormap import StepColormap
from folium import Choropleth, CircleMarker, DivIcon, Marker
from loguru import logger
from oauth2client.service_account import ServiceAccountCredentials
from shapely.errors import ShapelyDeprecationWarning
from shapely.geometry import MultiPolygon, Polygon, mapping, shape
from shapely.ops import orient
from shapely.validation import explain_validity

import dash
from dash import dcc, html
from dash.dependencies import Input, Output

warnings.simplefilter("ignore", category=ShapelyDeprecationWarning)
# Initialize logging
logging.basicConfig(level=logging.INFO)

tz = pytz.timezone('Asia/Seoul')
logger = logger.bind(timezone=tz)
# Read the shapefile
gdf = gpd.read_file("../geo_data/sig.shp", encoding='euc-kr')

# Read the 법정동.tsv file
dong_df = pd.read_csv("../geo_data/법정동.tsv", delimiter='\t', encoding='utf-8')
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

three_word_regions = {
    "경남 창원시", "경북 포항시", "경기 고양시", "경기 안산시", "전북 전주시",
    "충북 청주시", "충남 천안시", "경기 용인시", "경기 안양시", "경기 수원시", "경기 성남시"
}


def extract_region(address):
    # print(address)
    words = address.split()
    if " ".join(words[:2]) in three_word_regions:
        return " ".join(words[:3])
    return " ".join(words[:2])


def append_region_str(dfp, addr_column_name, region_column_name):
    dfp[region_column_name] = dfp[addr_column_name].apply(extract_region)
    dfp[region_column_name] = dfp[region_column_name].apply(lambda x: " ".join([sido_mapping.get(x.split()[0], x.split()[0])] + x.split()[1:]))
    return dfp


def is_valid_ring(ring):
    return len(ring) >= 4


def is_valid_geometry(geom):
    """Check if the geometry is valid and if any LinearRing has at least 4 coordinates."""
    if geom.is_valid:
        if isinstance(geom, Polygon):
            # Check exterior ring
            if len(geom.exterior.coords) < 4:
                return False
            # Check interior rings (holes)
            for interior in geom.interiors:
                if len(interior.coords) < 4:
                    return False
        elif isinstance(geom, MultiPolygon):
            for polygon in geom.geoms:  # <-- Adjusted this line
                if not is_valid_geometry(polygon):
                    return False
        return True
    return False


def clean_polygon(polygon):
    cleaned_coords = remove_duplicate_coordinates(polygon)
    if len(cleaned_coords["coordinates"][0]) < 4:
        return polygon, False
    return {"type": "Polygon", "coordinates": cleaned_coords["coordinates"]}, True


def clean_multi_polygon(multi_polygon):
    valid_rings = []
    for poly in multi_polygon["coordinates"]:
        cleaned_poly, is_valid = clean_polygon({"type": "Polygon", "coordinates": poly})
        if is_valid:
            valid_rings.append(cleaned_poly["coordinates"])
    if not valid_rings:
        return multi_polygon, False
    return {"type": "MultiPolygon", "coordinates": valid_rings}, True


def count_coordinates(geom):
    if geom.type == "Polygon":
        return len(geom.exterior.coords) + sum(len(interior.coords) for interior in geom.interiors)
    elif geom.type == "MultiPolygon":
        return sum(count_coordinates(p) for p in geom.geoms)
    return 0


def remove_consecutive_duplicate_coordinates(coordinates):
    if not coordinates:
        return []
    cleaned = [coordinates[0]]
    for coord in coordinates[1:]:
        if coord != cleaned[-1]:
            cleaned.append(coord)
    # Ensure closure
    if cleaned[0] != cleaned[-1]:
        cleaned.append(cleaned[0])
    return cleaned


def round_coordinates(geojson_data, precision=5):
    """
    Round the coordinates of a GeoJSON geometry to a specified number of decimal places.
    Embeds the removal of consecutive duplicates.
    """
    def round_function(coord):
        return round(coord, precision)

    if geojson_data["type"] == "Polygon":
        original_coordinates = geojson_data["coordinates"]
        rounded_coords = [[tuple(map(round_function, coords)) for coords in ring] for ring in geojson_data["coordinates"]]
        cleaned_coords = [remove_consecutive_duplicate_coordinates(ring) for ring in rounded_coords]
        for ring in cleaned_coords:
            if len(ring) < 4:
                cleaned_coords = original_coordinates
                break
        geojson_data["coordinates"] = cleaned_coords

    elif geojson_data["type"] == "MultiPolygon":
        original_coordinates = geojson_data["coordinates"].copy()
        for polygon_idx, polygon in enumerate(geojson_data["coordinates"]):
            rounded_coords = [[tuple(map(round_function, coords)) for coords in ring] for ring in polygon]
            cleaned_polygon = [remove_consecutive_duplicate_coordinates(ring) for ring in rounded_coords]
            for ring in cleaned_polygon:
                if len(ring) < 4:
                    cleaned_polygon = original_coordinates[polygon_idx]
                    break
            geojson_data["coordinates"][polygon_idx] = cleaned_polygon

    return geojson_data


def create_feature(geojson, region, count):
    """Create a GeoJSON Feature from the given parameters."""
    return {
        "type": "Feature",
        "id": region,  # <-- Add this
        "properties": {
            "region": region,
            "count": count
        },
        "geometry": geojson
    }


def repair_geometry(geojson_data):
    geom = shape(geojson_data)
    repaired_geom = geom.buffer(0)
    return mapping(repaired_geom)


def prepare_dataframe():
    df_vst = prepare_visit_dataframe()
    df_mbr = prepare_member_dataframe()
    all_df = pd.concat([df_vst, df_mbr], axis=0, ignore_index=True, sort=False)

    # df_sbsc = prepare_subsriber_dataframe()
    return all_df


def prepare_visit_dataframe():
    selected_columns = ['Old Address', 'New Address', 'IP', 'Latitude', 'Longitude', 'vst_dt']
    # df = pd.read_csv('./ip2addr_cache_dt.tsv', sep='\t', usecols=selected_columns, nrows=100)
    df_org = pd.read_csv('./ip2addr_cache_dt.tsv', sep='\t', usecols=selected_columns)
    df_org = df_org.dropna(subset=['Old Address'])
    df_org['접근날짜'] = df_org['vst_dt'].str.split(' ').str[0]
    # 날짜 부분만 추출
    # df['접근날짜'] = df['vst_dt'].dt.date
    df_org = append_region_str(df_org, 'Old Address', '지역구분')
    df_org['접근목적'] = '방문'
    df_org = df_org.rename(columns={'Old Address': '주소', 'New Address': '도로주소', 'Latitude': 'lat', 'Longitude': 'lon'})
    return df_org


def prepare_member_dataframe():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    client = gspread.authorize(creds)

    # Open the spreadsheet and select the sheet
    spreadsheet = client.open_by_url(spreadsheet_url)
    worksheet = spreadsheet.worksheet("DB원본")

    # Get the data from the specified columns
    data = worksheet.get_all_values()
    # Convert the data to a Pandas DataFrame
    df_org = pd.DataFrame(data[1:], columns=data[0])

    # Filter the DataFrame to only include the required columns
    df_org = df_org[['billing_address_1', 'ID', 'name', 'gender', 'user_registered_seoul']]
    df_org['접근날짜'] = df_org['user_registered_seoul'].str.split(' ').str[0]

    # Rename the columns
    # df_org.columns = ['주소', 'customer_id', '이름', '성별']
    df_org = df_org.dropna(subset=['billing_address_1'])
    df_org = df_org[df_org['billing_address_1'].str.strip() != '']
    df_org = append_region_str(df_org, 'billing_address_1', '지역구분')
    df_org['접근목적'] = '회원'
    df_org = df_org.rename(columns={'billing_address_1': '주소', 'Latitude': 'lat', 'Longitude': 'lon', 'gender': '성별', 'name': '이름'})

    return df_org


def prepare_subscriber_dataframe():
    return df_org


def adjust_centroid(centroid, font_size, text):
    # These are approximations and may need to be adjusted based on actual rendering
    lon_adjustment_factor = font_size * 0.00005 * len(text)
    lat_adjustment_factor = font_size * 0.00007

    adjusted_lon = centroid.x - lon_adjustment_factor
    adjusted_lat = centroid.y - lat_adjustment_factor

    return adjusted_lat, adjusted_lon


def add_features_to_merged_gdf(merged_gdf):
    centroids = []
    features_list = []
    for _, row in merged_gdf.iterrows():
        if 'SIG_KOR_NM2' not in row:
            continue

        simplified_geometry = row['geometry'].simplify(tolerance=0.001)
        mapped_geojson = mapping(simplified_geometry)
        cleaned_geojson = round_coordinates(mapped_geojson, precision=5)

        if cleaned_geojson is None or len(cleaned_geojson['coordinates']) == 0:
            logging.warning(f"Invalid cleaned geojson for region: {row['SIG_KOR_NM2']}")
            continue

        try:
            geom = shape(cleaned_geojson)
            is_valid_geom = is_valid_geometry(geom)
            if not is_valid_geom:
                cleaned_geojson = repair_geometry(cleaned_geojson)
                geom = shape(cleaned_geojson)
                is_valid_geom = is_valid_geometry(geom)
                if not is_valid_geom:
                    logging.info(f"Invalid geometry for region: {row['SIG_KOR_NM2']}")
                    continue
        except Exception as e:
            logging.error(f"Error processing geometry for region: {row['SIG_KOR_NM2']}. Error: {e}")
            continue
        feature = create_feature(cleaned_geojson, row['SIG_KOR_NM2'], 0)  # Using 0 as count placeholder
        # Append the feature to the features_list

        centroid = geom.centroid
        centroids.append(centroid)
        features_list.append(feature)

    # Add the features_list to the merged_gdf
    merged_gdf['features'] = features_list
    merged_gdf['centroids'] = centroids

    return merged_gdf


def merge_gdf_polygon(df_src):
    # Calculate the count of customers by region
    region_counts = df_src['지역구분'].value_counts().reset_index()
    region_counts.columns = ['지역구분', '고객수']
    # Merge the GeoDataFrame with the carecenters DataFrame
    final_gdf = merged_gdf.merge(region_counts[['지역구분', '고객수']], left_on='SIG_KOR_NM2', right_on='지역구분', how='left')
    # final_gdf.rename(columns={'count': '고객수'}, inplace=True)
    final_gdf = final_gdf.dropna(subset=['고객수']).reset_index()
    # final_gdf = final_gdf.fillna('')
    final_gdf['고객수'] = final_gdf['고객수'].astype(int)
    # final_gdf['geometry'] = final_gdf['geometry'].apply(lambda geom: geom.orient(1))
    final_gdf['geometry'] = final_gdf['geometry'].apply(lambda geom: orient(geom, 1))
    return final_gdf


# 경남 창원시,경부 포항시,경기 고양시, 경기 안산시, 전북 전주시, 충북 전주시, 충남 천안시, 경기 용인시, 경기 안양시, 경기 수원시, 경기 성남시
dong_df = dong_df[dong_df['폐지여부'] != '폐기']
for key, value in sido_mapping.items():
    dong_df['법정동명'] = dong_df['법정동명'].str.replace(key, value)

# Convert SIG_CD to 10 digit 법정동코드
gdf['법정동코드'] = gdf['SIG_CD'].apply(lambda x: int(x.ljust(10, '0')))
merged_gdf = pd.merge(gdf, dong_df, how='left', left_on='법정동코드', right_on='법정동코드')
merged_gdf.rename(columns={'법정동명': 'SIG_KOR_NM2'}, inplace=True)
merged_gdf.set_crs(epsg=5179, inplace=True)  # GRS 80 UTMK
merged_gdf = merged_gdf.to_crs(epsg=4326)  # WGS 84
print("### merged_gdf.head():", merged_gdf.head())
merged_gdf = add_features_to_merged_gdf(merged_gdf)


df = prepare_dataframe()

app = dash.Dash(__name__)
server = app.server
app.layout = html.Div([
    html.Div([  # 이 Div 내부의 컴포넌트들을 가로로 배치합니다.
        dcc.DatePickerRange(
            id="date-picker",
            start_date=df["접근날짜"].min(),
            end_date=df["접근날짜"].max(),
            display_format="YYYY-MM-DD",
            style={"width": "300px", "marginRight": "2px"}
        ),
        dcc.Dropdown(
            id="region-dropdown",
            options=[{"label": region, "value": region} for region in df["지역구분"].unique()],
            value=[],
            multi=True,
            style={"width": "600px", "marginRight": "2px"}
        ),
        dcc.Dropdown(
            id="purpose-dropdown",
            options=[{"label": purpose, "value": purpose} for purpose in df["접근목적"].unique()],
            value=[],
            style={"width": "240px", "marginRight": "2px"}
        ),
        dcc.Checklist(
            id="summary-checkbox",
            options=[{"label": "지역별 요약", "value": "summarize"}],
            value=["summarize"],
            inline=True
        ),
    ], style={"display": "flex", "alignItems": "center", "marginBottom": "1px"}),
    dcc.Graph(id="map", style={"flexGrow": 1, "overflow": "auto"})  # 이 부분에 스타일을 추가했습니다.
], style={"display": "flex", "flexDirection": "column", "height": "100vh"})


@app.server.after_request
def add_header(r):
    r.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '-1'
    return r


traces = []


@app.callback(
    Output('map', 'figure'),
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date'),
        Input('region-dropdown', 'value'),
        Input('purpose-dropdown', 'value'),
        Input('summary-checkbox', 'value')
    ]
)
def update_map(start_date, end_date, regions, purpose, checkbox_state):
    mask = (df['접근날짜'] >= start_date) & (df['접근날짜'] <= end_date)
    print("##### regions : ", regions)
    print("##### checkbox_state : ", checkbox_state)
    if regions and len(regions) > 0:
        mask &= df['지역구분'].isin(regions)

    if purpose:
        mask &= (df['접근목적'] == purpose)

    filtered_df = df[mask]

    mapbox_access_token = ''  # Secure your Mapbox token.
    trace = None
    all_features = []
    regions_list = []
    cust_counts = []
    cust_counts_str = []
    clats = []
    clons = []
    if traces:
        traces.clear()
    if 'summarize' in checkbox_state:
        gdf = merge_gdf_polygon(filtered_df)
        for _, row in gdf.iterrows():
            if '고객수' not in row:
                logging.warning("Column '고객수' missing in current row!")
                continue

            region_name = row['지역구분']
            # merged_gdf에서 해당 지역의 feature 정보를 가져옵니다.
            feature_info = merged_gdf[merged_gdf['SIG_KOR_NM2'] == region_name].iloc[0]['features']

            feature_info['properties']['count'] = row['고객수']  # 고객수 정보를 업데이트 합니다.
            all_features.append(feature_info)
            regions_list.append(row['지역구분'])
            cust_counts.append(row['고객수'])
            cust_counts_str.append(str(row['고객수']))

        # feature_json = json.dumps(feature)
        # print('### feature_json', feature_json)
        # print('### 고객수 ', row['고객수'])
        # print('### 고객수 type ', type(row['고객수']))

            # geom = shape(cleaned_geojson)
            # centroid = geom.centroid
            # # Usage in your callback or loop:
            # centroid_lat, centroid_lon = adjust_centroid(centroid, 13, str(row['고객수']))
            # clats.append(centroid_lat)
            # clons.append(centroid_lon)
            centroid_lat, centroid_lon = adjust_centroid(row['centroids'], 13, str(row['고객수']))
            clats.append(centroid_lat)
            clons.append(centroid_lon)

            # # Create a Scattermapbox trace for the text
            # feature_collection = {
            #     "type": "FeatureCollection",
            #     "features": [feature_info]
            # }
            # feature_collection_json = json.dumps(feature_collection)
            # print('### feature_collection', feature_collection_json)
            # # print('##### ', feature_info['id'])
            # # print('##### ', feature_info)
            # trace = go.Choroplethmapbox(
            #     geojson=feature_collection,
            #     locations=[feature_info['id']],
            #     z=[row['고객수']],
            #     marker_line=dict(color='red', width=1),
            #     colorscale="Viridis",
            #     showscale=False,
            #     marker_opacity=0.2,
            #     text=[row['고객수']]
            # )
            # traces.append(trace)

        feature_collection = {
            "type": "FeatureCollection",
            "features": all_features
        }
        trace = go.Choroplethmapbox(
            geojson=feature_collection,
            locations=regions_list,
            z=cust_counts,
            marker_line=dict(color='red', width=1),
            colorscale="jet",
            showscale=True,
            colorbar=dict(
                x=0.12,
                y=0.95,
                len=0.3,
                thickness=10,
                orientation='h'
            ),
            marker_opacity=0.2,
            text=cust_counts_str
        )
        traces.append(trace)

        text_trace = go.Scattermapbox(
            # lat=[centroid_lat],
            # lon=[centroid_lon],
            lat=clats,
            lon=clons,
            mode='text',
            text=cust_counts_str,  # Displaying the count
            textfont=dict(size=13, color='red'),
            hoverinfo='none',
            showlegend=False
        )
        traces.append(text_trace)

        # break
    else:
        print("##### filtered", filtered_df.shape)
        print(filtered_df.head())
        trace_dots = go.Scattermapbox(
            lon=filtered_df['lon'],
            lat=filtered_df['lat'],
            mode='markers',
            marker=go.scattermapbox.Marker(size=7),
            text=filtered_df['주소'] + '<br>' + filtered_df['접근날짜'],
            # text=filtered_df['주소'] + '<br>' + filtered_df['도로주소'] + '<br>' + filtered_df['접근날짜'],
        )
        traces.append(trace_dots)
        print("### traces", traces)
    layout = go.Layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(lat=37.5, lon=127),
            pitch=0,
            zoom=10,
            style='mapbox://styles/mapbox/light-v11'
            # style='mapbox://styles/mapbox/streets-v12'
            # style='open-street-map'
            # style='carto-positron',
            # style='carto-darkmatter',
            # style='white-bg',
            # style='stamen-watercolor',
            # style='stamen-toner',
            # style='mapbox://styles/mapbox/unicorn-v8'
        ),
        margin=dict(r=2, t=2, l=2, b=2),
    )
    return {'data': traces, 'layout': layout}


if __name__ == '__main__':
    app.run_server(debug=False, port=8090)


# mapbox.streets: mapbox://styles/mapbox/streets-v11
# mapbox.light: mapbox://styles/mapbox/light-v10
# mapbox.dark: mapbox://styles/mapbox/dark-v10
# mapbox.satellite: mapbox://styles/mapbox/satellite-v9
# mapbox.streets-satellite: mapbox://styles/mapbox/satellite-streets-v11
# mapbox.wheatpaste: mapbox://styles/mapbox/wheatpaste-v9
# mapbox.streets-basic: mapbox://styles/mapbox/streets-basic-v9
# mapbox.comic: mapbox://styles/mapbox/comic-v10
# mapbox.outdoors: mapbox://styles/mapbox/outdoors-v11
# mapbox.run-bike-hike: mapbox://styles/mapbox/run-bike-hike-v10
# mapbox.pencil: mapbox://styles/mapbox/pencil-v10
# mapbox.pirates: mapbox://styles/mapbox/pirates-v10
# mapbox.emerald: mapbox://styles/mapbox/emerald-v8
# mapbox.high-contrast: mapbox://styles/mapbox/high-contrast-v10
# open-street-map
# white-bg (plain white background)
# carto-positron
# carto-darkmatter
# stamen-terrain
# stamen-toner
# stamen-watercolor

# colorscale preview
# https://plotly.com/python/builtin-colorscales/
