import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px


def plot_ga_campaigns():
    # Read the CSV data from the file
    df = pd.read_csv('report.csv')

    # Merge the firstUserSourceMedium and firstUserManualAdContent fields
    df['campaign'] = df['firstUserSourceMedium'] + ' - ' + df['firstUserManualAdContent']

    # Exclude rows containing 'direct' or 'referral' in the firstUserSourceMedium field
    df = df[~df['firstUserSourceMedium'].str.contains('direct|referral', case=False)]

    # Convert the date column to a datetime object
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

    # Create a scatter chart with the campaign key on the y-axis, date on the x-axis, and the number of new users as the marker size
    fig = px.scatter(df, x='date', y='campaign', size='userEngagementDuration', title='New Users by Date and Campaign', height=1500, color_discrete_sequence=['red'])

    # Add x and y guide lines
    fig.update_xaxes(showspikes=True, spikecolor="gray", spikemode="toaxis+across", spikesnap="cursor")
    fig.update_yaxes(showspikes=True, spikecolor="gray", spikemode="toaxis+across", spikesnap="cursor")

    return fig

# Create the app and define the layout
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            [
                # Create the sidebar menu
                dbc.Col(
                    width=3,
                    children=[
                        html.H2(children='Menu', className='text-center mb-4'),
                        dbc.Nav(
                            [
                                dbc.NavItem(dbc.NavLink('Chart 1', href='/chart-1')),
                                dbc.NavItem(dbc.NavLink('Chart 2', href='/chart-2')),
                            ],
                            vertical=True,
                            pills=True,
                        ),
                    ],
                ),

                # Create the main content area
                dbc.Col(
                    width=9,
                    children=[
                        html.H1(children='Charts'),

                        # Create the page content based on the URL
                        dcc.Location(id='url', refresh=False),
                        html.Div(id='page-content')
                    ],
                ),
            ],)
    ],
)

fig_ga = plot_ga_campaigns()


# Define the callback that updates the page content based on the URL
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/chart-1':
        return dcc.Graph(id='chart1', figure=fig_ga)
    elif pathname == '/chart-2':
        return dcc.Graph(id='chart2', figure={'data': [{'x': [1, 2, 3], 'y': [10, 20, 30], 'type': 'scatter', 'name': 'Scatter chart'}], 'layout': {'title': 'Chart 2'}})
    else:
        return html.Div([html.H2('404 Error'), html.P('The page you requested was not found.')])


if __name__ == '__main__':
    app.run_server(debug=True)