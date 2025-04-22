import pandas as pd
from dateutil.parser import parse
import plotly.express as px


def plot(df):
    # Create a new column for the month and year
    df['month_year'] = df['주문 일자'].dt.to_period('M').dt.to_timestamp()
    # .astype(str)

    # Group the DataFrame by month_year and count the unique IDs
    monthly_active_users = df.groupby('month_year')['주문자 이메일'].nunique().reset_index()
    # Create a line plot with Plotly Express
    fig1 = px.line(monthly_active_users, x='month_year', y='주문자 이메일', title='Monthly Active Users')
    # Add a trend line to the plot
    fig2 = px.scatter(monthly_active_users, x='month_year', y='주문자 이메일', trendline="Monthly Active Users trends - ols")
    fig3 = px.scatter(monthly_active_users, x='month_year', y='주문자 이메일', trendline="Monthly Active Users trends - lowess")
    # Show the plot
    return fig1, fig2, fig3
