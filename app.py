import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
#import dash_canvas

import pandas as pd
import base64
import zipfile
import json
import io
import os

import plot
import image 


app = dash.Dash(__name__)

ZIP_FILE = 1
IMAGE_FILE = 2

no_image = "/assets/no_image.jpg"
zip_image = "/assets/zip.jpg"
images_base64_dict = {}    # Diccionario de filename:base64_image
final_points = []
plot_data01 = []
plot_data02 = []
file_type = None    # values: ZIP_FILE o IMAGE_FILE


app.layout = html.Div([
    html.Div([
        html.H1("AVATOR - Assistive Visual Analysis Tool for OrigamiDNA Research"),
        html.H2("M. Castro and D. Contreras"),
    ], style={'width':'100%', 'textAlign':'center', 'margin':'auto'}),
    dcc.Upload(
        id='upload-image',
        children=html.Div(['Drag and Drop an image or a ZIP file (images) or ', html.A('Click to select it')]),
        style={
            'width': '50%', 'height': '60px', 'lineHeight': '60px', 'margin':'auto',
            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center'
        },
        multiple=False  
    ), 
    html.Div([
        html.Br(),
        html.Div([
            dcc.Upload(
                id='btn-import-parameters',
                children=html.Button('Import parameters'),
                multiple=False
                )
        ], style={'display': 'inline-block'}),
        html.Div(' ', style={'display': 'inline-block', 'margin': '0 10px'}),
        html.Div([
            html.Button("Export parameters", id="btn-export-parameters"),
            dcc.Download(id='download-parameters-json'),
        ], style={'display': 'inline-block'}),
        html.Div(' ', style={'display': 'inline-block', 'margin': '0 10%'}),
         html.Div([
            html.Button('Download points (CSV)', id='btn-export-csv', n_clicks=0),
            dcc.Download(id='download-points-csv'),
        ], style={'display': 'inline-block'}),
        html.Div(' ', style={'display': 'inline-block', 'margin': '0 10px'}),
        html.Div([
            html.Button('Show plots', id='btn-show-plots', n_clicks=0),
        ], style={'display': 'inline-block'}),

    ], style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.H2("Original image:"),
            html.Img(id='img-uploaded-image', src=no_image)
        ], style={'width': '45%', 'textAlign':'center', 'margin':'auto', 'display': 'inline-block'}),
        html.Div([
            html.H2("Blur:"),
            html.Div([
                dcc.Slider(
                    id='blur-level-slider',
                    min=0,
                    max=20,
                    step=1,
                    value=4,
                    marks={i: str(i) for i in range(0, 21, 5)}
                ),
            dcc.Input(
                id='blur-level-input',
                type='number',
                value=5,
                min=0,
                max=20,
                style={'marginLeft': '10px', 'marginBottom': '10px', 'padding': '-100px', 'width': '50px', 'display': 'inline-block'}
            ),
            # New Checkbox element for median blur
            dcc.Checklist(
                id='median-blur-checkbox',
                options=[
                    {'label': 'Apply Median Blur', 'value': 'median_blur'}
                ],
                value=[],  # Default unchecked
                labelStyle={'display': 'inline-block', 'marginLeft': '10px'}
            ),
            dcc.Store(id='median-blur-store', data={'value': True}),
            dcc.Store(id='blur-store', data={'value': 0}),
            ]), 
            html.Img(id='img-blured-image', src=no_image),
        ], style={'width': '45%', 'textAlign':'center', 'margin':'auto', 'display': 'inline-block'}),
    ], style={'width': '80%', 'marginTop':'10px', 'margin':'auto', 'display': 'block'}),
    html.Div([
        html.Div([
            html.H2("B/W Threshold:"),
            html.Div([
                dcc.Slider(
                    id='bw-threshold-slider',
                    min=1,
                    max=255,
                    step=10,
                    value=33,
                    marks={i: str(i) for i in range(0, 256, 50)}
                ),
            dcc.Input(
                id='bw-threshold-input',
                type='number',
                value=45,
                min=1,
                max=255,
                style={'marginLeft': '10px', 'marginBottom': '10px', 'padding': '-100px', 'width': '50px', 'display': 'inline-block'}
            ),
            dcc.Store(id='bw-threshold-store', data={'value': 0}),
            ]), 
            html.Img(id='img-thresholded-image', src=no_image),
        ], style={'width': '45%', 'textAlign':'center', 'margin':'auto', 'display': 'inline-block'}),
        html.Div([
            html.H2("Area:"),
            html.Div([
                dcc.RangeSlider(
                        id='area-threshold-range-slider',
                        min=0,        # Valor mínimo del slider
                        max=250,       # Valor máximo del slider
                        step=10,       # Paso entre valores consecutivos
                        value=[10, 90], # Valores iniciales (mínimo y máximo)
                        marks={i: str(i) for i in range(0, 251, 50)}
                ),
                html.Label("Min:"),
                dcc.Input(
                    id='lo-area-threshold-input',
                    type='number',
                    value=23,
                    min=0,
                    max=250,
                    style={'marginLeft': '10px', 'marginBottom': '10px', 'padding': '-100px', 'width': '50px', 'display': 'inline-block'}
                ),
                dcc.Store(id='lo-area-threshold-store', data={'value': 0}),
                html.Label(" Max:"),
                dcc.Input(
                    id='hi-area-threshold-input',
                    type='number',
                    value=46,
                    min=0,
                    max=250,
                    style={'marginLeft': '10px', 'marginBottom': '10px', 'padding': '-100px', 'width': '50px', 'display': 'inline-block'}
                ),
                dcc.Store(id='hi-area-threshold-store', data={'value': 0}),
                dcc.Slider(
                    id='ecc-threshold-slider',
                    min=0,
                    max=1,
                    step=.05,
                    value=0.7,
                    marks={i: f"{i*0.1}" for i in range(10, 1)}
                ),
            html.Label(" Eccentricity:"),
            dcc.Input(
                id='ecc-threshold-input',
                type='number',
                value=0.7,
                step=0.01,
                min=0,
                max=1,
                style={'marginLeft': '10px', 'marginBottom': '10px', 'padding': '-100px', 'width': '50px', 'display': 'inline-block'}
            ),
            dcc.Store(id='ecc-threshold-store', data={'value': 0}),
            ] ), 
            html.Img(id='img-final-image', src=no_image),
        ], style={'width': '45%', 'textAlign':'center', 'margin':'auto', 'display': 'inline-block'}),
        html.Div([
            html.H2("", style={"marginTop":"50px"}),
            dcc.Graph(id='plot-histogram'), 
        ], style={'width': '45%', 'textAlign':'center', 'margin':'auto', 'display': 'inline-block'}),
        html.Div([
            html.H2("", style={"marginTop":"50px"}),
            dcc.Graph(id='plot-time'),    
        ], style={'width': '45%', 'textAlign':'center', 'margin':'auto', 'display': 'inline-block'}),

    ], style={'width': '80%', 'marginTop':'10px', 'margin':'auto', 'display': 'block'}),
    html.Div([
        html.Div([
            html.Button("Export plot data ", id="btn-export-plot-data01", n_clicks=0),
            dcc.Download(id='download-plot-data01'),
        ], style={'display': 'inline-block'}),
        html.Div(' ', style={'display': 'inline-block', 'margin': '0 300px'}),
        html.Div([
            html.Button('Export plot data', id='btn-export-plot-data02', n_clicks=0),
            dcc.Download(id='download-plot-data02'),
        ], style={'display': 'inline-block'}),
    ], style={'textAlign': 'center'}),
])




"""
Edición de puntos
html.Div([
    html.Button('Edit final image', id='button-edit-final-image', n_clicks=0), 
    html.Div([
        dash_canvas.DashCanvas(
            id='canvas-image',
            image_content=no_image,
            width=500,  
            height=500, 
            lineWidth=15,
            lineColor='green', 
            tool='pencil', 
            hide_buttons=['line', 'rectangle', 'select']
            ),
    ], id="div-final-image"),
], style={'width': '50%', 'text-align':'center', 'margin':'auto', 'margin-top':'30px', 'display': 'block'}),
"""


@app.callback(
    Output('plot-histogram', 'figure'),
    Output('plot-time', 'figure'),
    Input('btn-show-plots', 'n_clicks'),
    prevent_initial_call=True
)

def show_plots(n_clicks):
    # print(file_type)
    if file_type == IMAGE_FILE:
        plot_image01, plot_image02 = plot.generate_plots_image(final_points, plot_data01, plot_data02)
        return plot_image01, plot_image02
    elif file_type == ZIP_FILE:
        plot_zip01, plot_zip02 = plot.generate_plots_zip(final_points, plot_data01, plot_data02)
        return plot_zip01, plot_zip02
    else:
        return None, None

"""
*****************************************
Exporta los PARÁMETROS de procesamiento
*****************************************
"""

@app.callback(
    Output('download-parameters-json', 'data'),
    Input('btn-export-parameters', 'n_clicks'),
    State('blur-level-input', 'value'),
    State('median-blur-checkbox', 'value'),
    State('bw-threshold-input', 'value'),
    State('ecc-threshold-input', 'value'),
    State('lo-area-threshold-input', 'value'),
    State('hi-area-threshold-input', 'value'),
    prevent_initial_call=True
)

def export_parameters_json(n_clicks, blur_level, median_blur, bw_threshold, ecc_threshold, lo_area_threshold, hi_area_threshold):
    if n_clicks is not None and n_clicks > 0:
        data = {"blur_level" : blur_level,
    #            "median_blur" : median_blur,
                "bw_threshold":bw_threshold,
                "ecc_threshold":ecc_threshold,
                "lo_area_threshold" : lo_area_threshold, 
                "hi_area_threshold" : hi_area_threshold
        }
        
        return dcc.send_string(json.dumps(data, indent=4), "parameters.json")


"""
*****************************************
Importa los PARAMETROS de procesamiento
*****************************************
"""
i = 0

@app.callback(
    #Output('blur-level-input', 'value'),
    #Output('bw-threshold-input', 'value'),
    #Output('lo-area-threshold-input', 'value'),
    #Output('hi-area-threshold-input', 'value'),
    Output("blur-store", "data"),
   # Output("median-blur-store", "data"),
    Output("bw-threshold-store", "data"),
    Output("ecc-threshold-store", "data"),
    Output("lo-area-threshold-store", "data"),
    Output("hi-area-threshold-store", "data"),
    Output("btn-import-parameters", "contents"),
    Input('btn-import-parameters', 'contents'),
    prevent_initial_call=True
)

def import_parameters_json(uploaded_file): #, blur_store_value, median_blur_store_value, bw_threshold_value,  ecc_threshold_value, lo_area_threshold_store_value, hi_area_threshold_store_value):
    print(f"uploaded file:{uploaded_file}")
    if uploaded_file is None:
        raise PreventUpdate
    content_type, content_string = uploaded_file.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'application/json' in content_type or 'text/plain' in content_type:
            data = json.loads(decoded.decode('utf-8'))
            bl = data["blur_level"] if data["blur_level"] is not None else 0
            #ml = data["median_blur"] if data["median_blur"] is not None else 0
            bw = data["bw_threshold"] if data["bw_threshold"] is not None else 0
            ecc = data["ecc_threshold"] if data["ecc_threshold"] is not None else 0
            lo = data["lo_area_threshold"] if data["lo_area_threshold"] is not None else 0
            hi = data["hi_area_threshold"] if data["hi_area_threshold"] is not None else 0
            return {"value": bl}, {"value": bw}, {"value": ecc}, {"value": lo}, {"value": hi}, None
            #return {"value": bl}, {"value": ml}, {"value": bw}, {"value": ecc}, {"value": lo}, {"value": hi}, None
        else:
            return {"value": 0}, {"value": 0}, {"value": 0}, {"value": 0}, {"value": 0}, None
    except Exception:
        return {"value": 0}, {"value": 0}, {"value": 0}, {"value": 0}, None

"""
***************************************
Muestra la imagen en la IMAGEN ORIGINAL
***************************************
"""
@app.callback(
    Output('img-uploaded-image', 'src'),
    Input('upload-image', 'contents')
)
def show_original_image(contents):
    global images_base64, file_type
    if contents is None:
        raise PreventUpdate
    else:
        content_type, content_string = contents.split(',')
        if "image" in content_type:
            file_type = IMAGE_FILE
            return contents
        elif "zip" in content_type:
            file_type = ZIP_FILE
            images_base64 = unzip(content_string)
            return zip_image

"""
***************************************
Sincroniza el Slider del BLUR y su Input 
***************************************
"""
@app.callback(
    [Output('blur-level-slider', 'value'),
     Output('blur-level-input', 'value')],
    [Input('blur-level-slider', 'value'),
     Input('blur-level-input', 'value'),
     Input("blur-store", "data"),
     Input("median-blur-store", "data")],
     prevent_initial_call=True
     #,
     #[State('blur-level-slider', 'value'),
     #State('blur-level-input', 'value')]
)

def update_blur(value_slider, value_input, blur_store_data, median_blur_store_data): #, state_slider, state_input):
    ctx = dash.callback_context
    if not ctx.triggered:
        input_id = 'No inputs yet'
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if input_id == 'blur-level-slider':
        return value_slider, value_slider
    elif input_id == 'blur-level-input':
        return value_input, value_input
    elif input_id == 'blur-store':
        return blur_store_data['value'], blur_store_data['value']
    elif input_id == 'median-blur-store':
        return median_blur_store_data['value'],median_blur_store_data['value']
    else:
        return None, None
    

"""
***************************************
Sincroniza el Slider del BW y su Input 
***************************************
"""
@app.callback(
    [Output('bw-threshold-slider', 'value'),
     Output('bw-threshold-input', 'value')],
    [Input('bw-threshold-slider', 'value'),
     Input('bw-threshold-input', 'value'),
     Input("bw-threshold-store", "data")],
    [State('bw-threshold-slider', 'value'),
     State('bw-threshold-input', 'value')]
)

def update_threshold(value_slider, value_input, bw_threshold_data, state_slider, state_input):
    ctx = dash.callback_context

    if not ctx.triggered:
        input_id = 'No inputs yet'
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if input_id == 'bw-threshold-slider':
        return value_slider, value_slider
    elif input_id == 'bw-threshold-input':
        return value_input, value_input
    elif input_id == 'bw-threshold-store':
        return bw_threshold_data['value'], bw_threshold_data['value']    
    else:
        return state_slider, state_input
"""
***************************************
Sincroniza el Slider del Ecc y su Input 
***************************************
"""
@app.callback(
    [Output('ecc-threshold-slider', 'value'),
     Output('ecc-threshold-input', 'value')],
    [Input('ecc-threshold-slider', 'value'),
     Input('ecc-threshold-input', 'value'),
     Input("ecc-threshold-store", "data")],
    [State('ecc-threshold-slider', 'value'),
     State('ecc-threshold-input', 'value')]
)

def update_eccentricity(value_slider, value_input, ecc_threshold_data, state_slider, state_input):
    ctx = dash.callback_context

    if not ctx.triggered:
        input_id = 'No inputs yet'
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if input_id == 'ecc-threshold-slider':
        return value_slider, value_slider
    elif input_id == 'ecc-threshold-input':
        return value_input, value_input
    elif input_id == 'ecc-threshold-store':
        return ecc_threshold_data['value'], ecc_threshold_data['value']    
    else:
        return state_slider, state_input

"""
***************************************
Sincroniza el Slider del AREA y su Input
*************************************** 
"""
@app.callback(
    [Output('area-threshold-range-slider', 'value'),
     Output('lo-area-threshold-input', 'value'),
     Output('hi-area-threshold-input', 'value')],
    [Input('area-threshold-range-slider', 'value'),
     Input('lo-area-threshold-input', 'value'),
     Input('hi-area-threshold-input', 'value'),
     Input("lo-area-threshold-store", "data"),
     Input("hi-area-threshold-store", "data")],
    [State('area-threshold-range-slider', 'value'),
     State('lo-area-threshold-input', 'value'),
     State('hi-area-threshold-input', 'value')]
)

def update_area(range_values, min_value, max_value, lo_area_threshold_data, hi_area_threshold_data, state_slider, state_input_min, state_input_max):
    ctx = dash.callback_context
    if not ctx.triggered:
        input_id = 'No inputs yet'
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if input_id == 'area-threshold-range-slider':
        return [range_values, range_values[0], range_values[1]]
    elif input_id == 'lo-area-threshold-input' or input_id == 'hi-area-threshold-input':
        min_value_final = min(min_value if min_value is not None else range_values[0],
                 max_value if max_value is not None else range_values[1])
        max_value_final = max(min_value if min_value is not None else range_values[0],
                 max_value if max_value is not None else range_values[1])
        return [ [min_value_final, max_value_final], min_value_final, max_value_final]
    elif input_id == 'lo-area-threshold-store' or input_id == 'hi-area-threshold-store':
        return [ [lo_area_threshold_data['value'], hi_area_threshold_data['value']], lo_area_threshold_data['value'], hi_area_threshold_data['value']]
    else:
        return [state_slider, state_input_min, state_input_max]
    

"""
******************************************************************************
Procesa las imágenes al subir una imagen o actualizar los valores de los parámetros
*************************************** ***************************************
"""
@app.callback(
    Output('img-blured-image', 'src'),
    Output('img-thresholded-image', 'src'),
    Output('img-final-image', 'src'),
    Input('img-uploaded-image', 'src'),    
    Input('blur-level-slider', 'value'),
    Input('median-blur-checkbox', 'value'),
    Input('bw-threshold-slider', 'value'),
    Input('ecc-threshold-slider', 'value'),
    Input('area-threshold-range-slider', 'value'),
    prevent_initial_call=True
)

def update_image_processing(content, blur_level, median_blur, bw_threshold, ecc_threshold, area_threshold_range):
    if content is not None and content != no_image:
        final_points.clear()
        if content == zip_image:
            for filename, content in images_base64_dict.items():
                print(f"Processing ZIP: {filename}")
                image.processing_image(content, filename, blur_level, median_blur, bw_threshold, ecc_threshold, area_threshold_range[0], area_threshold_range[1], final_points)
            return [zip_image, zip_image, zip_image]
        else:
            print("Processing 1 Image...")
            children = parse_contents(content, "Image", blur_level, median_blur, bw_threshold, ecc_threshold, area_threshold_range[0], area_threshold_range[1])
            return children
    else:
        return [no_image, no_image, no_image]


def parse_contents(content, filename, blur_level, median_blur, bw_threshold, ecc_threshold, lo_area_threshold, hi_area_threshold):
    blurred_image_encoded, threshold_image_encoded, final_image_encoded = image.processing_image(content, filename, blur_level, median_blur, bw_threshold, ecc_threshold, lo_area_threshold, hi_area_threshold, final_points)

    return [
        f'data:image/png;base64,{blurred_image_encoded}', 
        f'data:image/png;base64,{threshold_image_encoded}',
        f'data:image/png;base64,{final_image_encoded}',
    ]

@app.callback(
    Output('download-points-csv', 'data'),
    Input('btn-export-csv', 'n_clicks')
)

def generate_csv(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        df = pd.DataFrame(final_points, columns=['filename', 'x', 'y'])
        return dcc.send_data_frame(df.to_csv, "points.csv", index=False)

        """
        # Convert the DataFrame to a CSV string
        csv_string = df.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
        
        # Return a download link for the CSV
        return html.A(
            "Download points",
            href=csv_string,
            download="centers.csv"
        )
        """


@app.callback(
    Output('download-plot-data01', 'data'),
    Input('btn-export-plot-data01', 'n_clicks')
)

def download_plot_data01(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        df = pd.DataFrame(plot_data01 , columns=['neighbors', 'count'])
        df = df.astype({'neighbors': 'int64', 'count': 'int64'}) 
        return dcc.send_data_frame(df.to_csv, "plot-data01.csv", index=False)
    
@app.callback(
    Output('download-plot-data02', 'data'),
    Input('btn-export-plot-data02', 'n_clicks')
)

def download_plot_data02(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        df = pd.DataFrame(plot_data02) #, columns=['filename', 'x', 'y'])
        return dcc.send_data_frame(df.to_csv, "plot-data02.csv", index=False)


def unzip(zip_content_string:str)->list:
    decoded_zip = base64.b64decode(zip_content_string)
    try:
        with zipfile.ZipFile(io.BytesIO(decoded_zip), 'r') as zip_file:
            zipped_files = zip_file.namelist()
            images = [file for file in zipped_files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            images_base64_dict.clear()
            for image_filename in images:
                image_data = zip_file.read(image_filename)
                base64_image = base64.b64encode(image_data).decode('utf-8')
                src = f"data:image/png;base64,{base64_image}"
                images_base64_dict[image_filename] = src
            return images_base64_dict
    except Exception as e:
        raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True) # , host='0.0.0.0', port=port)
    #app.run_server(debug=True, host='0.0.0.0', port=8000)

