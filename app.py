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
                        dcc.Link('Team Stats', href='/team-stats'),
                        dcc.Link('Player Stats', href='/player-stats')
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
                        dcc.Link('Team Stats', href='/team-stats'),
                        dcc.Link('Player Stats', href='/player-stats')
                    ]),
                    align="center",
                    no_gutters=True,
                ),
                dbc.NavbarToggler(id="navbar-toggler")
            ],
            color="dark",
            dark=True,
        ),
    dbc.Row([
        dbc.Col([
            html.H2('Team Stats'),
            dcc.Dropdown(
                id='page-1-dropdown',
                options=[{'label': i, 'value': i} for i in df['Team'].unique()],
                value=''
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='page-1-display-value')
            ])
    ])
])

layout_page_2 = html.Div([
    dbc.Navbar([
            dbc.Row(
                    dbc.Col([
                        dcc.Link('Team Stats', href='/team-stats'),
                        dcc.Link('Player Stats', href='/player-stats')
                    ]),
                    align="center",
                    no_gutters=True,
                ),
                dbc.NavbarToggler(id="navbar-toggler")
            ],
            color="dark",
            dark=True,
        ),
    html.H2('Player Stats'),
    dcc.Dropdown(
        id='page-2-dropdown',
        options=[{'label': i, 'value': i} for i in df['Player'].unique()],
        value=''
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
    if pathname == "/team-stats":
        return layout_page_1
    elif pathname == "/player-stats":
        return layout_page_2
    else:
        return layout_index


# Page 1 callbacks
@app.callback(Output('page-1-display-value', 'children'),
              Input('page-1-dropdown', 'value'))
def update_output(value):
    table = dash_table.DataTable(
        id='player-stats',
        columns=[{"name": i, "id": i} for i in df[df['Team'] == value].columns],
        data=df[df['Team'] == value].to_dict('records'),
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