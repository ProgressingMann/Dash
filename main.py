import pandas as pd
import numpy as np
import plotly.express as px

import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table

# --------------------------------------- Upload Component Start ---------------------------------------

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)

app.layout = html.Div([ # this code section taken from Dash docs https://dash.plotly.com/dash-core-components/upload
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
# --------------------------------------- Upload Component  ---------------------------------------
    ),
    html.Div(id='select-plottype'),
    html.Div(id='select-columns'),
    html.Div(id='output-div'),
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        dcc.Store(id='stored-data', data=df.to_dict('records')),
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        dcc.RadioItems(['Lineplot', 'Scatterplot', 'Boxplot', 'Histogram'], 
        'Lineplot', inline=True, id='plottype'),
        html.Button(id="submit-button", children="Create Graph"),
        html.Hr(),
    ])


@app.callback(Output('select-plottype', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(
    Output('select-columns', 'children'),
    Input('plottype', 'value'),
    State('stored-data', 'data')
    # State('xaxis-data', 'value'),
    # State('yaxis-data', 'value')
)
def show_columns(plottype, data):
    # df = pd.DataFrame(data)
    print(plottype)
    return html.Div([
        html.P("Insert X axis data"),
        dcc.Dropdown(id='xaxis-data',
                        options=[{'label':x, 'value':x} for x in list(data[0].keys())]),
        html.P("Insert Y axis data"),
        dcc.Dropdown(id='yaxis-data',
                        options=[{'label':x, 'value':x} for x in list(data[0].keys())]),
    ])


@app.callback(Output('output-div', 'children'),
              Input('submit-button','n_clicks'),
              Input('plottype', 'value'),
              State('stored-data','data'),
              State('xaxis-data','value'),
              State('yaxis-data', 'value'))
def make_graphs(n, data, plottype, x_data, y_data):
    print(plottype)
    if n is None:
        return dash.no_update
    elif 'bar' in plottype.lower():
        bar_fig = px.bar(data, x=x_data, y=y_data)
        return dcc.Graph(figure=bar_fig)
    elif 'line' in plottype.lower():
        line_fig = px.line(data, x=x_data, y=y_data)
        return dcc.Graph(figure=line_fig)
    elif 'hist' in plottype.lower():
        line_fig = px.histogram(data, x=x_data)
        return dcc.Graph(figure=line_fig)


if __name__ == '__main__':
    app.run_server(debug=True)