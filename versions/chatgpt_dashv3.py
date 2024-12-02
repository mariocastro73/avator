import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import cv2
import numpy as np
import pandas as pd
import base64
import urllib.parse

import io

# Initialize the Dash app
app = dash.Dash(__name__)

no_image = "/assets/no_image.jpg"
final_points = []

app.layout = html.Div([
    html.Div([
        html.H1("Triangulitos Detection :)"),
        html.H2("Bla, bla, bla, bla, ..."),
    ], style={'width':'100%', 'text-align':'center', 'margin':'auto'}),
    dcc.Upload(
        id='upload-image',
        children=html.Div(['Drag and Drop the image or ', html.A('Click to select it')]),
        style={
            'width': '50%', 'height': '60px', 'lineHeight': '60px', 'margin':'auto',
            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center'
        },
        multiple=False  
    ), 
    html.Div([
        html.Div([
            html.H2("Original image:"),
            html.Img(id='img-uploaded-image', src=no_image)
        ], style={'width': '45%', 'text-align':'center', 'margin':'auto', 'display': 'inline-block'}),
        html.Div([
            html.H2("Blur:"),
            html.Div([
                dcc.Slider(
                    id='blur-level-slider',
                    min=0,
                    max=20,
                    step=1,
                    value=5,
                    marks={i: str(i) for i in range(0, 21, 5)}
                )
            ], style={'width': '50%', 'marginRight': '20px', 'display': 'inline-block'}),
            dcc.Input(
                id='blur-level-input',
                type='number',
                value=5,
                min=0,
                max=20,
                style={'margin-left': '10px', 'margin-bottom': '10px', 'padding': '-100px', 'width': '50px', 'display': 'inline-block'}
            ),
            dcc.Store(id='blur-shared-data', data={'value': 5}),
            html.Img(id='img-blured-image', src=no_image),
        ], style={'width': '45%', 'text-align':'center', 'margin':'auto', 'display': 'inline-block'}),
    ], style={'width': '80%', 'margin-top':'10px', 'margin':'auto', 'display': 'block'}),
    html.Div([
        html.Div([
            html.H2("B/W Threshold:"),
            html.Div([
                dcc.Slider(
                    id='bw-threshold-slider',
                    min=1,
                    max=255,
                    step=10,
                    value=21,
                    marks={i: str(i) for i in range(0, 256, 50)}
                )
            ], style={'width': '50%', 'marginRight': '20px', 'display': 'inline-block'}),
            dcc.Input(
                id='bw-threshold-input',
                type='number',
                value=21,
                min=1,
                max=255,
                style={'margin-left': '10px', 'margin-bottom': '10px', 'padding': '-100px', 'width': '50px', 'display': 'inline-block'}
            ),
            html.Img(id='img-thresholded-image', src=no_image),
        ], style={'width': '45%', 'text-align':'center', 'margin':'auto', 'display': 'inline-block'}),
        html.Div([
            html.H2("Area:"),
            html.Div([
                dcc.Slider(
                    id='area-threshold-slider',
                    min=0,
                    max=200,
                    step=10,
                    value=50,
                    marks={i: str(i) for i in range(0, 201, 50)}
                )
            ], style={'width': '50%', 'marginRight': '20px', 'display': 'inline-block'}),
            dcc.Input(
                id='area-threshold-input',
                type='number',
                value=50,
                min=0,
                max=10000,
                style={'margin-left': '10px', 'margin-bottom': '10px', 'padding': '-100px', 'width': '50px', 'display': 'inline-block'}
            ),
            html.Img(id='img-final-image', src=no_image),
        ], style={'width': '45%', 'text-align':'center', 'margin':'auto', 'display': 'inline-block'}),
    ], style={'width': '80%', 'margin-top':'10px', 'margin':'auto', 'display': 'block'}),
    html.Div([
        html.Button('Export CSV', id='export-csv', n_clicks=0),
        #html.Div(id='output-image-upload'),
        html.Div(id='output-csv')
    ], style={'width': '50%', 'text-align':'center', 'margin':'auto', 'margin-top':'30px', 'display': 'block'}),
])

"""
Muestra la imagen en la IMAGEN ORIGINAL 
"""
@app.callback(
    Output('img-uploaded-image', 'src'),
    Input('upload-image', 'contents')
)
def update_output(contents):
    if contents is None:
        raise PreventUpdate
    return contents

"""
Sincroniza el Slider del BLUR y su Input 
"""
@app.callback(
    Output('blur-level-input', 'value'),
    Input('blur-level-slider', 'value')
)
def update_input_blur(value):
    return value

@app.callback(
    Output('blur-level-slider', 'value'),
    Input('blur-level-input', 'value')
)
def update_slider_blur(value):
    return value


"""
Sincroniza el Slider del BW y su Input 
"""
@app.callback(
    Output('bw-threshold-input', 'value'),
    Input('bw-threshold-slider', 'value')
)
def update_input_bw(value):
    return value

@app.callback(
    Output('bw-threshold-slider', 'value'),
    Input('bw-threshold-input', 'value')
)
def update_slider_bw(value):
    return value


"""
Sincroniza el Slider del AREA y su Input 
"""
@app.callback(
    Output('area-threshold-input', 'value'),
    Input('area-threshold-slider', 'value')
)
def update_input(value):
    return value

@app.callback(
    Output('area-threshold-slider', 'value'),
    Input('area-threshold-input', 'value')
)
def update_slider(value):
    return value


# Callbacks to update each image
@app.callback(
    Output('img-blured-image', 'src'),
    Output('img-thresholded-image', 'src'),
    Output('img-final-image', 'src'),
    Input('upload-image', 'contents'),
    State('upload-image', 'filename'),
    Input('blur-level-slider', 'value'),
    Input('bw-threshold-slider', 'value'),
    Input('area-threshold-slider', 'value'),
    prevent_initial_call=True
)
def update_output(content, filename, blur_level, bw_threshold, area_threshold):
    if content is not None:
        children = parse_contents(content, filename, blur_level, bw_threshold, area_threshold)
        return children
    else:
        return [no_image, no_image, no_image]

def parse_contents(contents, filename, blur_level, bw_threshold, area_threshold):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    image = np.asarray(bytearray(decoded), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    # Original image for display
    original_image_encoded = encode_image_for_display(image)

    # Apply median blur
    blurred = cv2.medianBlur(image, blur_level if blur_level % 2 != 0 else blur_level + 1)
    blurred_image_encoded = encode_image_for_display(blurred)

    # Convert to grayscale and apply binary threshold
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, bw_threshold, 255, cv2.THRESH_BINARY)
    threshold_image_encoded = encode_image_for_display(thresh)

    # Find contours and filter by area
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > area_threshold]

    final_points.clear()

    # Draw the centers of the triangles
    for cnt in large_contours:
        M = cv2.moments(cnt)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            final_points.append((cx, cy))
            cv2.circle(image, (cx, cy), 5, (0, 255, 0), -1)

    final_image_encoded = encode_image_for_display(image)

    return [
        f'data:image/png;base64,{blurred_image_encoded}', 
        f'data:image/png;base64,{threshold_image_encoded}',
        f'data:image/png;base64,{final_image_encoded}'
    ]

# Helper function to encode an image for display in Dash
def encode_image_for_display(image):
    _, buffer = cv2.imencode('.png', image)
    encoded = base64.b64encode(buffer).decode('utf-8')
    return encoded


# Define the callback for exporting CSV
@app.callback(
    Output('output-csv', 'children'),
    Input('export-csv', 'n_clicks')
)
def generate_csv(n_clicks):
    if n_clicks > 0:
        # Convert the centers to a DataFrame
        df = pd.DataFrame(final_points, columns=['x', 'y'])
        
        # Convert the DataFrame to a CSV string
        csv_string = df.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
        
        # Return a download link for the CSV
        return html.A(
            "Download points",
            href=csv_string,
            download="centers.csv"
        )

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

