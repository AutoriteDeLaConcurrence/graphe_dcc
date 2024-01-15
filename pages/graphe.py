import dash
from dash import html
from dash import dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd

from utils import TOPICS_TXT, DEF_STYLESHEET, COL_STYLESHEET
from utils import load_compressed_dat_file

dash.register_page(__name__, path='/graphe')


elements = load_compressed_dat_file("./data/cytoscape_graph.dat")
df_export = pd.read_csv('./data/edges.csv', index_col=False, sep=',', engine='python')
unique_nodes = pd.concat([df_export['DCC ORIGINE'], df_export['DCC DESTINATION']]).unique()

layout = html.Div([
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                cyto.Cytoscape(
                                    id="cytoscape-layout",
                                    layout={"name": "preset"},
                                    style={"width": "100%", "height": "600px"},
                                    elements=elements,
                                    stylesheet=DEF_STYLESHEET+COL_STYLESHEET,
                                    minZoom=0.04,
                                    maxZoom=1.5,
                                    selectedNodeData=[],
                                    mouseoverNodeData={"delay": 200, "duration": 1000, "hide": None},
                                )
                            ]
                        ),
                    ],
                    width=8
                ),
                dbc.Col(
                    [
                        dbc.Container(
                            [
                                dbc.Badge("Afficher :", color="primary", className="mr-1"),
                                html.Div(
                                    [
                                        dbc.RadioItems(
                                            id="radioitem-nb-citations",
                                            options=[
                                                {'label': 'Toutes les décisions citées ou citant une autre décision', 'value': 0},
                                                {'label': 'Toutes les décisions citées au moins 1 fois', 'value': 1},
                                                {'label': 'Toutes les décisions citées au moins 5 fois', 'value': 5},
                                                {'label': 'Toutes les décisions citées au moins 10 fois', 'value': 10},
                                                {'label': 'Toutes les décisions citées au moins 20 fois', 'value': 20},
                                            ],
                                            value=10
                                        ),
                                    ]
                                ),
                                html.Div(style={'height': '20px'}),
                                dbc.Badge("Secteurs:", color="primary", className="mr-1"),
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            id="sectors_dropdown",
                                            options=[
                                                {'label': secteur, 'value': secteur}
                                                for secteur in TOPICS_TXT
                                            ],
                                            persistence=False,
                                        ),
                                    ]
                                ),
                                html.Div(style={'height': '20px'}),
                                dbc.Badge("OU", color="primary", className="mr-1"),
                                html.Div(style={'height': '20px'}),
                                dbc.Badge("Sélectionnez directement une décision:", color="primary", className="mr-1"),
                                html.Div([dcc.Dropdown(id="dropdown_node", options=[{'label': node, 'value': node} for node in unique_nodes])]),
                                html.Div(style={'height': '20px'}),
                                html.Div(
                                    dbc.Button("Réinitialiser les filtres", id="reset-button", color="primary", size="sm"),
                                    style={"text-align": "center"}
                                )
                            ]
                        )
                    ],
                    width=4
                ),
            ],
            style={"height": "600px"}
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Badge("Passez la souris sur un noeud:", color="primary", className="mr-1"),
                        html.Div(id="hover-info"),
                    ],
                    width=6
                ),
                dbc.Col(
                    [
                        dbc.Badge("Pour plus de détails, cliquez sur le noeud", color="primary", className="mr-1"),
                        html.Div(id="elements-data"),
                    ]
                )
            ]
        )
    ]
)


# Callback 1 : Affichage du noeud quand on le hover
@callback(
    Output("hover-info", "children"),
    [Input("cytoscape-layout", "mouseoverNodeData")]
)
def display_hovered_node_info(node_data):
    if node_data.get("id"):
        id = node_data.get('id')
        secteur = node_data.get('liste_secteurs')
        sous_titre = node_data.get('sous_titre')

        return dbc.Card(
                    [
                        dbc.CardHeader(f"{id} {sous_titre}", style={"background-color": "#f8f9fa", "font-weight": "bold"}),
                        dbc.CardBody(
                            [
                                html.P(f"Secteur(s): {secteur}"),
                            ]
                        ),
                    ],
                    style={"border": "2px solid #ccc", "border-radius": "5px", "margin-top": "10px"},
                )
    else:
        return dbc.Card(style={"display": None})


# Callback 2 : Main interaction when clicking on a node or edge
@callback(
    Output("elements-data", "children"),
    [Input("cytoscape-layout", "selectedNodeData"), Input('cytoscape-layout', 'selectedEdgeData')],
)
def display_nodedata(node_attr, edge_attr):
    if node_attr:
        data = node_attr[-1]
        if len(data) > 3:
            title = html.H6(html.A(
                f'{data["id"]} {data["sous_titre"].title()}',
                href=f'https://www.autoritedelaconcurrence.fr/fr/liste-de-controle-des-concentrations?search_api_fulltext={data["id"]}&sort_by=search_api_relevance&field_date_dcc%5Bmin%5D=&field_date_dcc%5Bmax%5D=',
                target="_blank"
            ))
            subtitle = html.H6(f"Citée {str(data['indegrees'])} fois")
            body = [
                html.Br(),
                html.Strong("Secteur: "),
                data["liste_secteurs"],
                html.Br(),
                html.Strong("Date: "),
                data["date_decision"],
                html.Br(),
                html.Strong("Type d'opération: "),
                data["type_operation"],
                html.Br(),
                html.Strong("Décision de phase: "),
                data["Décision de phase"],
                html.Br(),
                html.Strong("Entreprise(s) concernée(s): "),
                data["Entreprise concernée"],
                html.Br(),
                html.Strong("Partie notifiante: "),
                data["Partie notifiante"],
                html.Br(),
                html.P(
                    [
                        dbc.Button(f"Télécharger les citations de {data['id']}", id="btn_xlsx", color="primary", size="sm"),
                        dcc.Download(id="download-dataframe-xlsx")
                    ],
                    style={"text-align": "center", "margin-top": "10px"}
                ),
            ]
        else:
            body = html.H5("Not available")

    elif edge_attr:
        data = edge_attr[-1]
        title = html.H4(f"Citation de {data['source']} vers {data.get('target')}")
        subtitle = html.H6(f"Citée {data['cited_occurences']} fois")
        body = []

    else:
        return dbc.Card(style={"display": None})

    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(title, className="card-title"),
                html.Div(subtitle, className="card-subtitle"),
                html.Div(body, className="card-text"),

            ]
        )
    )


# Callback 4 : update the stylesheet
@callback(
    Output('cytoscape-layout', 'stylesheet'),
    [
        Input('cytoscape-layout', 'tapNode'),
        Input(component_id='sectors_dropdown', component_property='value'),
        Input(component_id='dropdown_node', component_property='value'),
        Input(component_id='radioitem-nb-citations', component_property='value')
    ]
)
def generate_stylesheet(node, sector, input, citations):
    stylesheet = [
        {
            "selector": "node",
            "style": {"width": "data(node_size)", "height": "data(node_size)", "border-width": 10, "border-color": "#000000"},
        },
        {"selector": "edge", "style": {"width": 10, "curve-style": "bezier"}},
    ]

    if sector and citations:
        stylesheet.append(
            {
                "selector": f'node[liste_secteurs *= "{sector}"][indegrees >= {citations}]',
                "style": {'background-color': '#920000'}
            }
        )
        stylesheet.append(
            {
                "selector": f'node[liste_secteurs != "{sector}"][indegrees < {citations}]',
                "style": {'display': 'none'}
            }
        )
        stylesheet.append(
            {
                "selector": f'node[indegrees < {citations}]',
                "style": {'display': 'none'}
            }
        )
        return stylesheet

    if node:
        stylesheet.append(
            {
                "selector": 'node[id = "{}"]'.format(node['data']['id']),
                "style": {
                    'background-color': '#920000',
                    "border-color": "#920000",
                    "border-width": 5,
                    "border-opacity": 1,
                    "opacity": 1,
                    "label": "data(label)",
                    "color": "#920000",
                    "text-opacity": 1,
                    "font-size": 12,
                }
            }
        )

        for edge in node['edgesData']:
            if edge['source'] == node['data']['id']:
                stylesheet.append({
                    "selector": 'node[id = "{}"]'.format(edge['target']),
                    "style": {
                        'background-color': '#ffdf4d',
                        'opacity': 0.9,
                        "label": "data(label)",
                    }
                })
                stylesheet.append({
                    "selector": 'edge[id= "{}"]'.format(edge['id']),
                    "style": {
                        "mid-target-arrow-color": '#ffdf4d',
                        "mid-target-arrow-shape": "vee",
                        "line-color": '#ffdf4d',
                        'opacity': 0.9,
                    }
                })
            if edge['target'] == node['data']['id']:
                stylesheet.append({
                    "selector": 'node[id = "{}"]'.format(edge['source']),
                    "style": {
                        'background-color': '#b66dff ',
                        'opacity': 0.9,
                    }
                })
                stylesheet.append({
                    "selector": 'edge[id= "{}"]'.format(edge['id']),
                    "style": {
                        "mid-target-arrow-color": '#b66dff ',
                        "mid-target-arrow-shape": "vee",
                        "line-color": '#b66dff ',
                        'opacity': 1,
                    }
                })
        return stylesheet

    if sector:
        stylesheet.append(
            {
                'selector': f'[liste_secteurs *= "{sector}"]',
                'style': {
                    'background-color': '#920000',
                }
            },
        )
        return stylesheet

    if input:
        stylesheet.append(
            {
                "selector": f'[id ^= "{input}"]',
                "style": {
                    'background-color': '#920000',
                    "border-color": "#920000",
                    "border-width": 2,
                    "border-opacity": 1,
                    "opacity": 1,
                    "width": "200px",
                    "height": "200px",
                    "label": "data(label)",
                    "color": "#920000",
                    "text-opacity": 1,
                    "font-size": 12,
                }
            },
        )
        return stylesheet

    if citations:
        stylesheet = stylesheet + COL_STYLESHEET
        stylesheet.append(
            {
                "selector": f'[indegrees < {citations}]',
                "style": {"display": "none"}
            },
        )
        return stylesheet
    else:
        return DEF_STYLESHEET + COL_STYLESHEET


# Callback 5 : Download the data
@callback(
    Output("download-dataframe-xlsx", "data"),
    Input("btn_xlsx", "n_clicks"),
    State("cytoscape-layout", "selectedNodeData"),
    prevent_initial_call=True
)
def func(n_clicks, elements):
    for element in elements:
        data = df_export[(df_export['DCC ORIGINE'] == element['id']) | (df_export['DCC DESTINATION'] == element['id'])]
        data = data.sort_values("NOMBRE", ascending=False).reset_index(drop=True)
        return dcc.send_data_frame(data.to_excel, f"export_details_{element['id']}.xlsx", sheet_name="data")


# Callback6: Reset the filters
@callback(
    [
        Output("radioitem-nb-citations", "value"),
        Output("sectors_dropdown", "value"),
        Output("dropdown_node", "value"),
    ],
    [Input("reset-button", "n_clicks")]
)
def reset_filters(n_clicks):
    if n_clicks:
        return 10, None, None
    else:
        raise dash.exceptions.PreventUpdate
