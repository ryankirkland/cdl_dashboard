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
import numpy as np

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
                        dcc.Link('Player Stats', href='/player-stats'),
                        dcc.Link('League Leaders', href='/league-leaders')
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
                        dcc.Link('Player Stats', href='/player-stats'),
                        dcc.Link('League Leaders', href='/league-leaders')
                    ]),
                    align="center",
                    no_gutters=True,
                ),
                dbc.NavbarToggler(id="navbar-toggler")
            ],
            color="dark",
            dark=True,
        ),
    dbc.Row(
        dbc.Col(
            html.H2('Player Stats')
        )
    ),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='page-2-dropdown',
                options=[{'label': i, 'value': i} for i in df['Player'].unique()],
                value='',
                placeholder='Type or Select Player to View Stats'
            )
        ),
        dbc.Col(
            dcc.Dropdown(
                id='player-comp-dropdown',
                options=[{'label': i, 'value': i} for i in df['Player'].unique()],
                value='',
                placeholder='Type or Select Player to Compare Stats'
            ),
        )
    ]),
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
              Input('page-2-dropdown', 'value'),
              Input('player-comp-dropdown', 'value'), prevent_initial_call=True)
def display_value(value, player_comp=''):

    if player_comp == '':

        player_df = df[df['Player'] == value].reset_index()
    
        p1_kills = int(player_df['Kills'].sum())
        p1_deaths = int(player_df['Death'].sum())
        p1_kd = np.round(p1_kills/p1_deaths,2)

        player_event = player_df.groupby('Event').sum()

        map_group_df = player_df.groupby('Map').sum()
        vs_who_df = player_df.groupby('Vs Who').sum()

        kills_graph = go.Figure()
        kills_graph.add_trace(
            go.Bar(
                y=player_event['Kills'],
                x=player_event.index,
                name=value
            )
        )

        map_bar = go.Figure()
        map_bar.add_trace(
            go.Bar(
                y=map_group_df.index,
                x=map_group_df['Kills'],
                name=value,
                orientation='h'
            )
        )

        vs_who_bar = go.Figure()
        vs_who_bar.add_trace(
            go.Bar(
                y=vs_who_df.index,
                x=vs_who_df['Kills'],
                name=value,
                orientation='h'
            )
        )

        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H2(value),
                    html.Img(src=f'assets/{value}.png'),
                    html.H3(f'Season Kills: {p1_kills}'),
                    html.H3(f'Season Deaths: {p1_deaths}'),
                    html.H3(f'Season K/D: {p1_kd}')
                ]), 
                dbc.Col([
                    html.H2(player_comp, style={'display': None}),
                    html.H3(style={'display': None}),
                    html.H3(style={'display': None}),
                    html.H3(style={'display': None})
                ])
            ]),
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
            ])
        ])
        
    else:
        player_df = df[df['Player'] == value].reset_index()
    
        p1_kills = int(player_df['Kills'].sum())
        p1_deaths = int(player_df['Death'].sum())
        p1_kd = np.round(p1_kills/p1_deaths,2)

        player_event = player_df.groupby('Event').sum()

        map_group_df = player_df.groupby('Map').sum()
        vs_who_df = player_df.groupby('Vs Who').sum()

        kills_graph = go.Figure()
        kills_graph.add_trace(
            go.Bar(
                y=player_event['Kills'],
                x=player_event.index,
                name=value
            )
        )

        map_bar = go.Figure()
        map_bar.add_trace(
            go.Bar(
                y=map_group_df.index,
                x=map_group_df['Kills'],
                name=value,
                orientation='h'
            )
        )

        vs_who_bar = go.Figure()
        vs_who_bar.add_trace(
            go.Bar(
                y=vs_who_df.index,
                x=vs_who_df['Kills'],
                name=value,
                orientation='h'
            )
        )

        player2_df = df[df['Player'] == player_comp].reset_index()

        p2_kills = int(player2_df['Kills'].sum())
        p2_deaths = int(player2_df['Death'].sum())
        if p2_deaths > 0:
            p2_kd = np.round(p2_kills/p2_deaths,2)
        else:
            p2_kd = 0

        # table = dash_table.DataTable(
        #     id='player-stats',
        #     columns=[{"name": i, "id": i} for i in player_df.columns],
        #     data=player_df.to_dict('records'),
        #     style_cell={
        #     'whiteSpace': 'normal',
        #     'height': 'auto',
        #     'width': '400px'
        #     },
        #     css=[{
        #     'selector': '.dash-spreadsheet td div',
        #     'rule': '''
        #         line-height: 15px;
        #         max-height: 30px; min-height: 30px; height: 30px;
        #         display: block;
        #         overflow-y: hidden;
        #     '''
        #     }],
        # )

        
        player2_event = player2_df.groupby('Event').sum()

        kills_graph.add_trace(
            go.Bar(
                y=player2_event['Kills'],
                x=player2_event.index,
                name=player_comp
            )
        )


        p2_map_group_df = player2_df.groupby('Map').sum()
        p2_vs_who_df = player2_df.groupby('Vs Who').sum()

        map_bar.add_trace(
            go.Bar(
                y=p2_map_group_df.index,
                x=p2_map_group_df['Kills'],
                name=player_comp,
                orientation='h'
            )
        )

        vs_who_bar.add_trace(
            go.Bar(
                y=p2_vs_who_df.index,
                x=p2_vs_who_df['Kills'],
                name=player_comp,
                orientation='h'
            )
        )
        if p2_kills == 0:
            return html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H2(value),
                        html.H3(f'Season Kills: {p1_kills}'),
                        html.H3(f'Season Deaths: {p1_deaths}'),
                        html.H3(f'Season K/D: {p1_kd}')
                    ]), 
                    dbc.Col()
                ]),
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
                ])
            ])
        else:
            return html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H2(value),
                        html.Img(src=f'assets/{value}.png'),
                        html.H3(f'Season Kills: {p1_kills}'),
                        html.H3(f'Season Deaths: {p1_deaths}'),
                        html.H3(f'Season K/D: {p1_kd}')
                    ]), 
                    dbc.Col([
                        html.H2(player_comp),
                        html.Img(src=f'assets/{player_comp}.png'),
                        html.H3(f'Season Kills: {p2_kills}'),
                        html.H3(f'Season Deaths: {p2_deaths}'),
                        html.H3(f'Season K/D: {p2_kd}')
                    ])
                ]),
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
                ])
            ])


if __name__ == '__main__':
    app.run_server(debug=True)