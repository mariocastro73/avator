import dash
from dash import html, dcc, Input, Output, State
from PIL import Image, ImageEnhance
import base64
from io import BytesIO

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the application
app.layout = html.Div([
    html.H1("Image Contrast Adjuster and Personalized Greeting", style={'text-align': 'center'}),
    html.P("Upload an image and adjust its contrast.", style={'text-align': 'center'}),
    dcc.Upload(
        id='upload-image',
        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    dcc.Slider(
        id='contrast-slider',
        min=0, max=100, value=50, step=1,
        marks={i: str(i) for i in range(0, 101, 10)},
    ),
    html.Div(id='output-image', style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Label("Contrast:"),
            dcc.Input(id='input-contrast', type='number', placeholder='Contrast'),
        ], style={'padding': '10px'}),
        html.Button('Submit', id='submit-button', n_clicks=0),
    ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'justify-content': 'center'}),
    html.Div(id='output-container', style={'text-align': 'center', 'margin-top': '20px'}),
])

# Adjust the contrast of the image
def adjust_contrast(image_bytes, contrast_value):
    image = Image.open(BytesIO(image_bytes))
    enhancer = ImageEnhance.Contrast(image)
    image_enhanced = enhancer.enhance(contrast_value / 50)  # Adjusting contrast
    buffered = BytesIO()
    image_enhanced.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# Callback to display the uploaded image
@app.callback(
    Output('output-image', 'children'),
    Input('upload-image', 'contents'),
    State('upload-image', 'filename'),
    Input('contrast-slider', 'value')
)
def update_output(contents, filename, contrast_value):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        adjusted_image = adjust_contrast(decoded, contrast_value)
        return html.Img(src=f'data:image/jpeg;base64,{adjusted_image}', style={'max-width': '500px', 'height': 'auto'})

# Callback to update the greeting message
@app.callback(
    Output('output-container', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('input-contrast', 'value')],
)
def update_greeting(n_clicks, contrast):
    if n_clicks > 0:
        return f'The new contrast value is {contrast}.'

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
