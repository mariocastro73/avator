from dash import html

# URL de Bootstrap CDN para incluir Bootstrap 4
bootstrap_cdn = "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"

# Lista de hojas de estilo externas
external_stylesheets = [bootstrap_cdn]

# Inicializar la aplicación Dash con external_stylesheets
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# Definir el layout de la aplicación utilizando clases de Bootstrap
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H3('Celda 1'),
            html.P('Contenido de la celda 1...'),
        ], className='col-md-6'), # Clase de Bootstrap para columnas
        html.Div([
            html.H3('Celda 2'),
            html.P('Contenido de la celda 2...'),
        ], className='col-md-6'), # Clase de Bootstrap para columnas
    ], className='row'), # Clase de Bootstrap para filas

    html.Div([
        html.Div([
            html.H3('Celda 3'),
            html.P('Contenido de la celda 3...'),
        ], className='col-md-6'), # Clase de Bootstrap para columnas
        html.Div([
            html.H3('Celda 4'),
            html.P('Contenido de la celda 4...'),
        ], className='col-md-6'), # Clase de Bootstrap para columnas
    ], className='row') # Clase de Bootstrap para filas
])
