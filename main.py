import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

mapbox_access_token = "pk.eyJ1IjoibG9pY2JhY2hlbG90IiwiYSI6ImNraGc0bmdnOTBveWoyeW80ZDU1Z2EzY2kifQ.mOX2igWQn0uH5HJusetcqA"
mapbox_style = "dark"  # "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN])

server = app.server

df = pd.read_csv('./meteorites.csv').sort_values(by=['year'])

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
            children=[
                html.H1(children="Meteorites landing"),
                html.P(
                    id="description",
                    children="Here I will talk about the datasets I used and stuff like that. "
                             "Deaths are classified using the International Classification of Diseases, \
                        Tenth Revision (ICD–10). Drug-poisoning deaths are defined as having ICD–10 underlying \
                        cause-of-death codes X40–X44 (unintentional), X60–X64 (suicide), X85 (homicide), or Y10–Y14 \
                        (undetermined intent).",
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
                                                                        "Drag the slider to select the years to display",
                                                                        html_for='year-range-slider'),
                                                                ]),
                                                        ],
                                                            align='center',
                                                        ),
                                                        dbc.Col(
                                                            dbc.FormGroup(
                                                                children=[
                                                                    dbc.Label("Select the type of meteorites to display"),
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
                                                    ]),
                                            ]),
                                        dbc.CardBody(
                                            dcc.Graph(
                                                id='graph-map',
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
                                            ),
                                        ),
                                    ]),

                            ],
                        ),
                    ]),
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


@app.callback(
    dash.dependencies.Output('graph-map', 'figure'),
    [dash.dependencies.Input('year-range-slider', 'value'),
     dash.dependencies.Input('seen-found-check', 'value')],
    [dash.dependencies.State('graph-map', "relayoutData")]
)
def update_graph(years, fall, graph_layout):
    df_filter = get_filtered_df(years, fall)

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
                color='rgb(206, 118, 100)',
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
            style='dark',
        ),
    )
    fig = dict(data=trace, layout=layout)
    return fig


@app.callback(
    dash.dependencies.Output('output-container-test', 'children'),
    [dash.dependencies.Input('graph-map', 'layoutparam')]
)
def update_output(graph_layout):
    lat = lon = zoom = 0
    if graph_layout is not None:
        if "mapbox.center" in graph_layout.keys():
            lon = float(graph_layout["mapbox.center"]["lon"])
            lat = float(graph_layout["mapbox.center"]["lat"])
            zoom = float(graph_layout["mapbox.zoom"])
    return 'the actual parameters of the map are: lat ' + str(lat) + ' lon ' + str(lon) + ' zoom ' + str(zoom)


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
        margin=dict(r=5, l=30, t=0),
        paper_bgcolor='rgba(0, 0, 0, 100)',
        plot_bgcolor='rgba(0, 0, 0, 100)',
        yaxis=dict(
            type=yaxis_type,
            tickfont=dict(color='white')
        ),
        xaxis=dict(
            tickfont=dict(color='white')
        )
    )

    fig = dict(data=trace, layout=layout)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
