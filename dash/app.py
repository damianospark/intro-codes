"""
This app creates an animated sidebar using the dbc.Nav component and some local
CSS. Each menu item has an icon, when the sidebar is collapsed the labels
disappear and only the icons remain. Visit www.fontawesome.com to find
alternative icons to suit your needs!

dcc.Location is used to track the current location, a callback uses the current
location to render the appropriate page content. The active prop of each
NavLink is set automatically according to the current pathname. To use this
feature you must install dash-bootstrap-components >= 0.11.0.

For more details on building multi-page Dash applications, check out the Dash
documentation: https://dash.plot.ly/urls
"""
import csv
import io
import json
import logging
import os
import sys
import time
import warnings
from datetime import date, datetime, timedelta
from functools import wraps

import clbe_conv
import cleanblife_customers
import dash_auth
import dash_bootstrap_components as dbc
import geo_analytics
import gspread
import health_metrics
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objs as go
import pytz
import requests
import sales_analytics
from cleanblife_sales import fetch_cleanb_data
from dateutil.parser import parse
from flask import Flask, redirect, render_template, request, session, url_for
from flask.logging import default_handler
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (DateRange, Dimension, Metric,
                                                RunReportRequest,
                                                analytics_data_api)
from icecream import ic
from logdecorator import log_on_end, log_on_error, log_on_start
from loguru import logger
from oauth2client.service_account import ServiceAccountCredentials
from plotly.subplots import make_subplots
from qrytool import (execute_query, insert_dataframe_into_table,
                     load_data_into_dataframe)

import dash
# from dash import Input, Output, dcc, html
from dash import dcc, html
from dash.dependencies import Input, Output, State

warnings.simplefilter("ignore")

tz = pytz.timezone('Asia/Seoul')
logger = logger.bind(timezone=tz)

# Set the value of an environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './cleanbedding-c9b48eb044cf-service-account-key.json'
"""Google Analytics Data API sample quickstart application.
This application demonstrates the usage of the Analytics Data API using
service account credentials.
Before you start the application, please review the comments starting with
"TODO(developer)" and update the code to use correct values.
Usage:
  pip3 install --upgrade google-analytics-data
  python3 quickstart.py
"""
# [START analyticsdata_quickstart]

# old_order_df = None
# new_order_df = None


def get_old_df():  # get_order_df
    # use credentials to create a client to interact with the Google Drive API
    # scope = ['https://www.googleapis.com/auth/drive']
    # creds = ServiceAccountCredentials.from_json_keyfile_name(
    #     './cleanbedding-c9b48eb044cf-service-account-key.json', scope)
    # client = gspread.authorize(creds)

    # # open the Google Sheet by its title
    # # sheet = client.open('Analysis').worksheet("Orders(All)")
    # sheet = client.open_by_url(
    # # get all the data in the sheet
    # all_values = sheet.get_all_values()
    # data = [row[:55] for row in all_values[5:]]
    # # convert the data to a Pandas DataFrame
    # df = pd.DataFrame(data[1:], columns=data[0])
    qry = """
        SELECT
            c.id,c.생년월일 as 연령,s.*
        FROM sales_sx01 s
        LEFT JOIN
            cust_old c ON s.cust_id = c.id;
    """

    df = load_data_into_dataframe(qry)
    # df['연령'] = (datetime.now() - df['생년월일']).dt.days // 365

    # df = df[df['Validity'] == '배송지역']
    df = df[df['주문_일자'].notna()]
    # df['주문일자'] = df[df['주문_일자'].astype(bool)]
    df['주문_일자'] = pd.to_datetime(df['주문_일자'], format='%Y-%m-%d %H:%M:%S')
    # df['주문_일자'] = df['주문_일자'].apply(lambda x: parse(x).strftime('%Y-%m-%d'))

    # df=df[df['주문_일자']>'2020-10-11']
    # Sort the DataFrame by the '주문_일자' column in ascending order
    df.sort_values('주문_일자', inplace=True)
    df = df[df['주문_일자'] >= '2021-01-01']
    df = df[~df['주문_상태'].str.contains('취소')]
    df = df.rename(columns={'주문_일자': '결제일시', '결제_일자': '결제일시', '결제_금액': '결제금액'})
    # TODO: 주문자 이름+전화번호뒤4자리+배송지우편번호 로 신/구 고객 합집합 테이블 필요 여기서 가져온 카를 주문자 이메일 대신 사용!!
    return df


def get_order_df():
    old_df = get_old_df()
    old_df['source'] = 'old'  # Adding 'data source' column for old_df

    # Fetch data from MySQL
    new_df = fetch_cleanb_data()
    new_df['source'] = 'new'  # Adding 'data source' column for new_df
    logger.info('get in -------------------------------')
    logger.info(new_df)

    # Concatenate both dataframes along rows
    merged_df = pd.concat([old_df, new_df], ignore_index=True)
    logger.info('merged_df: \n' + merged_df.head().to_string())

    return merged_df


def to_csv(report_response, prop_id):
    original_list = [
        dimension.name for dimension in report_response.dimension_headers]
    new_list = [metric.name for metric in report_response.metric_headers]
    index = -3
    # Get the header names from the report metadata
    header = original_list[:index + 1] + new_list + original_list[index + 1:]

    # Get the data rows from the report data
    rows = []
    for row in report_response.rows:
        original_list = [dimension.value for dimension in row.dimension_values]
        new_list = [metric.value for metric in row.metric_values]
        index = -3
        row_values = original_list[:index + 1] + \
            new_list + original_list[index + 1:]
        rows.append(row_values)

    # Write the CSV file
    with open(f'{prop_id}_cmp_report.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(rows)


def to_df(report_response, prop_id):
    to_csv(report_response, prop_id)
    df = pd.read_csv(f'./{prop_id}_cmp_report.csv')
    dtypes = {
        # 'newUsers': int,
        'conversions': int,
        # 'totalUsers': int,
        # 'transactions': int,
        # 'checkouts': int,
        # 'totalPurchasers': int,
        # 'engagedSessions': int,
        # 'userEngagementDuration': int,
        # 'bounceRate': float,
    }
    # df = pd.DataFrame(rows, columns=header)
    df = df.astype(dtypes)
    return df


def report_6month(property_id="289131905"):  # '289131905'  #PROPERTY ID in GA4
    """Runs a simple report on a Google Analytics 4 property."""

    ic(property_id)
    target_file = f'./{property_id}_cmp_report.csv'
    # Check if file exists
    if os.path.isfile(target_file):
        # Get last modified date of file
        mod_time = os.path.getmtime(target_file)
        last_modified_date = datetime.fromtimestamp(mod_time).date()
        # Check if last modified date is today
        today = date.today()
        if last_modified_date == today:
            logger.info('File exists and was last modified today.')
            return pd.read_csv(target_file)

    # [START analyticsdata_run_report_initialize]
    # Using a default constructor instructs the client to use the credentials
    # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
    client = BetaAnalyticsDataClient()
    # [END analyticsdata_run_report_initialize]

    # Get today's date
    today = datetime.now()
    # Calculate the date 6 months ago
    six_months_ago = today - timedelta(days=6 * 30)
    # Format the date as YYYY-mm-dd
    date_from = six_months_ago.strftime('%Y-%m-%d')

    # [START analyticsdata_run_report]
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="date"),
            # Dimension(name="firstSessionDate"),
            # Dimension(name="firstUserSource"),
            Dimension(name="campaignName"),
            # Dimension(name="firstUserManualTerm"),
            # Dimension(name="firstUserManualAdContent"),
            # # # Dimension(name="firstUserGoogleAdsCampaignName"), #!이게 포함되면 구글로 유입된 데이터만 추출됨
            # # Dimension(name="pageReferrer"),
            # # Dimension(name="landingPagePlusQueryString"),  #-deviceCategory, platform, userAgeBracket,userGender, brandingInterest, audienceName, city
        ],
        metrics=[
            # Metric(name="newUsers"),
            Metric(name="conversions"),
            # Metric(name="totalUsers"),
            # Metric(name="transactions"),
            # Metric(name="checkouts"),
            # Metric(name="totalPurchasers"),
            # Metric(name="engagedSessions"),
            # Metric(name="userEngagementDuration"),
            # Metric(name="bounceRate"),
        ],
        # date_ranges=[DateRange(start_date="2023-01-01", end_date="today")],
        date_ranges=[DateRange(start_date=date_from, end_date="today")],
    )
    # engagement      : sessions that lasted longer than 10 seconds, or had a conversion event, or had 2 or more screen views.
    # Engagement rate : The percentage of engaged sessions (Engaged sessions divided by Sessions). This metric is returned as a fraction; for example, 0.7239 means 72.39% of sessions were engaged sessions.
    # Bounce rate     : The percentage of sessions that were not engaged ((Sessions Minus Engaged sessions) divided by Sessions). This metric is returned as a fraction; for example, 0.2761 means 27.61% of sessions were bounces.
    # Conversions     : The count of conversion events. Events are marked as conversions at collection time; changes to an event's conversion marking apply going forward. You can mark any event as a conversion in Google Analytics, and some events (i.e. first_open, purchase) are marked as conversions by default. To learn more, see https://support.google.com/analytics/answer/9267568.
    # TODO more details --> https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema

    response = client.run_report(request)
    return to_df(response, property_id)


def plot_ga_campaigns(prop_id):
    campaign_df = report_6month(prop_id)
    df = campaign_df
    logger.info(df.head().to_string() + '\n' + str(df.dtypes))

    df['campaign'] = df['campaignName']  # +' ['+df['firstUserSource']+']'
    df['campaignName'] = df['campaignName'].fillna('')
    logger.info(
        'unary?' + str(df['campaignName'].str.contains('direct|referral', case=False)))
    df = df[~df['campaignName'].str.contains('direct|referral', case=False)]

    # Convert the date column to a datetime object
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

    # Create a scatter chart with the campaign key on the y-axis, date on the x-axis, and the number of new users as the marker size
    fig = px.scatter(df, x='date', y='campaign', size='conversions',
                     title='Conversions by Date and Campaign', height=1000, color='campaign', size_max=50)

    # Add x and y guide lines
    # fig.update_xaxes(showspikes=True, spikecolor="gray", spikemode="toaxis+across", spikesnap="cursor", showticklabels=True, ticklabelposition="outside top",)
    fig.update_xaxes(showspikes=True, spikecolor="gray",
                     spikemode="toaxis+across", spikesnap="cursor")
    fig.update_yaxes(showspikes=True, spikecolor="gray",
                     spikemode="toaxis+across", spikesnap="cursor")
    return fig


# def plot_ga_campaigns(prop_id):
#     campaign_df = report_6month(prop_id)
#     df = campaign_df
#     logger.info(df.head().to_string() + '\n' + str(df.dtypes))

#     df['campaign'] = df['firstUserSourceMedium']
#     df['firstUserSourceMedium'] = df['firstUserSourceMedium'].fillna('')
#     logger.info('unary?' + str(df['firstUserSourceMedium'].str.contains('direct|referral', case=False)))
#     df = df[~df['firstUserSourceMedium'].str.contains('direct|referral', case=False)]
#     df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

#     # Create a scatter chart with graph_objects
#     # fig = go.Figure()
#     fig = px.scatter(df, x="date", y="campaign", color="campaign",
#                      size='newUsers')
#     # fig.update_traces(marker_size=5)
#     return fig


# VALID_USERNAME_PASSWORD_PAIRS = {'dna': 'lCCn6q+LrCcq0QWH', 'sam': 'DpiKCdXChgfiC3s9', 'max': 'lc5cniKBFLIEU+42'}
# PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
PLOTLY_LOGO = './assets/cbi_logo.png'
PLOTLY_TITLE = './assets/cblogo-long.png'
OLD_PID = '289131905'
NEW_PID = '387495261'


# server = Flask(__name__)
app = dash.Dash(external_stylesheets=[
                dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
server = app.server
server.secret_key = os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.server.before_request
def route_login():
    if not current_user.is_authenticated and request.endpoint != 'login':
        return redirect('/login')


@server.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        headers = {
            'Origin': 'https://stats.cleanb.life',
            'Referer': 'https://stats.cleanb.life'
        }
        username = request.form['username']
        password = request.form['password']
        response = requests.post('https://bellboy.cleanb.life/api/v1/auth/user/signin',
                                 headers=headers, json={"email": username, "password": password})

        if response.status_code == 200:
            data = response.json()
            if 'token' in data:
                user = User(data['token'])
                login_user(user)
                return redirect('/')
            else:
                return "Login failed. Please try again."
        else:
            return "Login failed. Please try again."
    return render_template('login.html')


@server.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


def protected(f):
    @wraps(f)
    def decorated_callback(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_callback


logger.remove()
# app.logger.addHandler(handler)
# app.server.logger.addHandler(handler)

# logger.add(sys.stderr, level="TRACE")
# logger.add(sys.stdout, level="TRACE")
logger.add(
    "run.log",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    level="INFO",
    enqueue=True,
    serialize=False,
    backtrace=True,
    diagnose=True,
    rotation="100 MB",
    retention="10 days",
    compression="zip",
    buffering=-1,
)

sidebar = html.Div(
    [
        html.Div([
            html.Img(src=PLOTLY_LOGO, style={"width": "3.25rem"}),
            html.Img(src=PLOTLY_TITLE, style={"width": "7.25rem"}),
        ], className="sidebar-logo"),
        html.Div(
            [
                # dbc.DropdownMenu(
                #     label="Select data source",
                #     children=[
                #         dbc.DropdownMenuItem('cleanbedding.kr', id='old-pid'),
                #         dbc.DropdownMenuItem('cleanb.life', id='new-pid'),
                #     ],
                #     value='old-pid',
                #     style={"width": "14rem"},
                #     className="sidebar-dropdown",
                # ),
                # html.Div(id='data-source', style={'display': 'none'}),
                dcc.Dropdown(
                    id='data-source',
                    options=[
                        {'label': 'cleanbedding.kr', 'value': OLD_PID},
                        {'label': 'cleanb.life', 'value': NEW_PID},
                    ],
                    value=NEW_PID,  # Default selected item
                    clearable=False,
                    style={"width": "10.5rem"},
                    className="sidebar-dropdown",
                )
            ],
            className="sidebar-header",
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    [html.I(className="fas fa-shoe-prints me-2"),
                     html.Span("광고방문자")],
                    href="/",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-users me-2"),
                        html.Span("사용자분석"),
                    ],
                    href="/customers",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-money-check-alt me-2"),
                        html.Span("매출분석"),
                    ],
                    href="/sales",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-chart-line me-2"),
                        html.Span("성장지표"),
                    ],
                    href="/health",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-map-marked-alt me-2"),
                        html.Span("지역분석"),
                    ],
                    href="/geo",
                    active="exact",
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className="sidebar",
)


@app.callback(Output('current-pid', 'data'), [Input('data-source', 'value')])
def update_data_source(data_source):
    return data_source


content = html.Div(id="page-content", className="content")

# auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    dcc.Loading(id="loading", type="circle", className="loading-with-text",
                fullscreen=True, children=[content]),
    dcc.Store(id='sidebar-hover', data=False),
    dcc.Store(id='current-pid', data=OLD_PID)  # New dcc.Store component
])

customer_df = None


@app.callback(Output("ga-graph-container", "children"),
              [Input("conversion-dropdown", "value"), Input("current-pid", "data")])
def update_ga_graph(conversion_type, data_source):
    if conversion_type == "GA conversion":
        fig = plot_ga_campaigns(data_source)
    elif conversion_type == "Clbe Conversion":
        fig = clbe_conv.plot_clbe_conversions()  # 또는 다른 플로팅 함수
    return dcc.Graph(id='ga', figure=fig)


@app.callback(
    Output('customer-eda-graph', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_customer_eda(start_date, end_date):
    # 필요한 경우 start_date 및 end_date를 사용하여 데이터를 필터링하고
    start_date_object = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date_object = datetime.strptime(end_date, '%Y-%m-%d').date()
    # if start_date_object.year == 2023 and start_date_object.month < 8:
    #     start_date_object = start_date_object.replace(month=7, day=23)
    # 인수 수정 필요
    return cleanblife_customers.plot_customer_eda(customer_df, start_date_object, end_date_object)


@app.callback(
    Output("geo-output", "children"),
    [Input("geo-dropdown", "value")]
)
def update_geo_content(selected_value):
    logger.info(f"selected_value: {selected_value}")
    try:
        if selected_value == "all":
            return html.Div(geo_analytics.plot())
        elif selected_value == "subscribed":
            return html.Div(geo_analytics.subscription_plot())
        else:
            return html.Div(figure=geo_analytics.plot())
    except Exception as e:
        return html.Div(f"An error occurred: {e}")


@app.callback(Output("page-content", "children"), [Input("url", "pathname"), Input("current-pid", "data")])
# @protected
def render_page_content(pathname, data_source):
    global customer_df
    # time.sleep(5)
    if pathname == "/":
        # return dcc.Graph(id='ga', figure=plot_ga_campaigns(data_source))
        return html.Div(children=[
            html.H1(children='Your Dashboard'),
            dcc.Dropdown(id="conversion-dropdown",
                         options=[{"label": "GA conversion", "value": "GA Conversion"},
                                  {"label": "Clbe Conversion", "value": "Clbe Conversion"}],
                         value="Clbe Conversion"),
            html.Div(id='ga-graph-container')
        ])
    elif pathname == "/sales":
        odf = get_order_df()
        return html.Div(children=[
            html.H1(children='Sales analytics'),
            dcc.Graph(id='sa-stack',
                      figure=sales_analytics.monthly_sales_stacked_plot(odf)),
            dcc.Graph(id='sa', figure=sales_analytics.msales_plot(odf)),
            dcc.Graph(id='gr', figure=sales_analytics.user_plot(odf)),
            dcc.Graph(id='dnu', figure=sales_analytics.dnu_plot(odf)),
            dcc.Graph(id='dnut', figure=sales_analytics.dnu_trend_plot(odf))
        ])
    elif pathname == "/customers":

        customer_df = cleanblife_customers.fetch_customer_data()
        customer_df['user_registered_seoul'] = pd.to_datetime(
            customer_df['user_registered_seoul'])
        customer_df['registration_date'] = customer_df['user_registered_seoul'].dt.date

        return html.Div(children=[
            html.H1(children='사용자 분석 '),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date="2023-08-01",
                end_date=customer_df['registration_date'].max(),
                display_format='YYYY-MM-DD'
            ),
            dcc.Graph(id='customer-eda-graph')
            # dcc.Graph(id='customer-eda-graph', figure=cleanblife_customers.plot_customer_eda())
        ])
    elif pathname == "/health":
        return html.Div(children=[
            html.H1(children='Product Health Metrics'),
            dcc.Graph(id='ha', figure=health_metrics.plot(get_order_df())[0]),
            dcc.Graph(id='crr', figure=health_metrics.plot(get_order_df())[1])
        ])
    elif pathname == "/geo":
        return html.Div(children=[
            html.H1(children='행정구역별 고객 수'),
            dcc.Dropdown(id="geo-dropdown",
                         options=[{"label": "회원수", "value": "all"},
                                  {"label": "구독자수", "value": "subscribed"}],
                         value="all"
                         ),
            html.Div(id='geo-output')
            # geo_analytics.plot(),
            # geo_analytics.subscription_plot(),
        ])
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )


class PropagateHandler(logging.Handler):

    def emit(self, record):
        level = logging.getLevelName(record.levelno)
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(level, record.getMessage())


logging.basicConfig(handlers=[PropagateHandler()], level=0)
sys.stdout = sys.stderr = open('run.log', 'a')
if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0')
    # app.run_server(debug=True, host='0.0.0.0', threaded=True,)
