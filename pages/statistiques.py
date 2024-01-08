import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import networkx as nx
from collections import defaultdict
import json
from components import Box
import plotly.express as px
import dash_mantine_components as dmc
from statistics import mean

dash.register_page(__name__, path='/statistiques')

# Load edge and nodes data
edges = pd.read_csv("./data/edges.csv", encoding='utf-8', sep=",")
with open("./data/nodes.json", "r", encoding="utf-8") as json_file:
    nodes = json.load(json_file)

nodes_liste_secteurs = {key: {"liste_secteurs":value.get("liste_secteurs")} for key, value in nodes.items()}

# Create graphe from edges list
d = defaultdict(dict)
for a, b, c in edges.itertuples(index=False):
    d[a][b] = {"weight": c}
d = dict(d)


# On crée 2 versions : dirigé et non dirigé
directed_graph = nx.DiGraph(d)
not_directed_graph = nx.Graph(d)

in_degrees = directed_graph.in_degree()
df_indegree = pd.DataFrame(in_degrees, columns= ["id_decision", "Nombre de citations"])
histogram_indegree = px.histogram(df_indegree, "Nombre de citations", title="Nombre de décisions par nombre de citations")


largest_cc = max(nx.connected_components(not_directed_graph), key=len)
not_directed_graph = nx.subgraph(not_directed_graph, largest_cc)

nx.set_node_attributes(G=not_directed_graph, values=nodes_liste_secteurs)


# #### Stats
nombre_nodes = len(not_directed_graph.nodes)
nombre_edges = len(not_directed_graph.edges)
average_edges = mean(dict(in_degrees).values())
nombre_jamais_citees = len([key for key, value in dict(in_degrees).items() if value==0])
nombre_citees_moins_10 = len([key for key, value in dict(in_degrees).items() if value<=10])
nombre_citees_plus_50 = len([key for key, value in dict(in_degrees).items() if value>=50])
# # # Top 10 des citations les plus citées
top_10_nodes_in = sorted(in_degrees, key=lambda x: x[1], reverse=True)[:10]
# # Centralité betweeness
top10_betweeness = sorted(nx.betweenness_centrality(not_directed_graph).items(), key=lambda x: x[1], reverse=True)[:10]
# # PageRank
top10_pagerank = sorted(nx.pagerank(directed_graph).items(), key=lambda x: x[1], reverse=True)[:10]


collapse_graph = html.Div(
    [
        dbc.Button(
            "Afficher l'histogramme du nombre de citations",
            id="collapse-button",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            dbc.Row(
                dbc.Col(
                    Box(
                        children=dcc.Graph(figure = histogram_indegree)),
                    width=6
                ),
            ),
            id="collapse",
            is_open=False,
        ),
    ]
)


@callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open



layout = html.Div(
    [
        html.H1('Statistiques du graphe des DCC', style={"textAlign":"center"}, ),
        html.H2("Nombre de décisions et nombre de citations"),
        html.P("""Le graphe des décisions de controle des concentraitions est composé de {} noeuds représentant chacun une decision, et de {} liens représentant les citations entre les décisions. 
               En moyenne, les décisions sont citées {:.2f} fois mais cela cache de fortes disparités, puisque {:.2%} des décisions sont citées moins de 10 fois, dont {:.2%} qui n'ont aucune citations. 
               """.format(nombre_nodes, nombre_edges, average_edges, nombre_citees_moins_10/nombre_nodes, nombre_jamais_citees/nombre_nodes)),
        dbc.Row(
            [
                dbc.Col(
                    Box(
                        title="Nombre de décisions",
                        children=html.H5(nombre_nodes),
                        style={"background-color":"lightblue", "textAlign":"center"},
                        title_style={"textAlign":"center"}, 
                    ),
                    width=4
                ),
                dbc.Col(
                    Box(
                        children=html.H5(nombre_edges),
                        title="Nombre de citations",
                        style={"background-color":"lightgreen", 'textAlign': 'center'},
                        ),
                    width=4
                ),
                dbc.Col(
                    Box(
                        title="Nombre moyen de citation par décision",
                        children=html.H5("{:.2f}".format(average_edges)),
                        style={"background-color":"lightpink", 'textAlign': 'center'}
                    ),
                    width=4
                ),
            ]
        ),

       dbc.Row(
            [
                dbc.Col(
                    Box(
                        title="Nombre de décisions jamais citées",
                        children=html.H5("{} ({:.2%})".format(nombre_jamais_citees, nombre_jamais_citees/nombre_nodes)),
                        style={"background-color":"lightgreen",'textAlign': 'center'},
                    ),
                    width=4
                ),
                dbc.Col(
                    Box(
                        title="Nombre de décisions citées moins de 10 fois",
                        children=html.H5("{} ({:.2%})".format(nombre_citees_moins_10, nombre_citees_moins_10/nombre_nodes)),
                        style={"background-color":"lightpink", 'textAlign': 'center'},
                    ),
                    width=4
                ),
                dbc.Col(
                    Box(
                        title="Nombre de décisions citées plus de 50 fois",
                        children=html.H5("{} ({:.2%})".format(nombre_citees_plus_50, nombre_citees_plus_50/nombre_nodes)),
                        style={"background-color":"lightblue", 'textAlign': 'center'},
                    ),
                    width=4
                ),
            ]
        ),
        collapse_graph,
        html.H2('Décisions les plus importantes'),
        html.P("""Cette analyse nous permet d'identifier les noeuds centraux du graphe des décisions de concentrations.
                La décision 09-DCC-16 est la plus citée et par des noeuds importants, mais elle se situe en périphérie du graphe, ce qui réduit son score de centralité d'intermédiarité.
                A l'inverse, la décision 13-DCC-90 est citée par des décisions moins importantes (score Pagerank plus faible), mais apparait comme plus centrale dans le graphe.
                
                """),
        dbc.Row(
            [
                dbc.Col(
                    Box(
                        children = dmc.List(
                            [
                                dmc.ListItem(f"{node} ({score})")
                                for node, score in list(top_10_nodes_in) 
                            ],
                            type="ol"
                        ),
                        title="Centralité de degré entrant",
                        subtitle="Nombre de citations",
                        style={"background-color":"lightpink"},
                        title_style={"textAlign":"center"}, 
                    ),
                width=4
                ),
                dbc.Col(
                    Box(
                        children = dmc.List(
                            [
                                dmc.ListItem(f"{node} ({score})")
                                for node, score in list(top10_pagerank) 
                            ],
                            type="ol"
                        ),
                        title="Centralité PageRank",
                        subtitle="Liens et importance relative des liens",
                        style={"background-color":"lightblue"},
                        title_style={"textAlign":"center"}, 
                    ),
                width=4
                ),
                dbc.Col(
                    Box(
                        children = dmc.List(
                            [
                                dmc.ListItem(f"{node} ({score})")
                                for node, score in list(top10_betweeness) 
                            ],
                            type="ol"
                        ),
                        title="Centralité d'intermédiarité",
                        subtitle="Nombre de chemins les plus courts passant par ce noeud",
                        style={"background-color":"lightgreen"},
                        title_style={"textAlign":"center"}, 
                    ),
                width=4
                ),
            ]
        ),
    ]
)
