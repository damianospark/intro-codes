import datetime
import json
import string
import traceback
import warnings

import gspread
import mysql.connector
import numpy as np
import pandas as pd
import plotly.express as px
from loguru import logger

warnings.simplefilter(action='ignore')


def get_clbe_conv_data():
    # MySQL 데이터베이스에 연결
 


    #각 광고를 타고 들어와 처음 매출을 일으킨 건들만 조회
    query = """
    SELECT
        o.id AS order_id,
        p.ID AS wp_order_id,
        p.post_status AS order_status,
        m1.meta_value AS customer_user_id,
        m2.meta_value AS billing_name_kr,
        m3.meta_value AS billing_address_1,
        m4.meta_value AS billing_address_2,
        t.item_value AS traffic_source,
        c.item_value AS utm_campaign,
        s.item_value AS utm_source,
        m.item_value AS utm_medium,
        u.item_value AS utm_content,
        o.utm_term_id,
        o.utm_content_id,
        o.gross_sale,
        o.net_sale,
        o.total_sale,
        o.date AS order_date
    FROM
        wp_pys_stat_order o
    JOIN
        wp_posts p ON o.order_id = p.ID
    LEFT JOIN
        wp_postmeta m1 ON p.ID = m1.post_id AND m1.meta_key = '_customer_user'
    LEFT JOIN
        wp_postmeta m2 ON p.ID = m2.post_id AND m2.meta_key = '_billing_first_name_kr'
    LEFT JOIN
        wp_postmeta m3 ON p.ID = m3.post_id AND m3.meta_key = '_billing_address_1'
    LEFT JOIN
        wp_postmeta m4 ON p.ID = m4.post_id AND m4.meta_key = '_billing_address_2'
    LEFT JOIN
        wp_pys_stat_traffic t ON o.traffic_source_id = t.id
    LEFT JOIN
        wp_pys_stat_utm_campaing c ON o.utm_campaing_id = c.id
    LEFT JOIN
        wp_pys_stat_utm_source s ON o.utm_source_id = s.id
    LEFT JOIN
        wp_pys_stat_utm_medium m ON o.utm_medium_id = m.id
    LEFT JOIN
        wp_pys_stat_utm_content u ON o.utm_content_id = u.id
    INNER JOIN (
        SELECT
            m1.meta_value AS customer_user_id,
            MIN(o.date) AS first_order_date
        FROM
            wp_pys_stat_order o
        JOIN
            wp_posts p ON o.order_id = p.ID
        LEFT JOIN
            wp_postmeta m1 ON p.ID = m1.post_id AND m1.meta_key = '_customer_user'
        WHERE
            p.post_type = 'shop_order'
        GROUP BY
            m1.meta_value
    ) AS first_orders ON m1.meta_value = first_orders.customer_user_id AND o.date = first_orders.first_order_date
    WHERE
        p.post_type = 'shop_order'
    ORDER BY
        order_date DESC;
    """

    # 쿼리 실행하고 결과를 DataFrame으로 가져오기
    df = pd.read_sql_query(query, conn)
    # 연결 종료
    conn.close()
    # print(df)
    return df


def plot_clbe_conversions():
    df = get_clbe_conv_data()

    # Additional processing to fill na and handle date formatting
    df['utm_campaign'] = df['utm_campaign'].fillna('')
    df['order_date'] = pd.to_datetime(df['order_date']).dt.date

    # Making sure 'utm_campaign' and 'order_date' columns are not empty or null
    df = df[df['utm_campaign'].notna() & df['order_date'].notna()]

    # Grouping by order_date and utm_campaign and counting the occurrences
    df_grouped = df.groupby(['order_date', 'utm_campaign']
                            ).size().reset_index(name='order_count')

    # Adding a row for the sum of all campaigns per day
    df_sum_all = df.groupby(['order_date']).size(
    ).reset_index(name='order_count')
    df_sum_all['utm_campaign'] = 'Sum of all comp.'

    # Concatenating the two dataframes
    df_grouped = pd.concat([df_grouped, df_sum_all], ignore_index=True)

    # Creating the plot
    fig = px.scatter(df_grouped, x='order_date', y='utm_campaign', size='order_count',
                     title='CLbe Conversions by Date and Campaign', height=1000,
                     color='utm_campaign', size_max=30)

    # Adding guidelines for x and y axes
    fig.update_xaxes(showspikes=True, spikecolor="gray",
                     spikemode="toaxis+across", spikesnap="cursor")
    fig.update_yaxes(showspikes=True, spikecolor="gray",
                     spikemode="toaxis+across", spikesnap="cursor")
    fig.update_layout(hovermode='x unified')

    return fig


def plot_clbe_convsales():
    df = get_clbe_conv_data()

    # Additional processing to fill na and handle date formatting
    df['utm_campaign'] = df['utm_campaign'].fillna('')
    df['order_date'] = pd.to_datetime(df['order_date'])

    # Making sure 'utm_campaign' and 'order_date' columns are not empty or null
    df = df[df['utm_campaign'].notna() & df['order_date'].notna()]

    # Creating the plot
    fig = px.scatter(df, x='order_date', y='utm_campaign', size='gross_sale',
                     title='CLbe Conversions by Date and Campaign', height=1000,
                     color='utm_campaign', size_max=30)

    # Adding guidelines for x and y axes
    fig.update_xaxes(showspikes=True, spikecolor="gray",
                     spikemode="toaxis+across", spikesnap="cursor")
    fig.update_yaxes(showspikes=True, spikecolor="gray",
                     spikemode="toaxis+across", spikesnap="cursor")

    return fig
