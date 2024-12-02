# Importar librerías
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Definir el layout de la aplicación
app.layout = html.Div([
    dcc.Slider(
        id='mi-slider',
        min=0,
        max=20,
        step=1,
        value=10,
    ),
    dcc.Input(
        id='mi-input',
        type='number',
        value=10
    )
])

# Callback para actualizar el input basado en el slider
@app.callback(
    Output('mi-input', 'value'),
    Input('mi-slider', 'value')
)
def actualizar_input(valor_slider):
    return valor_slider

# Callback para actualizar el slider basado en el input
@app.callback(
    Output('mi-slider', 'value'),
    Input('mi-input', 'value')
)
def actualizar_slider(valor_input):
    # Convertir el valor a int para asegurar compatibilidad con el slider
    return int(valor_input) if valor_input else 0

# Correr la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
