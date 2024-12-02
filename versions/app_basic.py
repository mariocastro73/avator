import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the application
app.layout = html.Div([
    dcc.Input(
        id='number-input', 
        type='number', 
        placeholder='Enter a number'
    ),
    html.Button('Submit', id='submit-val', n_clicks=0),
    html.Div(id='number-output', children='Your number will appear here')
])

# Callback to update the output div with the entered number
@app.callback(
    Output('number-output', 'children'),
    Input('submit-val', 'n_clicks'),
    State('number-input', 'value')
)
def update_output(n_clicks, text_input):
    #if n_clicks > 0:
    return f'You entered: {text_input} - {n_clicks}'
    #return f'You entered: {value}'
    #else:
    #    return 'Your number will appear here'

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
