import blosc
from dash import html
import pickle
import plotly.express as px

TOPICS_TXT = [
    "Presse / Médias", "Energie / Environnement", "Transports", "Santé",
    "Grande consommation", "Distribution", "Industrie", "Banque / Assurance",
    "Outre-Mer", "Agriculture / Agro-alimentaire", "Télécoms", "Services",
    "Tourisme / hôtellerie / restauration", "BTP", "Numérique",
    "Professions réglementées", "Arts et culture"
]

COLOL_PALETTE = px.colors.qualitative.Dark24
COLOL_PALETTE = [color for color in COLOL_PALETTE if color != '#778AAE']
SECTOR_COLOR_MAPPING = {sector: COLOL_PALETTE[i] for i, sector in enumerate(TOPICS_TXT)}

SECTOR_HTML = [html.Div([html.Span([f"{i+1}: {topic}\n"], style={"color": SECTOR_COLOR_MAPPING.get(topic)}), html.Br()]) for i, topic in enumerate(TOPICS_TXT)]
moitie_secteur = len(SECTOR_HTML) // 2 + (len(SECTOR_HTML) % 2 > 0)

DEF_STYLESHEET = [
    {"selector": f".{sector}", "style": {"background-color": SECTOR_COLOR_MAPPING[sector], "line-color": SECTOR_COLOR_MAPPING[sector]}}
    for sector in TOPICS_TXT
]
DEF_STYLESHEET += [
    {"selector": "node", "style": {"width": "data(node_size)", "height": "data(node_size)", "border-width": 10, "border-color": "#000000"}},
    {"selector": "edge", "style": {"width": 10, "curve-style": "bezier"}}
]

COL_STYLESHEET = [
    {'selector': f'[secteur = "{secteur}"]', 'style': {'background-color': f'{couleur}'}}
    for secteur, couleur in SECTOR_COLOR_MAPPING.items()
]


def load_compressed_dat_file(path):
    with open(path, "rb") as f:
        compressed_pickle = f.read()
        depressed_pickle = blosc.decompress(compressed_pickle)
        elements = pickle.loads(depressed_pickle)
    return elements
