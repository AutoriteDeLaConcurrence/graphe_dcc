import dash
from dash import html
from dash import dcc, Input, Output, State, callback, clientside_callback
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd

from utils import TOPICS_TXT, DEF_STYLESHEET, COL_STYLESHEET
from utils import load_compressed_dat_file

dash.register_page(__name__, path_template="/graphe/<decision_id>")


def layout(decision_id=None):
    elements = load_compressed_dat_file("./data/cytoscape_graph.dat")
    all_nodes_list = [x.get("data").get("id") for x in elements if x.get("data").get("id")]
    if decision_id not in all_nodes_list:
        layout = html.Div(
            dbc.Alert("La décision recherchée n'est pas dans le graphe!", color="warning")
        )
    else:
        elements = [x if not x.get("data").get("id") == decision_id else dict(x, selected=True) for x in elements]
        selected_node = [x for x in elements if x.get("data").get("id") == decision_id][0].get("data")
        selected_pos = [x for x in elements if x.get("data").get("id") == decision_id][0].get("position")
        selected_edges = [x for x in elements if x.get("data").get("source") == decision_id or x.get("data").get("target") == decision_id]
        nodes = [edge.get("data").get("source") for edge in selected_edges] + [edge.get("data").get("target") for edge in selected_edges]
        selected_nodes = [x for x in elements if x.get("data").get("id") in nodes]

        DEF_STYLESHEET_NEW = [
            {
                "selector": f'[id ^= "{selected_node.get("id")}"]',
                "style": {
                    'background-color': '#920000',
                    "border-color": "#920000",
                    "border-width": 2,
                    "border-opacity": 1,
                    "opacity": 1,
                    # "label": "data(label)",
                    "color": "#920000",
                    "text-opacity": 1,
                    "font-size": 30,
                }
            },
            {
                'selector': 'node',
                'style': {
                    # 'content': 'data(label)',
                    'text-halign': 'center',
                    'text-valign': 'center',
                    "font-size": '50',
                    "color": "white"
                }
            }
        ]

        layout = html.Div([
                html.H4(f"Graphe associé à la décision {decision_id}."),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        cyto.Cytoscape(
                                            id="cytoscape-layout-specifique",
                                            layout={"name": "preset"},
                                            style={"width": "100%", "height": "700px"},
                                            elements=selected_nodes+selected_edges,
                                            stylesheet=DEF_STYLESHEET+COL_STYLESHEET + DEF_STYLESHEET_NEW,
                                            minZoom=0.1,
                                            maxZoom=1,
                                            selectedNodeData=[selected_node],
                                            mouseoverNodeData={"delay": 200, "duration": 1000, "hide": None},
                                            pan=selected_pos
                                        )
                                    ]
                                ),
                            ],
                            width=8
                        ),
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        dbc.Badge("Noeud selectionné :", color="primary", className="mr-1"),
                                        html.Div(id="elements-data-specific"),
                                    ]
                                ),
                                dbc.Row(
                                    [
                                        dbc.Badge("Passez la souris sur un noeud:", color="primary", className="mr-1"),
                                        html.Div(id="hover-info-specific"),
                                    ],
                                ),
                            ]
                        )
                    ]
                ),
            ]
        )
    return layout


# Callback 1 : Affichage du noeud quand on le hover
@callback(
    Output("hover-info-specific", "children"),
    [Input("cytoscape-layout-specifique", "mouseoverNodeData")]
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
    Output("elements-data-specific", "children"),
    [Input("cytoscape-layout-specifique", "selectedNodeData")],
)
def display_nodedata(node_attr):
    if node_attr:
        data = node_attr[-1]
        # print(data)
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
                # html.P(
                #     [
                #         dbc.Button(f"Télécharger les citations de {data['id']}", id="btn_xlsx", color="primary", size="sm"),
                #         dcc.Download(id="download-dataframe-xlsx")
                #     ],
                #     style={"text-align": "center", "margin-top": "10px"}
                # ),
            ]
        else:
            body = html.H5("Not available")

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
