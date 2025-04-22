import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

# Create the app and define the layout
app = dash.Dash()
app.layout = html.Div(children=[
    html.H1(children='Tabs Demo'),

    # Create the tabs
    dcc.Tabs(id='tabs', value='tab-1', children=[

        # First tab
        dcc.Tab(label='Tab 1', value='tab-1', children=[
            html.H2(children='Content of Tab 1'),
            dcc.Graph(
                id='chart1',
                figure={
                    'data': [
                        go.Bar(x=[1, 2, 3], y=[4, 1, 2], name='Bar Chart'),
                        go.Scatter(x=[1, 2, 3], y=[2, 4, 3], mode='lines', name='Line Chart')
                    ],
                    'layout': {
                        'title': 'Chart in Tab 1'
                    }
                }
            )
        ]),

        # Second tab
        dcc.Tab(label='Tab 2', value='tab-2', children=[
            html.H2(children='Content of Tab 2'),
            dcc.Graph(
                id='chart2',
                figure={
                    'data': [
                        go.Scatter(x=[1, 2, 3], y=[10, 20, 30], mode='markers', name='Scatter Chart')
                    ],
                    'layout': {
                        'title': 'Chart in Tab 2'
                    }
                }
            )
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
