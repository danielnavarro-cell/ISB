"""Semantic colors shared by plots, PDF and components; no visual redesign.

Native surfaces/accent come from .streamlit/config.toml. Change those globals
and these semantic tokens when the red/pearl clinical palette is approved.
"""
from pathlib import Path
import tomllib

_config=next((p/'.streamlit/config.toml' for p in Path(__file__).resolve().parents if (p/'.streamlit/config.toml').exists()),None)
if _config is None:
    raise ValueError('Falta .streamlit/config.toml en la carpeta del proyecto o del repositorio.')
_theme = tomllib.loads(_config.read_text(encoding='utf-8'))['theme']
PALETTE = dict(accent=_theme['primaryColor'],panel=_theme['secondaryBackgroundColor'],
               background=_theme['backgroundColor'],text=_theme['textColor'],border=_theme['borderColor'],
               raw='#9CB5C2',marker='#EAB66B')
PDF_PALETTE = dict(table='#edf6f5',raw='#677e8a',filtered='#087f77',marker='#bc7a12',axis='#808080')
CHART_TEMPLATE = 'plotly_dark' if _theme.get('base','dark')=='dark' else 'plotly_white'


def download_css():
    return f"""
button {{ width:100%; padding:.7rem 1rem; border:1px solid {PALETTE['border']};
 background:{PALETTE['panel']}; color:{PALETTE['text']}; border-radius:.5rem; cursor:pointer;
 font:inherit; min-height:44px; }}
button:hover {{ border-color:{PALETTE['accent']}; color:{PALETTE['accent']}; }}
button:focus-visible {{ outline:2px solid {PALETTE['accent']}; outline-offset:2px; }}
"""
