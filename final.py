import base64
import datetime
import io
import dash
# from jupyter_dash import JupyterDash
from dash import no_update
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from matplotlib.pyplot import plot
import plotly.express as px

import pandas as pd


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
        multiple=True
    ),
    html.Div(id='output-plottypes'),
    html.Div(id='output-select-axis'),
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
        dcc.RadioItems(options=['lineplot', 'barplot', 'scatterplot', 'histogram'], value='lineplot', id='selectplot', inline=True),
        html.Hr(),  # horizontal line
    ])


@app.callback(Output('output-plottypes', 'children'),
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
    Output('output-select-axis', 'children'),
    Input('selectplot', 'value'),
    State('stored-data', 'data'),
    prevent_initial_call = True,
)
def select_axis(plottype, data):
        if 'hist' not in plottype.lower():
            return html.Div([html.P("Inset X axis data"),
            dcc.Dropdown(id='xaxis-data',
                        options=[x for x in list(data[0].keys())]),
            html.P("Inset Y axis data"),
            dcc.Dropdown(id='yaxis-data',
                        options=[x for x in list(data[0].keys())]),
            html.Button(id="submit-button", children="Create Graph")
            ])
        else:
            return html.Div([html.P("Inset X axis data"),
            dcc.Dropdown(id='xaxis-data',
                        options=[x for x in list(data[0].keys())]),
            html.P("Inset Y axis data"),
            dcc.Dropdown(id='yaxis-data',
                        options=[x for x in list(data[0].keys())], disabled=True),
            html.Button(id="submit-button", children="Create Graph")
            ])


@app.callback(Output('output-div', 'children'),
              Input('submit-button','n_clicks'),
              State('selectplot', 'value'),
              State('stored-data','data'),
              State('xaxis-data','value'),
              State('yaxis-data', 'value'))
              
def make_graphs(n, plottype, data, x_data, y_data):
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
