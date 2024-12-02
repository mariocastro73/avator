import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import cv2
import numpy as np
import pandas as pd
import base64
import io

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dcc.Upload(
        id='upload-image',
        children=html.Button('Upload Image'),
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Br(),
    dcc.Slider(
        id='blur-level-slider',
        min=0,
        max=20,
        step=1,
        value=5,
        marks={i: str(i) for i in range(0, 21, 5)}
    ),
    dcc.Slider(
        id='bw-threshold-slider',
        min=0,
        max=255,
        step=1,
        value=127,
        marks={i: str(i) for i in range(0, 256, 25)}
    ),
    dcc.Slider(
        id='area-threshold-slider',
        min=0,
        max=10000,
        step=100,
        value=50,
        marks={i: str(i) for i in range(0, 10001, 1000)}
    ),
    html.Button('Export CSV', id='export-csv', n_clicks=0),
    html.Div(id='output-image-upload'),
    html.Div(id='output-csv', style={'display': 'none'})
])

# Define the callback for uploading images
@app.callback(
    Output('output-image-upload', 'children'),
    Input('upload-image', 'contents'),
    State('upload-image', 'filename'),
    Input('blur-level-slider', 'value'),
    Input('bw-threshold-slider', 'value'),
    Input('area-threshold-slider', 'value'),
    prevent_initial_call=True
)
def update_output(content, filename, blur_level, bw_threshold, area_threshold):
    if content is not None:
        children = [
            parse_contents(content, filename, blur_level, bw_threshold, area_threshold)
        ]
        return children

# Function to parse the uploaded image and apply transformations
def parse_contents(contents, filename, blur_level, bw_threshold, area_threshold):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    image = np.asarray(bytearray(decoded), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    # Apply median blur
    blur = cv2.medianBlur(image, blur_level if blur_level % 2 != 0 else blur_level + 1)

    # Convert to grayscale and apply binary threshold
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, bw_threshold, 255, cv2.THRESH_BINARY_INV)

    # Find contours and filter by area
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > area_threshold]

    # Draw the centers of the triangles
    centers = []
    for cnt in large_contours:
        M = cv2.moments(cnt)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            centers.append((cx, cy))
            cv2.circle(image, (cx, cy), 5, (0, 255, 0), -1)

    # Convert image to display on the web
    _, buffer = cv2.imencode('.png', image)
    image_encoded = base64.b64encode(buffer).decode('utf-8')

    # Display the images
    return html.Div([
        html.Img(src=f'data:image/png;base64,{image_encoded}', style={'width': '50%', 'display': 'inline-block'}),
    ])

# Define the callback for exporting CSV
@app.callback(
    Output('output-csv', 'children'),
    Input('export-csv', 'n_clicks'),
    State('output-image-upload', 'children'),
    prevent_initial_call=True
)
def generate_csv(n_clicks, children):
    if n_clicks > 0 and children:
        # Extracting centers from the state of the image component
        # Since this is a demo code, we will assume 'centers' is a list of tuples (x, y) coordinates
        # Here you need to implement the logic to extract centers based on your actual application state
        centers = [(100, 150), (200, 250)] # Placeholder for actual centers
        
        # Convert the centers to a DataFrame
        df = pd.DataFrame(centers, columns=['x', 'y'])
        
        # Convert the DataFrame to a CSV string
        csv_string = df.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
        
        # Return a download link for the CSV
        return html.A(
            "Download CSV",
            href=csv_string,
            download="centers.csv"
        )

# Helper function to extract centers from the image component's children
# This is a placeholder function, you'll need to replace this with actual logic
def extract_centers_from_image(children):
    # Placeholder for extracting the center coordinates
    centers = [(100, 150), (200, 250)] # Example data
    return centers

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

