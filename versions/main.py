import dash
from dash import html, dcc, Input, Output, State
import base64
from io import BytesIO
from PIL import Image, ImageEnhance

# OpenCV

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the application
app.layout = html.Div([
    dcc.Upload(
        id='upload-image',
        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
        style={
            'width': '50%', 'height': '60px', 'lineHeight': '60px', 'margin':'auto',
            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center'
        },
        multiple=False  # Allow only one file to be uploaded
    ),
    html.Div([
        html.H3("Contrast:"),
        dcc.Slider(
            id='contrast-slider',
            min=0, max=200, value=100, step=10,
            marks={i: str(i) for i in range(0, 201, 25)},
        ),
        dcc.Input(
            id='contrast-input',
            type='number',
            value=100,
            style={'margin': '10px', 'width': '50px'}
        ),
    ], style={'width': '50%', 'text-align':'center', 'margin':'auto'}),
    html.Div(id='output-image-container', style={'width': '50%', 'text-align':'center', 'margin':'auto'})
])

def adjust_contrast(image_str, contrast_value):
    decoded_image = base64.b64decode(image_str)
    image = Image.open(BytesIO(decoded_image))
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(contrast_value / 100)
    buffered = BytesIO()
    enhanced_image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# Callbacks to update the image and inputs
@app.callback(
    Output('output-image-container', 'children'),
    [Input('upload-image', 'contents'),
     Input('contrast-slider', 'value'),
     Input('contrast-input', 'value')]
)
def update_output(contents, slider_value, input_value):
    ctx = dash.callback_context
    if not ctx.triggered:
        input_id = 'No input yet'
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if contents is None:
        return None

    if input_id == 'contrast-slider':
        contrast_value = slider_value
    else:  # This handles both initial load and direct input changes
        contrast_value = input_value

    image_str = contents.split(',')[1]
    enhanced_image_str = adjust_contrast(image_str, contrast_value)

    return html.Img(src=f'data:image/jpeg;base64,{enhanced_image_str}', style={'max-width': '500px', 'height': 'auto'})

@app.callback(
    [Output('contrast-slider', 'value'),
     Output('contrast-input', 'value')],
    [Input('contrast-slider', 'value'),
     Input('contrast-input', 'value')]
)
def sync_inputs(slider_value, input_value):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if input_id == 'contrast-slider':
        return slider_value, slider_value
    else:
        return input_value, input_value

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

