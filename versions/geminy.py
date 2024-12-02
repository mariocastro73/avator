import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import cv2
import numpy as np


app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Image Processing App"),
    html.Div([
        dcc.Upload(
            id='upload-image',
            children=html.Div([
                'Drag and drop or ',
                html.A('Select an image'),
            ]),
            multiple=False
        ),
        html.Div(id='output-image-upload'),
    ]),
    html.Div([
        html.Div([
            html.Label("Blur Level"),
            dcc.Slider(
                id='blur-level',
                min=1,
                max=9,
                step=2,
                value=3,
            ),
        ]),
        html.Div([
            html.Label("BW Threshold (Low-High)"),
            dcc.RangeSlider(
                id='bw-threshold',
                min=0,
                max=255,
                step=1,
                value=[0, 127],
            ),
        ]),
        html.Div([
            html.Label("Area Threshold (Low-High)"),
            dcc.RangeSlider(
                id='area-threshold',
                min=0,
                max=10000,
                step=10,
                value=[100, 1000],
            ),
        ]),
        html.Div([
            html.Label("Eccentricity"),
            dcc.Slider(
                id='eccentricity',
                min=0,
                max=1,
                step=0.01,
                value=0.8,
            ),
        ]),
    ]),
    html.Div([
        html.Div(id='output-image-bw-median'),
        html.Div(id='output-image-thresholded'),
        html.Div(id='output-image-detected-black'),
        html.Div(id='output-image-with-circles'),
    ]),
    html.Button(id='export-csv', children='Export CSV'),
])


@app.callback(
    Output('output-image-upload', 'children'),
    Input('upload-image', 'contents'),
    State('upload-image', 'filename'),
)
def display_uploaded_image(contents, filename):
    if contents is not None:
        img_array = cv2.imdecode(np.frombuffer(contents, dtype=np.uint8), -1)
        return html.Img(src=base64.b64encode(img_array).decode('utf-8'))
    else:
        return html.Div([])


@app.callback(
    Output('output-image-bw-median', 'children'),
    Input('upload-image', 'contents'),
    State('blur-level', 'value'),
)
def apply_median_blur(contents, blur_level):
    if contents is not None:
        img_array = cv2.imdecode(np.frombuffer(contents, dtype=np.uint8), -1)
        img_blurred = cv2.medianBlur(img_array, blur_level)
        return html.Img(src=base64.b64encode(img_blurred).decode('utf-8'))
    else:
        return html.Div([])


@app.callback(
    Output('output-image-thresholded', 'children'),
    Input('output-image-bw-median', 'children'),  # Input from previous callback
    Input('bw-threshold', 'value'),
)
def apply_threshold(img_div, threshold):
    # Decode image from base64 and convert to grayscale
    img_array = cv2.imdecode(np.frombuffer(img_div.split(',')[1], dtype=np.uint8), -1)
    img_gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

    # Apply thresholding based on slider values
    low_thresh, high_thresh = threshold
    img_thresh = cv2.threshold(img_gray, low_thresh, high_thresh, cv2.THRESH_BINARY)[1]

    # Encode and display thresholded image
    return html.Img(src=base64.b64encode(img_thresh).decode('utf-8'))


@app.callback(
    Output('output-image-detected-black', 'children'),
    Input('output-image-thresholded', 'children'),  # Input from previous callback
    Input('area-threshold', 'value'),
    Input('eccentricity', 'value'),
)
def detect_black_areas(img_div, area_threshold, eccentricity):
    # Decode image from base64
    img_array = cv2.imdecode(np.frombuffer(img_div.split(',')[1], dtype=np.uint8), -1)

    # Find contours and filter based on area and eccentricity
    contours, _ = cv2.findContours(img_array, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area_threshold[0] < area < area_threshold[1]:
            M = cv2.moments(contour)
            if M['hu'][0] < eccentricity:
                filtered_contours.append(contour)

    # Draw filtered contours on a blank image
    img_black = np.zeros_like(img_array)
    cv2.drawContours(img_black, filtered_contours, -1, (0, 0, 255), 2)

    # Encode and display image with detected areas
    return html.Img(src=base64.b64encode(img_black).decode('utf-8'))


@app.callback(
    Output('output-image-with-circles', 'children'),
    Input('upload-image', 'contents'),  # Input from initial upload
    Input('output-image-detected-black', 'children'),  # Input from previous callback
)
def draw_circles(original_contents, img_div):
    # Decode original image from base64
    original_img = cv2.imdecode(np.frombuffer(original_contents, dtype=np.uint8), -1)

    # Decode image with detected areas from base64
    img_array = cv2.imdecode(np.frombuffer(img_div.split(',')[1], dtype=np.uint8), -1)

    # Find contour moments and calculate centroid coordinates
    contours, _ = cv2.findContours(img_array, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    coordinates = []
    for contour in contours:
        M = cv2.moments(contour)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        coordinates.append((cx, cy))

    # Draw green circles on the original image at coordinates
    for x, y in coordinates:
        cv2.circle(original_img, (x, y), 5, (0, 255, 0), -1)

    # Encode and display original image with circles
    return html.Img(src=base64.b64encode(img_black).decode('utf-8'))




if __name__ == '__main__':
    app.run_server(debug=True)


