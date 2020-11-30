import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import flask

import pandas as pd

df = pd.read_csv('hp_cleaned.csv')

app = dash.Dash(__name__)

url_bar_and_content_div = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

layout_index = dbc.Container([
        dbc.Navbar([
            dbc.Row(
                    dbc.Col([
                        dcc.Link('Navigate to "/page-1"', href='/page-1'),
                        dcc.Link('Navigate to "/page-2"', href='/page-2')
                    ]),
                    align="center",
                    no_gutters=True,
                ),
                dbc.NavbarToggler(id="navbar-toggler")
            ],
            color="dark",
            dark=True,
        )
    ])

layout_page_1 = html.Div([
    dbc.Navbar([
            dbc.Row(
                    dbc.Col([
                        dcc.Link('Navigate to "/page-1"', href='/page-1'),
                        dcc.Link('Navigate to "/page-2"', href='/page-2')
                    ]),
                    align="center",
                    no_gutters=True,
                ),
                dbc.NavbarToggler(id="navbar-toggler")
            ],
            color="dark",
            dark=True,
        ),
    html.H2('Page 1'),
    dcc.Input(id='input-1-state', type='text', value='Montreal'),
    dcc.Input(id='input-2-state', type='text', value='Canada'),
    html.Button(id='submit-button', n_clicks=0, children='Submit'),
    html.Div(id='output-state')
])

layout_page_2 = html.Div([
    dbc.Navbar([
            dbc.Row(
                    dbc.Col([
                        dcc.Link('Navigate to "/page-1"', href='/page-1'),
                        dcc.Link('Navigate to "/page-2"', href='/page-2')
                    ]),
                    align="center",
                    no_gutters=True,
                ),
                dbc.NavbarToggler(id="navbar-toggler")
            ],
            color="dark",
            dark=True,
        ),
    html.H2('Page 2'),
    dcc.Dropdown(
        id='page-2-dropdown',
        options=[{'label': i, 'value': i} for i in df['Player'].unique()],
        value='LA'
    ),
    html.Div(id='page-2-display-value')
])

# index layout
app.layout = url_bar_and_content_div

# "complete" layout
app.validation_layout = html.Div([
    url_bar_and_content_div,
    layout_index,
    layout_page_1,
    layout_page_2,
])


# Index callbacks
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == "/page-1":
        return layout_page_1
    elif pathname == "/page-2":
        return layout_page_2
    else:
        return layout_index


# Page 1 callbacks
@app.callback(Output('output-state', 'children'),
              Input('submit-button', 'n_clicks'),
              State('input-1-state', 'value'),
              State('input-2-state', 'value'))
def update_output(n_clicks, input1, input2):
    return ('The Button has been pressed {} times,'
            'Input 1 is "{}",'
            'and Input 2 is "{}"').format(n_clicks, input1, input2)


# Page 2 callbacks
@app.callback(Output('page-2-display-value', 'children'),
              Input('page-2-dropdown', 'value'))
def display_value(value):
    table = dash_table.DataTable(
        id='player-stats',
        columns=[{"name": i, "id": i} for i in df[df['Player'] == value].columns],
        data=df[df['Player'] == value].to_dict('records'),
        style_cell={
        'whiteSpace': 'normal',
        'height': 'auto',
        'width': '400px'
        },
        css=[{
        'selector': '.dash-spreadsheet td div',
        'rule': '''
            line-height: 15px;
            max-height: 30px; min-height: 30px; height: 30px;
            display: block;
            overflow-y: hidden;
        '''
        }],
    )
    return html.Div([
        dbc.Row(
            dbc.Col(
                children=table,
                width={'size': 6, 'offset': 2},
                
            )
        )
    ])


if __name__ == '__main__':
    app.run_server(debug=True)