import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

mapbox_access_token = "pk.eyJ1IjoibG9pY2JhY2hlbG90IiwiYSI6ImNraGc0bmdnOTBveWoyeW80ZDU1Z2EzY2kifQ.mOX2igWQn0uH5HJusetcqA"
mapbox_style = "dark"  # "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN])

server = app.server

df = pd.read_csv('data/meteorites.csv').sort_values(by=['year'])

dropdown_opt = [
    {"label": str(name), "value": str(name)}
    for name in ['Country', 'Population', 'Area (km sq)',
                 'Pop. Density (per sq. km.)', 'GDP ($ per capita)', 'Climate', 'Region',
                 'fall', 'count']
]

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            className="jumbotron",
            style={
                'padding': '0rem 2rem',
                'marginBottom': '0rem',
            },
            children=[
                html.H1(children="Meteorites landing"),
                html.P(
                    id="description",
                    children="The data are the meteorites landing data coming from the NASA open data:",
                ),
            ],
        ),
        dbc.Container(
            id="app-container",
            fluid=True,
            children=[
                dbc.Row(
                    children=[
                        dbc.Col(
                            id="left-column",
                            align='center',
                            children=[
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            id='control-panel',
                                            children=[
                                                dbc.Row(
                                                    children=[
                                                        dbc.Col([
                                                            dbc.FormGroup(
                                                                children=[
                                                                    dcc.RangeSlider(
                                                                        id='year-range-slider',
                                                                        min=df['year'].min(),
                                                                        max=df['year'].max(),
                                                                        step=1,
                                                                        value=[df['year'].min(), df['year'].max()],
                                                                        updatemode='mouseup',
                                                                        pushable=True,
                                                                        tooltip=dict(
                                                                            always_visible=True,
                                                                        )
                                                                    ),
                                                                    dbc.Label(
                                                                        "Filter by discovery year (or select range on the Landing/Year graph)",
                                                                        html_for='year-range-slider'),
                                                                ]),
                                                        ],
                                                            align='center',
                                                        ),
                                                        dbc.Col(
                                                            dbc.FormGroup(
                                                                children=[
                                                                    dbc.Label("Select the type of meteorites"),
                                                                    dbc.Checklist(
                                                                        id='seen-found-check',
                                                                        options=[
                                                                            {'label': 'Found', 'value': 'Found'},
                                                                            {'label': 'Seen', 'value': 'Fell'},
                                                                        ],
                                                                        value=['Found', 'Fell'],
                                                                        inline=False,
                                                                    ),
                                                                ],
                                                            )
                                                        ),
                                                        dbc.Col([
                                                            dbc.Label("Type of map"),
                                                            dbc.RadioItems(
                                                                options=[
                                                                    {"label": "Dark mode", "value": 'dark'},
                                                                    {"label": "Topographic map", "value": 'stamen-terrain'},
                                                                ],
                                                                value='dark',
                                                                id="type-map",
                                                            ),
                                                        ])
                                                    ]),
                                            ]),
                                        dbc.CardBody(
                                            dcc.Graph(
                                                id='graph-map',
                                                style={'height': '50vh'}
                                            )
                                        )
                                    ]
                                ),
                            ]),
                        dbc.Col(
                            id="right-column",
                            align='center',
                            children=[
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            id="graph-container",
                                            children=[
                                                dbc.Row(
                                                    children=[
                                                        dbc.Col([
                                                            dbc.Label("Graph controls"),
                                                            dbc.Checklist(
                                                                options=[
                                                                    {"label": "Log scale Y axis",
                                                                     "value": 'log'},
                                                                    # {"label": "Option 2", "value": 2},
                                                                ],
                                                                value=[],
                                                                id="graph-input",
                                                                switch=True,
                                                            )]),
                                                        dbc.Col([
                                                            html.P(id="chart-selector", children="Select x:"),
                                                            dcc.Dropdown(
                                                                options=dropdown_opt,
                                                                value="Country",
                                                                id="chart-dropdown",
                                                                clearable=False,
                                                                style={
                                                                    'color': 'black'
                                                                }
                                                            ),
                                                        ]),
                                                    ]),
                                            ]),
                                        dbc.CardBody(
                                            dcc.Graph(
                                                id="barchart",
                                                style={'height': '50vh'}
                                            ),
                                        ),
                                    ]),

                            ],
                        ),
                    ]),
                dbc.Row(
                    dbc.Col(
                        dbc.Card(
                            dcc.Graph(
                                id="year-chart",
                                config={
                                    'displayModeBar': False
                                }
                            ),
                            body=True,
                            style={
                                'marginTop': '5px'
                            }

                        ),
                    ),
                )
            ])
    ])


def get_filtered_df(years, fall):
    # filter year range
    df_filter = df[(df["year"] >= years[0]) & (df["year"] <= years[1])]

    # filter seen_found
    df_filter = df_filter[df_filter["fall"].isin(fall)]
    return df_filter


def get_by_country(years, fall):
    df_by_country = get_filtered_df(years, fall)
    df_by_country = df_by_country.groupby(
        ['Country', 'ISO 3166-1 alpha-3', 'Population', 'Area (km sq)', 'Pop. Density (per sq. km.)',
         'GDP ($ per capita)', 'Climate', 'Region', 'fall'])[['fall']].count()
    df_by_country.rename(columns={"fall": 'count'}, inplace=True)
    df_by_country = df_by_country.reset_index()
    df_by_country.sort_values(by='count', inplace=True)
    return df_by_country


def get_by_climate(years, fall):
    df_climate = get_by_country(years, fall).groupby(['Climate'])[['count', 'Area (km sq)']].sum().reset_index()
    df_climate.rename(columns={"name": "count"}, inplace=True)
    df_climate.sort_values(by='count', inplace=True)
    df_climate['density'] = df_climate['count'] / df_climate['Area (km sq)']
    return df_climate


def get_by_years(years, fall):
    df_years = get_filtered_df(years, fall)
    df_years = df_years.groupby(['year', 'fall'])['name'].count().reset_index()
    df_years.rename(columns={"name": "count"}, inplace=True)
    df_years.sort_values(by='year', inplace=True)
    return df_years


@app.callback(
    dash.dependencies.Output('graph-map', 'figure'),
    [dash.dependencies.Input('year-range-slider', 'value'),
     dash.dependencies.Input('seen-found-check', 'value'),
     dash.dependencies.Input('type-map', 'value')],
    [dash.dependencies.State('graph-map', "relayoutData")]
)
def update_graph(years, fall, map_style, graph_layout):
    df_filter = get_filtered_df(years, fall)

    if map_style == 'dark':
        marker_color = 'rgb(206, 118, 100)'
    else:
        marker_color = 'rgba(99, 110, 250, 100)'

    trace = [
        dict(
            type="scattermapbox",
            lat=df_filter.reclat,
            lon=df_filter.reclong,
            text=df_filter.year,
            hoverinfo='text',
            mode='markers',
            marker=dict(
                size=5,
                color=marker_color,
                opacity=0.4),
        )
    ]

    lat = 0
    lon = 0
    zoom = 0.5
    if graph_layout is not None:
        if "mapbox.center" in graph_layout.keys():
            lon = float(graph_layout["mapbox.center"]["lon"])
            lat = float(graph_layout["mapbox.center"]["lat"])
            zoom = float(graph_layout["mapbox.zoom"])

    layout = dict(
        hovermode='closest',
        margin=dict(r=0, l=0, t=0, b=0),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=lat,
                lon=lon,
            ),
            zoom=zoom,
            style=map_style,
        ),
    )
    fig = dict(data=trace, layout=layout)
    return fig


@app.callback(
    dash.dependencies.Output("barchart", "figure"),
    [dash.dependencies.Input("chart-dropdown", "value"),
     dash.dependencies.Input("year-range-slider", "value"),
     dash.dependencies.Input('seen-found-check', 'value'),
     dash.dependencies.Input('graph-input', 'value')],
)
def display_barchart(chart_dropdown, years, fall, graph_input):
    df_country = get_by_country(years, fall)
    if chart_dropdown in ['Population', 'Area (km sq)',
                          'Pop. Density (per sq. km.)', 'GDP ($ per capita)']:
        type_graph = 'scatter'
        mode_graph = 'markers'
    else:
        type_graph = 'bar'
        mode_graph = 'none'

    yaxis_type = ''
    if 'log' in graph_input:
        yaxis_type = 'log'

    trace = []
    for i in fall:
        trace.append(
            dict(
                type=type_graph,
                mode=mode_graph,
                x=df_country[df_country['fall'] == i][chart_dropdown],
                y=df_country[df_country['fall'] == i]["count"],
                name=i,
            )
        )

    layout = dict(
        margin=dict(r=0, l=30, t=0),
        paper_bgcolor='rgba(0, 0, 0, 100)',
        plot_bgcolor='rgba(0, 0, 0, 100)',
        yaxis=dict(
            type=yaxis_type,
            tickfont=dict(color='white'),
        ),
        xaxis=dict(
            tickfont=dict(color='white'),
        ),
        legend_title_text='Type of meteorites',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            font=dict(
                color="white"
            ),
        )
    )

    fig = dict(data=trace, layout=layout)
    return fig


@app.callback(
    dash.dependencies.Output("year-chart", "figure"),
    [dash.dependencies.Input("year-range-slider", "value"),
     dash.dependencies.Input('seen-found-check', 'value')],
)
def display_year_chart(years, fall):
    df_years = get_by_years(years, fall)
    trace = []
    for i in fall:
        trace.append(
            dict(
                type='scatter',
                mode='lines',
                x=df_years[df_years['fall'] == i]['year'],
                y=df_years[df_years['fall'] == i]["count"],
                name=i,
            )
        )

    layout = dict(
        height=180,
        margin=dict(r=5, l=35, t=0, b=20),
        paper_bgcolor='rgba(0, 0, 0, 100)',
        plot_bgcolor='rgba(0, 0, 0, 100)',
        automargin=True,
        yaxis=dict(
            tickfont=dict(color='white')
        ),
        xaxis=dict(
            tickfont=dict(color='white'),
        ),
        legend_title_text='Type of meteorites',
        legend=dict(
            font=dict(
                color="white"
            ),
        ),
        title=dict(
            text="Landing/year",
            y=0.9,
            x=0.5,
            xanchor='center',
            yanchor='center',
            font=dict(
                color="white"
            ),
        )
    )

    fig = dict(data=trace, layout=layout)
    return fig


@app.callback(
    dash.dependencies.Output("year-range-slider", "value"),
    [dash.dependencies.Input("year-chart", "relayoutData")],
)
def update_slider(layout):
    if layout is not None:
        if 'xaxis.range[0]' in layout:
            return [int(layout['xaxis.range[0]']), int(layout['xaxis.range[1]']) + 1]
    return [df['year'].min(), df['year'].max()]


if __name__ == '__main__':
    app.run_server(debug=True)
