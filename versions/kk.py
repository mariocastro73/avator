# Importar las librerías necesarias
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Definir el layout de la aplicación utilizando un contenedor con estilo flex
app.layout = html.Div([
    html.Div([
        # Contenedor para el Slider con un estilo específico para el ancho
        html.Div([
            dcc.Slider(
                id='mi-slider',
                min=0,
                max=20,
                step=1,
                value=10,
            )
        ], style={'width': '70%', 'marginRight': '20px', 'display': 'inline-block'}),
        # Input con un margen a la izquierda
        dcc.Input(
            id='mi-input',
            type='number',
            value=10,
            style={'width': '20%', 'display': 'inline-block'}
        )
    ], style={'display': 'flex', 'alignItems': 'center'}),  # Asegura que los elementos estén en la misma línea y centrados verticalmente
])

# Callback para actualizar el input con el valor del slider
@app.callback(
    Output('mi-input', 'value'),
    [Input('mi-slider', 'value')]
)
def update_input(value):
    return value

# Correr la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)

