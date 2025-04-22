import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

# Create a sample dataset
df = pd.DataFrame({'x': [1, 2, 3, 4, 5], 'y1': [10, 8, 6, 4, 2], 'y2': [5, 10, 5, 10, 5], 'y3': [0, 2, 4, 6, 8]})

# Create the app and define the layout
app = dash.Dash()
app.layout = html.Div(children=[
    html.H1(children='Multiple Charts'),

    # First chart
    dcc.Graph(
        id='chart1',
        figure={'data': [go.Bar(x=df['x'], y=df['y1'], name='Bar Chart'), go.Scatter(x=df['x'], y=df['y2'], mode='lines', name='Line Chart')], 'layout': {'title': 'Chart 1'}}),

    # Second chart
    dcc.Graph(id='chart2', figure={'data': [go.Scatter(x=df['x'], y=df['y3'], mode='markers', name='Scatter Chart')], 'layout': {'title': 'Chart 2'}})
])

if __name__ == '__main__':
    app.run_server(debug=True)
