import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

import flask

import pandas as pd

external_stylesheets = [dbc.themes.YETI]

df = pd.read_csv('hp_cleaned.csv')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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

    player_df = df[df['Player'] == value].reset_index()

    table = dash_table.DataTable(
        id='player-stats',
        columns=[{"name": i, "id": i} for i in player_df.columns],
        data=player_df.to_dict('records'),
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

    kills_graph = go.Figure()
    kills_graph.add_trace(
        go.Scatter(
            y=player_df['Kills'],
            x=player_df.index,
            mode='lines+markers',
            name=f'{value} Kills'
        )
    )

    map_group_df = player_df.groupby('Map').sum()
    vs_who_df = player_df.groupby('Vs Who').sum()

    map_bar = go.Figure()
    map_bar.add_trace(
        go.Bar(
            y=map_group_df['Kills'],
            x=map_group_df.index
        )
    )

    vs_who_bar = go.Figure()
    vs_who_bar.add_trace(
        go.Bar(
            y=vs_who_df['Kills'],
            x=vs_who_df.index
        )
    )

    return html.Div([
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='kills_graph',
                    figure=kills_graph
                )
            )
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='map_bar',
                    figure=map_bar
                )
            ),
            dbc.Col(
                dcc.Graph(
                    id='vs_who_bar',
                    figure=vs_who_bar,
                )
            )
        ]),
        dbc.Row(
            dbc.Col(
                children=table,
                width={'size': 6, 'offset': 2},
                
            )
        )
    ])


if __name__ == '__main__':
    app.run_server(debug=True)