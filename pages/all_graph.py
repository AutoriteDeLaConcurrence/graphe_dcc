import dash
from dash import html
from dash import dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd

from utils import TOPICS_TXT, DEF_STYLESHEET, COL_STYLESHEET
from utils import load_compressed_dat_file

dash.register_page(__name__, path='/all')


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
                                    style={"width": "100%", "height": "1200px"},
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
                    width=12
                ),
            ],
        ),
    ]
)
