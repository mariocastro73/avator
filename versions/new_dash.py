import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import cv2
import numpy as np
import pandas as pd
import base64
from io import BytesIO

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = dbc.Container(fluid=True, children=[
    dbc.Row([
        dbc.Col(dcc.Upload(
            id='upload-image',
            children=html.Div(['Drag and Drop or ', html.A('Select an Image')]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=False
        ), width=12),
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='original-image-container', children='Original Image'), width=6),
        dbc.Col(html.Div(id='bw-median-blurred-image-container', children='BW Median Blurred Image'), width=6),
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='thresholded-image-container', children='Thresholded Image'), width=6),
        dbc.Col(html.Div(id='detected-black-areas-container', children='Detected Black Areas'), width=6),
    ]),
    dbc.Row([
        dbc.Col(dbc.Input(id='blur-level', type='number', placeholder='Blur Level'), width=4),
        dbc.Col(dcc.RangeSlider(id='bw-threshold', min=0, max=255, step=1, value=[100, 200], marks={i: str(i) for i in range(0, 256, 50)}), width=4),
        dbc.Col(dcc.RangeSlider(id='area-threshold', min=0, max=10000, step=100, value=[500, 5000], marks={i: str(i) for i in range(0, 10001, 2000)}), width=4),
    ]),
    dbc.Row([
        dbc.Col(dcc.Slider(id='eccentricity', min=0, max=1, step=0.01, value=0.5, marks={i/10: str(i/10) for i in range(0, 11, 2)}), width=12),
    ]),
    dbc.Row([
        dbc.Col(html.Button('Export CSV', id='export-csv', n_clicks=0), width=12),
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='original-image-with-circles-container', children='Original Image withpip  Circles at Coordinates'), width=12),
    ]),
    dcc.Download(id="download-csv")
])


@app.callback(
    Output('original-image-container', 'children'),
    Input('upload-image', 'contents')
)
def update_output(list_of_contents):
    if list_of_contents is not None:
        children = html.Img(src=list_of_contents, style={'width': '100%', 'height': 'auto'})
        return children
    return "Upload an Image"


if __name__ == '__main__':
    app.run_server(debug=True)
