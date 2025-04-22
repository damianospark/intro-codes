import plotly.graph_objs as go
import pandas as pd
# import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
import warnings

from plotly.subplots import make_subplots
import pytz
from loguru import logger

tz = pytz.timezone('Asia/Seoul')
logger = logger.bind(timezone=tz)
warnings.simplefilter("ignore")


# def monthly_sales_stacked_plot(df):
#     # Convert '결제금액' (Payment Amount) to numeric
#     df['결제금액'] = pd.to_numeric(df['결제금액'], errors='coerce').fillna(0).astype(int)

#     # Group by both '결제일시' (Order Date) and 'source', and then compute the sum of sales for each month
#     monthly_sales_grouped = df.groupby([pd.Grouper(key='결제일시', freq='M'), 'source'])['결제금액'].sum().unstack().reset_index()

#     # Create a plotly figure
#     fig = go.Figure()

#     # Check if old or new data is present and add the respective bars
#     if 'old' in monthly_sales_grouped.columns:
#         fig.add_trace(go.Bar(
#             x=monthly_sales_grouped['결제일시'],
#             y=monthly_sales_grouped['old'],
#             name='Old 월매출'
#         ))

#     if 'new' in monthly_sales_grouped.columns:
#         fig.add_trace(go.Bar(
#             x=monthly_sales_grouped['결제일시'],
#             y=monthly_sales_grouped['new'],
#             name='New 월매출'
#         ))

#     # Set the layout for stacked bar
#     fig.update_layout(barmode='stack', xaxis_title='Date', yaxis_title='Sales', title='Monthly Sales for Old and New Revenue')
#     # Show the plot
#     return fig

def monthly_sales_stacked_plot(df):
    # Convert '결제금액' (Payment Amount) to numeric
    df['결제금액'] = pd.to_numeric(df['결제금액'], errors='coerce').fillna(0).astype(int)

    # Group by both '결제일시' (Order Date) and 'source', and then compute the sum of sales for each month
    monthly_sales_grouped = df.groupby([pd.Grouper(key='결제일시', freq='M'), 'source'])['결제금액'].sum().unstack().reset_index()
    monthly_sales_grouped['total'] = monthly_sales_grouped[['old', 'new']].sum(axis=1)

    # Format function for KRW in millions
    def format_krw(value):
        return f"{int(value / 1_000_000)}백만 원"

    # Determine last three month's average sales for same days up to today
    current_month_start = df['결제일시'].max().replace(day=1)
    last_date = df['결제일시'].max()
    sales_list = []
    for i in range(1, 4):
        month_start = (current_month_start - pd.DateOffset(months=i))
        month_end = month_start.replace(day=min(last_date.day, (month_start + pd.DateOffset(months=1) - pd.DateOffset(days=1)).day))
        sales = df[(df['결제일시'] >= month_start) & (df['결제일시'] <= month_end)]['결제금액'].sum()
        sales_list.append(sales)

    last_three_month_avg = sum(sales_list) / 3

    # Number of unique months
    num_months = len(monthly_sales_grouped['결제일시'].unique())

    # Create subplots
    fig = make_subplots(rows=1, cols=2, column_widths=[num_months, 1], shared_yaxes=True, subplot_titles=(
        '월매출 추이 및 매출 속도 비교', '이전3개월'), horizontal_spacing=0)

    # Add bars for the monthly sales
    if 'old' in monthly_sales_grouped.columns:
        fig.add_trace(go.Bar(
            x=monthly_sales_grouped['결제일시'],
            y=monthly_sales_grouped['old'],
            name='Old 월매출',
        ), row=1, col=1)

    if 'new' in monthly_sales_grouped.columns:
        fig.add_trace(go.Bar(
            x=monthly_sales_grouped['결제일시'],
            y=monthly_sales_grouped['new'],
            name='New 월매출',
        ), row=1, col=1)

    # Adding the combined text on top of the stacked bars
    fig.add_trace(go.Scatter(
        x=monthly_sales_grouped['결제일시'],
        y=monthly_sales_grouped['total'],
        mode='text',
        text=monthly_sales_grouped['total'].apply(format_krw),
        showlegend=False
    ), row=1, col=1)

    # Add bars for the average sales of last three months
    fig.add_trace(go.Bar(
        x=['3개월 평균'],
        y=[last_three_month_avg],
        name='동기간 3개월 평균',
        marker_color='orange',
        text=format_krw(last_three_month_avg),
        textposition='outside'
    ), row=1, col=2)

    fig.update_layout(barmode='stack', yaxis_title='Sales')

    # Show the plot
    return fig


def msales_plot(df):
    df['결제금액'] = pd.to_numeric(df['결제금액'], errors='coerce').fillna(0).astype(int)
    # Resample the data to get the monthly and weekly sales
    monthly_sales = df.resample('M', on='결제일시')['결제금액'].sum().reset_index()
    weekly_sales = df.resample('W', on='결제일시')['결제금액'].sum().reset_index()

    # Create a plotly figure
    fig = go.Figure()

    # Add the monthly sales data as a scatter plot
    fig.add_trace(go.Scatter(
        x=monthly_sales['결제일시'],
        y=monthly_sales['결제금액'],
        name='월매출',
        mode='markers+lines',
        line=dict(shape='linear'),
        marker=dict(size=8),
    ))

    # Add the weekly sales data as a scatter plot
    fig.add_trace(go.Scatter(
        x=weekly_sales['결제일시'],
        y=weekly_sales['결제금액'],
        name='Weekly Sales',
        mode='markers+lines',
        line=dict(shape='linear'),
        marker=dict(size=4),
    ))

    # Add the trendline for monthly sales
    fig.add_trace(
        go.Scattergl(x=monthly_sales['결제일시'], y=monthly_sales['결제금액'].rolling(window=6).mean(), name='Trendline (Monthly)', mode='lines', line=dict(color='orange', dash='dot')))
    # Add the trendline for weekly sales
    fig.add_trace(
        go.Scattergl(x=weekly_sales['결제일시'], y=weekly_sales['결제금액'].rolling(window=8).mean(), name='Trendline (Weekly)', mode='lines', line=dict(color='green', dash='dot')))

    # Set the axis labels and title
    fig.update_layout(xaxis_title='Date', yaxis_title='Sales', title='Monthly and Weekly Sales')

    # Show the plot
    return fig


def user_plot(df):
    df['결제금액'] = pd.to_numeric(df['결제금액'], errors='coerce').fillna(0).astype(int)
    default_date = '1900-01-01'
    df['연령'].fillna(default_date, inplace=True)
    df.loc[df['연령'] == '', '연령'] = default_date
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    # logger.info(df['연령'].unique())
    unique_ages = df['연령']
    for age in unique_ages:
        logger.info(age)
    # Convert the '연령' column to a datetime format
    df['연령'] = pd.to_datetime(df['연령'], format='%Y-%m-%d')

    # Calculate the age in years based on the '연령' column
    now = datetime.now()
    df['Age'] = df['연령'].apply(lambda x: relativedelta(now, x).years)

    # Create a new column for age group based on the 'Age' column
    df['Age Group'] = pd.cut(df['Age'], bins=[0, 20, 30, 40, 50, 60, float('inf')], labels=['10s', '20s', '30s', '40s', '50s', '60s+'])

    # Convert the '결제일시' column to a datetime format and extract the year and month
    df['결제일시'] = pd.to_datetime(df['결제일시'])
    df['YearMonth'] = df['결제일시'].dt.strftime('%Y-%m')

    # Calculate the monthly sales sum and count by age group
    grouped = df.groupby(['YearMonth', 'Age Group']).agg({'결제금액': 'sum', '결제일시': 'count'}).reset_index()
    grouped.columns = ['YearMonth', 'Age Group', '결제금액', 'Count']

    # Calculate the total monthly sales
    total_monthly_sales = grouped.groupby(['YearMonth'])['결제금액'].sum().reset_index()
    total_monthly_sales.columns = ['YearMonth', 'Total Sales']

    # Calculate the monthly sales percentage by age group
    grouped_with_percentage = grouped.merge(total_monthly_sales, on='YearMonth')
    grouped_with_percentage['Percentage'] = (grouped_with_percentage['결제금액'] / grouped_with_percentage['Total Sales']) * 100

    # Create a stacked bar chart using Plotly with percentage annotations
    fig = go.Figure()

    for age_group in grouped['Age Group'].unique():
        age_group_data = grouped_with_percentage[grouped_with_percentage['Age Group'] == age_group]

        hovertemplate = ('<b>%{x}</b><br>' +
                         'Age Group: ' + age_group + '<br>' +
                         '건수: %{customdata[0]:,}<br>' +
                         '매출: %{customdata[1]:,.0f}<br>' +
                         '비율: %{customdata[2]:.1f}%<br>' +
                         '월매출: %{customdata[3]:,.0f}')

        fig.add_trace(go.Bar(name=age_group, x=age_group_data['YearMonth'],
                             y=age_group_data['결제금액'],
                             text=age_group_data['Percentage'].round(1).astype(str) + '%',
                             textposition='inside',
                             customdata=age_group_data[['Count', '결제금액', 'Percentage', 'Total Sales']].values,
                             hovertemplate=hovertemplate))

    fig.update_layout(title='Monthly Sales by Age Group',
                      xaxis=dict(title='Year-Month'),
                      yaxis=dict(title='Sales Sum'),
                      barmode='stack')
    # fig.show()
    return fig


def dnu_plot(df):
    # Group the DataFrame by '주문자_이메일' and get the first occurrence of the user in the DataFrame

    df_first_orders = df.groupby('주문자_이메일').first()
    print(df_first_orders['결제일시'], df['결제일시'].max())

    # Count the number of occurrences for each date
    df_daily_new_users = df_first_orders['결제일시'].value_counts()

    # Resample the DataFrame to fill in missing days with zero values
    df_daily = df_daily_new_users.resample('D').sum().fillna(0)

    df_daily_3weeks = df_daily.tail(112)
    df_daily_3weeks.name = 'New Users'
    # display(df_daily_3weeks, mondays,thursdays)

    # Create a line plot with Plotly Express
    fig = px.line(df_daily_3weeks, x=df_daily_3weeks.index, y='New Users', title='Daily New Users')

    # Add markers at every Sunday
    sundays = df_daily_3weeks.index[df_daily_3weeks.index.dayofweek == 6]
    fig.add_trace(go.Scatter(
        name='일',
        x=sundays,
        y=df_daily[df_daily.index.isin(sundays)].values,
        mode='markers',
        marker=dict(
            color='orange',
            size=7
        ),
        showlegend=True
    ))

    # Add lines to show Mondays and Thursdays
    mondays = df_daily_3weeks.index[df_daily_3weeks.index.dayofweek == 0]
    # for day in [mondays, thursdays]:
    fig.add_trace(go.Scatter(
        name='월',
        x=mondays,
        y=df_daily[df_daily.index.isin(mondays)].values,
        mode='markers',
        marker=dict(
            size=7, color='yellow'
        ),
        showlegend=True
    ))

    saturdays = df_daily_3weeks.index[df_daily_3weeks.index.dayofweek == 5]
    fig.add_trace(go.Scatter(
        name='토',
        x=saturdays,
        # y=[0] * len(day),
        y=df_daily[df_daily.index.isin(saturdays)].values,
        mode='markers',
        marker=dict(
            size=7, color='red'
        ),
        showlegend=True
    ))
    # Show the plot
    # fig.show()
    return fig


def dnu_trend_plot(df):
    # Group the DataFrame by '주문자_이메일' and get the first occurrence of the user in the DataFrame
    df_first_orders = df.groupby('주문자_이메일').first()

    # Count the number of occurrences for each date
    df_daily_new_users = df_first_orders['결제일시'].value_counts()

    # Resample the DataFrame to fill in missing days with zero values
    df_daily = df_daily_new_users.resample('D').sum().fillna(0)
    df_daily.name = 'New Users'

    fig4 = px.scatter(df_daily, x=df_daily.index, y='New Users', trendline="expanding",
                      trendline_color_override='deeppink')  # trendline="rolling", trendline_options={"window": 10}
    fig4.update_layout(title='Daily New Users Trend')
    return fig4
