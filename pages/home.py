
import dash
from dash import html
from dash import dcc, Input, Output, State, callback, get_asset_url
import dash_bootstrap_components as dbc

from utils import SECTOR_HTML, moitie_secteur

dash.register_page(__name__, path='/')

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Hr(),
                        html.H3("Données"),
                        html.Hr(),
                        html.P(
                            """
                            Les données sont les 3275 décisions de contrôle des concentrations publiées par l'Autorité de la concurrence entre 2009 et le 31 décembre 2023.
                            Les noeuds correspondent aux décisions. Les arêtes sont les citations entre les décisions.
                            Exemple: la décision 10-DCC-30 cite la décision 09-DCC-08, les deux noeuds sont donc reliés.
                            La taille des noeuds correspond au nombre de fois où les décisions sont citées par d'autres décisions: plus le noeud est grand, plus la décision est référencée.
                            """
                        )
                    ],
                    width=6
                ),
                dbc.Col(
                    [
                        html.Hr(),
                        html.H3("Secteurs"),
                        html.Hr(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div(
                                        SECTOR_HTML[start:start+moitie_secteur],
                                        style={
                                            "fontSize": 14,
                                            "overflow": "auto",
                                        },
                                    ),
                                )
                                for start in [0, moitie_secteur]
                            ]
                        ),
                    ],
                    width=6
                ),
            ]
        ),
        html.Hr(),
        html.H3("Version française"),
        html.Hr(),
        html.Img(src=get_asset_url("graphe_label_FR.png")),
        html.Hr(),
        html.H3("Version anglaise"),
        html.Hr(),
        html.Img(src=get_asset_url("graphe_label_EN.png"))
    ],
    fluid=True,
)
