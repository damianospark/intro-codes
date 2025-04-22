# from flask import Flask, render_template, request, redirect, url_for, session
# from dash import Dash
import datetime
import os
import re

import folium
import geopandas as gpd
import gspread
import pandas as pd
import pytz
# import dash_bootstrap_components as dbc
import requests
from branca.colormap import StepColormap
from folium import Choropleth, CircleMarker, DivIcon, Marker
from loguru import logger
from oauth2client.service_account import ServiceAccountCredentials

from dash import dcc, html

tz = pytz.timezone('Asia/Seoul')
logger = logger.bind(timezone=tz)
# Read the shapefile
gdf = gpd.read_file("./geo_data/sig.shp", encoding='euc-kr')

# Read the 법정동.tsv file
dong_df = pd.read_csv("./geo_data/법정동.tsv", delimiter='\t', encoding='utf-8')
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


# Define a custom color palette with pastel tones
color_bins = [0, 5, 10, 20, 50, 100, 200]
# colors = ['#d3d3d3', '#add8e6', '#98fb98', '#f0e68c', '#ffb6c1', '#dda0dd', '#ffa07a']  # , '#ffdead', '#ffefd5']


def map_html_created_today():
    file_path = "./map.html"
    # Check if the file exists
    if os.path.exists(file_path):
        # Get the file creation date
        creation_time = os.path.getctime(file_path)
        creation_date = datetime.datetime.fromtimestamp(creation_time).date()

        # Get today's date
        today = datetime.datetime.today().date()

        # Compare the creation date with today's date
        if creation_date == today:
            print(f"{file_path} was created today.")
            return True
        else:
            print(f"{file_path} was NOT created today.")
            return False
    else:
        print(f"{file_path} does not exist.")
        return False


def plot():
    colors = ['#f7e6ff', '#eeccff', '#e6b3ff', '#d57fff', '#c44cff', '#b319ff']

    color_map = StepColormap(
        colors,
        index=color_bins,
        vmin=min(color_bins),
        vmax=max(color_bins),
        caption='행정 구역별 고객수 '
    )

    def style_function(feature):
        count = feature['properties']['고객수']
        if count == 0:
            return {
                'fillColor': 'none',  # Do not fill the area with color
                'fillOpacity': 0,
                'color': 'blue',
                'weight': 0.7,
            }
        color = color_map(count)
        return {
            'fillColor': color,
            'fillOpacity': 0.75,
            'color': 'blue',
            'weight': 0.6,
        }

    # if not map_html_created_today():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('./cleanbedding-c9b48eb044cf-service-account-key.json', scope)
    client = gspread.authorize(creds)

    # Open the spreadsheet and select the sheet
    spreadsheet = client.open_by_url(spreadsheet_url)
    worksheet = spreadsheet.worksheet("DB원본")

    # Get the data from the specified columns
    data = worksheet.get_all_values()
    # Convert the data to a Pandas DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])

    # Filter the DataFrame to only include the required columns
    df = df[['billing_address_1', 'ID']]

    # Rename the columns
    df.columns = ['address', 'customer_id']
    df = df.dropna(subset=['address'])
    df = df[df['address'].str.strip() != '']

    # Extract the region from the address
    df['시도_군구'] = df['address'].apply(extract_region)

    # Replace the first word based on the mapping
    df['시도_군구'] = df['시도_군구'].apply(lambda x: " ".join([sido_mapping.get(x.split()[0], x.split()[0])] + x.split()[1:]))

    # Calculate the count of customers by region
    region_counts = df['시도_군구'].value_counts().reset_index()
    region_counts.columns = ['시도_군구', '고객수']

    # Display the resulting dataframe
    # print(region_counts)

    # Merge the GeoDataFrame with the carecenters DataFrame
    final_gdf = merged_gdf.merge(region_counts[['시도_군구', '고객수']], left_on='SIG_KOR_NM2', right_on='시도_군구', how='left')
    # final_gdf.rename(columns={'count': '고객수'}, inplace=True)
    final_gdf = final_gdf.dropna(subset=['고객수']).reset_index()
    final_gdf['고객수'] = final_gdf['고객수'].astype(int)

    # print(final_gdf, '\n---------------------\n len(final_gdf):', len(final_gdf))

    # Create a folium map centered around South Korea
    m = folium.Map(location=[36.5, 127.5], zoom_start=9, tiles='CartoDB Positron')
    # colormap definition gnoopy
    m.add_child(color_map)

    geojson = folium.GeoJson(
        final_gdf,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=['시도_군구', '고객수'], aliases=['행정구역', '고객수'])

    )
    geojson.add_to(m)

    # Add labels to the center of each area
    for index, row in final_gdf.iterrows():
        # print('index:', index)
        center = row['geometry'].centroid
        marker = Marker(
            location=(center.y, center.x),
            icon=DivIcon(
                icon_size=(150, 36),
                icon_anchor=(7, 20),
                html=f"<div id='marker{index}' style='font-size: 9pt; font-weight: bold; color: blue;'>{row['고객수']}</div>",
            ),
        )
        marker.add_to(m)

    # Add JavaScript code to adjust the font size based on the zoom level
    js_function = """
    <script>
    function zoomToFontSize(zoom) {
        return Math.round(9 + (zoom - 9) * 2.5) + "pt";
    }

    function updateFontSize() {
        var zoom = myMap.getZoom();
        var fontSize = zoomToFontSize(zoom);
        for (var i = 0; i < """ + str(len(final_gdf)) + """; i++) {
            document.getElementById("marker" + i).style.fontSize = fontSize;
            document.getElementById("marker" + i).style.color = "blue";
        }
    }

    myMap.on("zoomend", updateFontSize);
    </script>
    """
    # Save the map to an HTML file
    m.save('map.html')
    with open('map.html', 'a') as file:
        file.write(js_function)

    with open('map.html', "r") as file:
        map_html = file.read()

    # Find the automatically generated variable name
    match = re.search(r"var (map_[a-z0-9]+) =", map_html)
    if match:
        auto_var_name = match.group(1)
        # Replace the automatically generated variable name with the desired variable name
        map_html = map_html.replace(auto_var_name, "myMap")
        # Save the modified HTML content back to the file
        # Add the JavaScript code to the HTML file
        print("Map saved to 'map.html'. Open this file in a web browser to view the map.")
    return html.Iframe(srcDoc=map_html, width='100%', height='1800')


three_word_regions = {
    "경남 창원시", "경북 포항시", "경기 고양시", "경기 안산시", "전북 전주시",
    "충북 청주시", "충남 천안시", "경기 용인시", "경기 안양시", "경기 수원시", "경기 성남시"
}

# Function to extract region from address


def extract_region(address):
    words = address.split()
    if " ".join(words[:2]) in three_word_regions:
        return " ".join(words[:3])
    return " ".join(words[:2])


def subscription_plot():

    colors = ['#ccccff', '#b3b3ff', '#9999ff', '#7f7fff', '#6666ff', '#4c4cff']

    color_map = StepColormap(
        colors,
        index=color_bins,
        vmin=min(color_bins),
        vmax=max(color_bins),
        caption='행정 구역별 고객수 '
    )

    def style_function2(feature):

        count = feature['properties']['구독고객수']
        if count == 0:
            return {
                'fillColor': 'none',  # Do not fill the area with color
                'fillOpacity': 0,
                'color': 'blue',
                'weight': 0.7,
            }
        color = color_map(count)
        return {
            'fillColor': color,
            'fillOpacity': 0.75,
            'color': 'blue',
            'weight': 0.6,
        }

    # if not map_html_created_today():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('./cleanbedding-c9b48eb044cf-service-account-key.json', scope)
    client = gspread.authorize(creds)

    # Open the spreadsheet and select the sheet
    spreadsheet = client.open_by_url(spreadsheet_url)
    worksheet = spreadsheet.worksheet("DB원본")

    # Get the data from the specified columns
    data = worksheet.get_all_values()
    # Convert the data to a Pandas DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])
    logger.info(f"subscription_plot:df.shape[0]-all : {df.shape[0]}")

    df['is_subscribed'] = df['first_subscription_time'] != ''
    logger.info(f"subscription_plot:df.shape[0]-sub : {df.shape[0]}")

    # Filter the DataFrame to only include the required columns
    df = df[['billing_address_1', 'ID', 'is_subscribed']]

    # Rename the columns
    df.columns = ['address', 'customer_id', 'is_subscribed']
    df = df.dropna(subset=['address'])
    df = df[df['address'].str.strip() != '']

    # Extract the region from the address
    df['시도_군구'] = df['address'].apply(extract_region)
    df['시도_군구'] = df['시도_군구'].apply(lambda x: " ".join([sido_mapping.get(x.split()[0], x.split()[0])] + x.split()[1:]))

    subscribed_df = df[df['is_subscribed']]
    # Calculate the count of subscribed customers by region
    subscribed_region_counts = subscribed_df['시도_군구'].value_counts().reset_index()
    subscribed_region_counts.columns = ['시도_군구', '구독고객수']
    # print(subscribed_region_counts)

    # Filter the DataFrame to only include the required columns
    subscribed_df = df[df['is_subscribed']]
    subscribed_df = subscribed_df[['address', 'customer_id']]

    # Rename the columns
    subscribed_df.columns = ['address', 'customer_id']
    subscribed_df = subscribed_df.dropna(subset=['address'])
    subscribed_df = subscribed_df[subscribed_df['address'].str.strip() != '']

    # Merge the GeoDataFrame with the subscribed_region_counts DataFrame
    final_gdf = merged_gdf.merge(subscribed_region_counts[['시도_군구', '구독고객수']], left_on='SIG_KOR_NM2', right_on='시도_군구', how='left')
    final_gdf = final_gdf.dropna(subset=['구독고객수']).reset_index()
    final_gdf['구독고객수'] = final_gdf['구독고객수'].astype(int)

    # print(final_gdf, '\n---------------------\n len(final_gdf):', len(final_gdf))

    # Create a folium map centered around South Korea
    m = folium.Map(location=[36.5, 127.5], zoom_start=9, tiles='CartoDB Positron')
    # colormap definition gnoopy
    m.add_child(color_map)

    geojson = folium.GeoJson(
        final_gdf,
        style_function=style_function2,
        tooltip=folium.GeoJsonTooltip(fields=['시도_군구', '구독고객수'], aliases=['행정구역', '구독고객수'])
    )
    geojson.add_to(m)

    # Add labels to the center of each area
    for index, row in final_gdf.iterrows():
        # print('index:', index)
        center = row['geometry'].centroid
        marker = Marker(
            location=(center.y, center.x),
            icon=DivIcon(
                icon_size=(150, 36),
                icon_anchor=(7, 20),
                html=f"<div id='marker{index}' style='font-size: 9pt; font-weight: bold; color: blue;'>{row['구독고객수']}</div>",
            ),
        )
        marker.add_to(m)

    # Add JavaScript code to adjust the font size based on the zoom level
    js_function = """
    <script>
    function zoomToFontSize(zoom) {
        return Math.round(9 + (zoom - 9) * 2.5) + "pt";
    }

    function updateFontSize() {
        var zoom = myMap.getZoom();
        var fontSize = zoomToFontSize(zoom);
        for (var i = 0; i < """ + str(len(final_gdf)) + """; i++) {
            document.getElementById("marker" + i).style.fontSize = fontSize;
            document.getElementById("marker" + i).style.color = "blue";
        }
    }

    myMap.on("zoomend", updateFontSize);
    </script>
    """
    # Save the map to an HTML file
    m.save('map.html')
    with open('map.html', 'a') as file:
        file.write(js_function)

# end if map_html_created_today():

    with open('map.html', "r") as file:
        map_html = file.read()
    # Find the automatically generated variable name
    match = re.search(r"var (map_[a-z0-9]+) =", map_html)
    if match:
        auto_var_name = match.group(1)
        # Replace the automatically generated variable name with the desired variable name
        map_html = map_html.replace(auto_var_name, "myMap")
        # Save the modified HTML content back to the file
        # Add the JavaScript code to the HTML file
        print("Map saved to 'map.html'. Open this file in a web browser to view the map.")

    return html.Iframe(srcDoc=map_html, width='100%', height='1800')
