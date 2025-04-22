# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
import warnings

import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

warnings.simplefilter("ignore")

# # use credentials to create a client to interact with the Google Drive API
# scope = ['https://www.googleapis.com/auth/drive']
# creds = ServiceAccountCredentials.from_json_keyfile_name('./cleanbedding-c9b48eb044cf-service-account-key.json', scope)
# client = gspread.authorize(creds)

# # open the Google Sheet by its title
# # sheet = client.open('Analysis').worksheet("Orders(All)")

# # get all the data in the sheet
# all_values = sheet.get_all_values()
# data = [row[:55] for row in all_values[5:]]

# # convert the data to a Pandas DataFrame
# df = pd.DataFrame(data[1:], columns=data[0])
# df = df[df['Validity'] == '배송지역']
# # Load order list data
# # orders_df = pd.read_excel('주문_주문별_상세검색_230227170733.xlsx')

# # Convert '결제일시' column to datetime
# df['결제일시'] = pd.to_datetime(df['결제일시'], format='%Y-%m-%d')

# df.sort_values('결제일시', inplace=True)
# df = df[df['결제일시'] >= '2021-01-01']
# df = df[~df['주문 상태'].str.contains('취소')]


def plot(df):  # Calculate MRR
    # Extract month from '결제일시' column and create a new 'Month' column
    df['Month'] = df['결제일시'].dt.to_period('M')
    # df['결제금액'] = df['결제금액'].astype('int')
    df['결제금액'] = pd.to_numeric(df['결제금액'], errors='coerce').fillna(0).astype(int)

    mrr_df = df.groupby('Month')['결제금액'].sum().reset_index()
    mrr_df.rename(columns={'결제금액': 'MRR'}, inplace=True)

    # Calculate CRR
    current_month = mrr_df['Month'].max().month
    previous_month = current_month - 1
    current_mrr = mrr_df[mrr_df['Month'].dt.month == current_month]['MRR'].values[0]
    previous_mrr = mrr_df[mrr_df['Month'].dt.month == previous_month]['MRR'].values[0]
    crr = current_mrr / previous_mrr

    # Calculate ARPU
    arpu_df = df.groupby('Month')['결제금액', '주문자 이메일'].agg({'결제금액': 'sum', '주문자 이메일': 'nunique'}).reset_index()
    arpu_df.rename(columns={'결제금액': 'MRR', '주문자 이메일': 'Active Users'}, inplace=True)
    arpu_df['ARPU'] = arpu_df['MRR'] / arpu_df['Active Users']

    orders_df = df
    # calculate monthly MRR
    monthly_mrr = orders_df.groupby(pd.Grouper(key='결제일시', freq='M'))['결제금액'].sum().reset_index()
    monthly_mrr.columns = ['Month', 'MRR']

    monthly_mrr['MRR'] = monthly_mrr['MRR'] / 1000000  # convert to millions

    # calculate monthly CRR
    monthly_orders = orders_df.groupby(pd.Grouper(key='결제일시', freq='M'))['주문자 이메일'].nunique().reset_index()
    monthly_orders.columns = ['Month', 'Unique Users']
    monthly_crr = monthly_orders.copy()
    monthly_crr['CRR'] = monthly_crr['Unique Users'].pct_change()
    monthly_crr = monthly_crr.dropna()

    # merge monthly MRR and CRR
    monthly_metrics = pd.merge(monthly_mrr, monthly_crr, on='Month', how='outer')

    # calculate monthly ARPU
    monthly_metrics['ARPU'] = monthly_metrics['MRR'] / orders_df.groupby(pd.Grouper(key='결제일시', freq='M'))['주문자 이메일'].nunique().values
    monthly_metrics['Month Number'] = monthly_metrics['Month'].dt.strftime('%Y-%m-%d')

    # plot the data
    # Define custom hover template with month number
    hover_template = '<b>Month %{customdata[1]}</b><br>' + \
        'MRR: %{customdata[0]:,.2f}M<br>' + \
        'CRR: %{customdata[2]:.0%}<br>' + \
        'ARPU: %{customdata[3]:,.2f}<br>'

    # Add month number column
    monthly_metrics['Month Number'] = monthly_metrics['Month'].apply(lambda x: f'{x.month}')

    # Plot the data

    #
    # decorate
    #
    # create subplot with two y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add markers for current month and same month last year
    fig.add_trace(
        go.Scatter(hovertemplate=hover_template, x=monthly_metrics['Month'], y=monthly_metrics['MRR'], name='MRR', line_color='#636EFA', marker=dict(color='blue')),
        secondary_y=False)
    fig.add_trace(
        go.Scatter(hovertemplate=hover_template, x=monthly_metrics['Month'], y=monthly_metrics['CRR'], name='CRR', line_color='#aa0000', marker=dict(color='red')),
        secondary_y=False)
    fig.add_trace(
        go.Scatter(hovertemplate=hover_template, x=monthly_metrics['Month'], y=monthly_metrics['ARPU'], name='ARPU', line_color='#00aa00', marker=dict(color='green')),
        secondary_y=True)

    fig.update_traces(mode='lines',
                      customdata=np.column_stack((monthly_metrics['MRR'], monthly_metrics['Month Number'], monthly_metrics['CRR'], monthly_metrics['ARPU'])),
                      hovertemplate=hover_template)

    # @rule: Current Month는 바로 직전월로 한다. 현재 월은 아직 모든 매출이 일어난 것이 아니므로!
    current_month = monthly_metrics['Month'].max()  # Monday가 starting date임.
    current_month = current_month + pd.DateOffset(months=-1)  # last_month
    last_year_month = current_month + pd.DateOffset(years=-1)
    last_year = current_month + pd.DateOffset(years=-1)

    marker_data = [{
        'bc': 'rgba(0,0,100,0.7)',
        'x': current_month,
        'y': monthly_metrics.loc[(monthly_metrics['Month'].dt.year == current_month.year) & (monthly_metrics['Month'].dt.month == current_month.month), 'MRR'].iloc[0],
        'color': 'blue',
        'label': 'current MRR'
    },
        {
        'bc': 'rgba(0,0,100,0.7)',
        'x': last_year_month,
        'y': monthly_metrics.loc[(monthly_metrics['Month'].dt.year == last_year.year) & (monthly_metrics['Month'].dt.month == last_year_month.month), 'MRR'].iloc[0],
        'color': 'blue',
        'label': 'last year MRR'
    },
        {
        'bc': 'rgba(100,0,0,0.7)',
        'x': current_month,
        'y': monthly_metrics.loc[(monthly_metrics['Month'].dt.year == current_month.year) & (monthly_metrics['Month'].dt.month == current_month.month), 'CRR'].iloc[0],
        'color': 'red',
        'label': 'current CRR'
    },
        {
        'bc': 'rgba(100,0,0,0.7)',
        'x': last_year_month,
        'y': monthly_metrics.loc[(monthly_metrics['Month'].dt.year == last_year.year) & (monthly_metrics['Month'].dt.month == last_year_month.month), 'CRR'].iloc[0],
        'color': 'red',
        'label': 'last year CRR'
    },
        {
        'bc': 'rgba(0,100,0,0.7)',
        'x': current_month,
        'y': monthly_metrics.loc[(monthly_metrics['Month'].dt.year == current_month.year) & (monthly_metrics['Month'].dt.month == current_month.month), 'ARPU'].iloc[0],
        'color': 'green',
        'label': 'current ARPU'
    },
        {
        'bc': 'rgba(0,100,0,0.7)',
        'x': last_year_month,
        'y': monthly_metrics.loc[(monthly_metrics['Month'].dt.year == last_year.year) & (monthly_metrics['Month'].dt.month == last_year_month.month), 'ARPU'].iloc[0],
        'color': 'green',
        'label': 'last year ARPU'
    }]
    # Add markers to the plot
    for marker in marker_data:
        scndy = True if 'ARPU' in marker['label'] else False
        fig.add_trace(go.Scatter(x=[marker['x']], y=[marker['y']], marker={'color': marker['color']}, showlegend=False), secondary_y=scndy)
        fig.add_annotation(x=marker['x'],
                           y=marker['y'],
                           yref='y2' if scndy else 'y',
                           text=f"{marker['label']}:{marker['y']:.1f}",
                           showarrow=False,
                           xanchor='left',
                           font=dict(color='white', size=10),
                           opacity=0.9,
                           bgcolor=marker['bc'],
                           yshift=8,
                           secondary_y=scndy)

    fig.update_traces(marker_size=8)
    fig.update_xaxes(showspikes=True, spikedash='dot', spikemode='marker+toaxis', spikethickness=1.5, spikesnap='cursor', showline=True, showgrid=True, title_text='Month')
    fig.update_yaxes(showspikes=True,
                     spikedash='dot',
                     spikemode='marker+toaxis',
                     spikethickness=1.5,
                     spikesnap='cursor',
                     showline=True,
                     showgrid=False,
                     title_text='MRR 백만원, CRR 명')
    fig.update_yaxes(title='ARPU 백만원', secondary_y=True)

    fig.update_layout(title='Monthly Recurring Revenue(MRR), Customer Retention Rate(CRR), and Average Revenue Per User(ARPU)')
    # fig.show()

    monthly_metrics.fillna(0, inplace=True)
    # display(monthly_metrics)

    # create scatter plot with line and trendline
    #   trendline_name='Trendline', labels={'x': 'Month', 'y': 'CRR'}, title='Monthly CRR')
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(x=monthly_metrics['Month'],
                   y=monthly_metrics['CRR'],
                   marker=dict(color='red', size=monthly_metrics['Unique Users'] / 10),
                   name='CRR',
                   mode='lines+markers',
                   line_color='red'))
    # fig2.add_trace(go.Scatter(x=monthly_metrics['Month'], y=monthly_metrics['CRR'], mode='lines+markers', line_color='red', name='CRR'))
    # adjust layout
    fig2.add_trace(go.Scatter(x=monthly_metrics['Month'], y=monthly_metrics['CRR'].rolling(window=3).mean(), mode='lines', line_color='blue', name='Trendline'))
    # fig2.update_traces(marker_size=5)

    fig2.update_layout(showlegend=True, hovermode='x')
    return fig, fig2
