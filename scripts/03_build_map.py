import pandas as pd
import folium
from folium.plugins import MarkerCluster
import os

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "centres_musicals_cv_20260504.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "maps")
os.makedirs(OUTPUT_DIR, exist_ok=True)

COLORS = {
    "ESCUELA PRIVADA DE MUSICA":            "blue",
    "ESCUELA PRIVADA DE MUSICA Y DANZA":    "blue",
    "ESCUELA PRIVADA DE MUSICA Y ARTES ESCENICAS": "blue",
    "ESCUELA PUBLICA DE MUSICA":            "green",
    "ESCUELA PUBLICA DE MUSICA Y DANZA":    "green",
    "CONSERVATORIO ELEMENTAL DE MUSICA":    "orange",
    "CONSERVATORIO PROFESIONAL DE MUSICA":  "orange",
    "CONSERVATORIO SUPERIOR DE MUSICA":     "red",
    "CONSERVATORIO PROFESIONAL DE MUSICA Y ELEMENTAL DE DANZA": "orange",
    "CENTRO AUTORIZADO ELEMENTAL DE MUSICA":  "lightblue",
    "CENTRO AUTORIZADO DE ENSENANZAS ARTISTICAS PROFESIONALES DE MUSICA": "purple",
    "CENTRO AUTORIZADO SUPERIOR DE MUSICA": "darkred",
    "CENTRO INTEGRADO DE MUSICA Y ENSENANZAS DE REGIMEN GENERAL": "darkgreen",
}

import unicodedata
def norm(s):
    if not isinstance(s, str): return ""
    s = s.upper()
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

df = pd.read_csv(INPUT_FILE, low_memory=False)
df["latitud"]  = pd.to_numeric(df["latitud"],  errors="coerce")
df["longitud"] = pd.to_numeric(df["longitud"], errors="coerce")
df = df.dropna(subset=["latitud", "longitud"])
df["_tipus_norm"] = df["denominacion_generica_es"].apply(norm)
print(f"Centres amb coordenades: {len(df)}")

m = folium.Map(location=[39.4, -0.7], zoom_start=8, tiles="CartoDB positron")

grups = {
    "Escoles privades": folium.FeatureGroup(name="Escoles de Musica privades", show=True),
    "Escoles publiques": folium.FeatureGroup(name="Escoles de Musica publiques", show=True),
    "Conservatoris":    folium.FeatureGroup(name="Conservatoris", show=True),
    "Centres Autoritzats": folium.FeatureGroup(name="Centres Autoritzats", show=True),
}

def get_grup(tipus_norm):
    if "CONSERVATORIO" in tipus_norm: return "Conservatoris"
    if "AUTORIZADO" in tipus_norm or "INTEGRADO" in tipus_norm: return "Centres Autoritzats"
    if "PUBLICA" in tipus_norm: return "Escoles publiques"
    return "Escoles privades"

for _, row in df.iterrows():
    tipus      = str(row.get("denominacion_generica_es", ""))
    tipus_norm = norm(tipus)
    nom        = str(row.get("denominacion", ""))
    munic      = str(row.get("localidad", ""))
    comarca    = str(row.get("comarca", ""))
    prov       = str(row.get("provincia", ""))
    tel        = str(row.get("telefono", ""))
    regim      = str(row.get("regimen", ""))
    color      = COLORS.get(tipus_norm, "gray")
    popup_html = f"""<div style='font-family:Arial;min-width:200px'>
      <b>{nom}</b><br><span style='color:#666;font-size:11px'>{tipus}</span><br><br>
      <b>Municipi:</b> {munic}<br><b>Comarca:</b> {comarca}<br>
      <b>Provincia:</b> {prov}<br><b>Regim:</b> {regim}<br><b>Tel:</b> {tel}
    </div>"""
    marker = folium.Marker(
        location=[row["latitud"], row["longitud"]],
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=nom,
        icon=folium.Icon(color=color, icon="music", prefix="fa"),
    )
    marker.add_to(grups[get_grup(tipus_norm)])

for g in grups.values():
    g.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

title_html = """<div style='position:fixed;top:10px;left:50%;transform:translateX(-50%);
z-index:1000;background:white;padding:10px 20px;border-radius:8px;
box-shadow:0 2px 8px rgba(0,0,0,0.3);font-family:Arial;font-size:15px;
font-weight:bold;color:#1A3A5C'>
Cartografia de les Ensenyances Musicals · Comunitat Valenciana · 2026</div>"""
m.get_root().html.add_child(folium.Element(title_html))

output_path = os.path.join(OUTPUT_DIR, "index.html")
m.save(output_path)
print(f"Mapa guardat: {output_path}")
print("Obre maps/index.html al navegador per veure el mapa.")
