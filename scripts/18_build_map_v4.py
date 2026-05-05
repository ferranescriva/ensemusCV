import pandas as pd
import folium
import json
import os, math, unicodedata

BASE_DIR = os.path.expanduser("~/ensemusCV")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
MAP_DIR  = os.path.join(BASE_DIR, "maps")
os.makedirs(MAP_DIR, exist_ok=True)

df = pd.read_csv(os.path.join(PROC_DIR, "centres_musicals_enriquits.csv"))
df['latitud']  = pd.to_numeric(df['latitud'],  errors='coerce')
df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
df = df.dropna(subset=['latitud','longitud'])

with open(os.path.join(PROC_DIR, "cobertura_dissolve.geojson"), encoding='utf-8') as f:
    cobertura = json.load(f)

def norm(s):
    if not isinstance(s, str): return ""
    return "".join(c for c in unicodedata.normalize("NFD", s.upper())
                   if unicodedata.category(c) != "Mn")

def classify(row):
    t = norm(str(row.get('denominacion_generica_es','')))
    tit = norm(str(row.get('titular','')))
    gva = 'GENERALITAT' in tit
    if 'CONSERVATORIO SUPERIOR' in t or 'CONSERVATORI SUPERIOR' in t:
        return ('Conservatori Superior GVA', '#8B6914', 'Conservatoris GVA')
    if ('CONSERVATORIO PROFESIONAL' in t or 'CONSERVATORI PROFESSIONAL' in t) and gva:
        return ('Conservatori Professional GVA', '#E8A020', 'Conservatoris GVA')
    if ('CONSERVATORIO PROFESIONAL' in t or 'CONSERVATORI PROFESSIONAL' in t) and not gva:
        return ('Conservatori Professional Municipal', '#F5C842', 'Conservatoris Municipals')
    if ('CONSERVATORIO ELEMENTAL' in t or 'CONSERVATORI ELEMENTAL' in t):
        return ('Conservatori Elemental Municipal', '#FAE08A', 'Conservatoris Municipals')
    if 'AUTORIZADO' in t or 'AUTORITZAT' in t:
        if 'ELEMENTAL' in t:
            return ('Centre Autoritzat Elemental', '#C45C5C', 'Centres Autoritzats')
        return ('Centre Autoritzat Professional', '#8B1A1A', 'Centres Autoritzats')
    if 'PUBLICA' in t:
        return ('Escola Publica de Musica', '#2E8B57', 'Escoles Publiques')
    if 'PRIVADA' in t:
        return ('Escola Privada de Musica', '#2E6DA4', 'Escoles Privades')
    return ('Altres', '#888888', 'Altres')

def fmt(v):
    if v is None or (isinstance(v, float) and math.isnan(v)): return "sense dades"
    return "{:,.0f} EUR".format(v).replace(",",".")

def radius(v, label):
    big = 'Conservatori' in label or 'Autoritzat' in label
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return 9 if big else 5
    base = 9 if big else 5
    div  = 10000 if big else 3000
    return max(base, min(30, base + math.sqrt(v / div)))

m = folium.Map(location=[39.4, -0.7], zoom_start=8, tiles="CartoDB positron")

cob_60 = folium.FeatureGroup(name="Cobertura 60 min (vehicle)", show=True)
cob_30 = folium.FeatureGroup(name="Cobertura 30 min (vehicle)", show=True)
zona_descoberta = folium.FeatureGroup(name="Zona sense cobertura reglada", show=False)

for feat in cobertura['features']:
    tipus = feat['properties']['tipus']
    if tipus == 'cobertura_60min':
        folium.GeoJson(
            feat,
            style_function=lambda x: {
                'fillColor': '#AED6F1',
                'color': '#2E86C1',
                'weight': 1,
                'fillOpacity': 0.25,
            },
            tooltip="Cobertura 60 min en vehicle"
        ).add_to(cob_60)
    elif tipus == 'cobertura_30min':
        folium.GeoJson(
            feat,
            style_function=lambda x: {
                'fillColor': '#2E8B57',
                'color': '#1a5c35',
                'weight': 1,
                'fillOpacity': 0.30,
            },
            tooltip="Cobertura 30 min en vehicle"
        ).add_to(cob_30)

cob_60.add_to(m)
cob_30.add_to(m)

grup_names = [
    'Conservatoris GVA', 'Conservatoris Municipals',
    'Centres Autoritzats', 'Escoles Publiques', 'Escoles Privades', 'Altres',
]
grups = {n: folium.FeatureGroup(name=n, show=True) for n in grup_names}

for _, row in df.iterrows():
    label, color, grup_key = classify(row)
    nom     = str(row.get('denominacion', ''))
    munic   = str(row.get('localidad', ''))
    comarca = str(row.get('comarca', ''))
    prov    = str(row.get('provincia', ''))
    cif     = str(row.get('cif', ''))
    tit     = str(row.get('titular', ''))
    sa      = row.get('subv_linia_A_2024', None)
    sb      = row.get('subv_linia_B_2024', None)
    st      = row.get('subv_total_2024',   None)
    integrat = str(row.get('centre_integrat', '')).strip().lower() in ('true', '1', 'yes')
    nota    = str(row.get('nota_relacio', ''))

    border_color = '#000000' if integrat else color
    border_width = 2.5 if integrat else 1

    popup = "<div style='font-family:Arial;min-width:250px;font-size:12px'>"
    popup += "<b style='font-size:13px'>" + nom + "</b><br>"
    popup += "<span style='color:#666;font-size:11px'>" + label + "</span><br>"
    if integrat:
        popup += "<span style='background:#FFF3CD;padding:1px 4px;border-radius:3px;font-size:10px'>Registres vinculats</span><br>"
    popup += "<span style='color:#999;font-size:10px'>Titular: " + tit + "</span><br>"
    popup += "<hr style='margin:4px 0'/>"
    popup += "<b>Municipi:</b> " + munic + "<br>"
    popup += "<b>Comarca:</b> " + comarca + "<br>"
    popup += "<b>Provincia:</b> " + prov + "<br>"
    popup += "<b>CIF:</b> " + cif + "<br>"
    popup += "<hr style='margin:4px 0'/>"
    popup += "<b>Subvencio Linia A 2024:</b> " + fmt(sa) + "<br>"
    popup += "<b>Subvencio Linia B 2024:</b> " + fmt(sb) + "<br>"
    popup += "<b style='color:#B8860B'>Total subvencio publica 2024:</b> " + fmt(st)
    if nota and nota != 'nan':
        popup += "<hr style='margin:4px 0'/>"
        popup += "<span style='color:#555;font-size:10px'>" + nota + "</span>"
    popup += "</div>"

    folium.CircleMarker(
        location=[row['latitud'], row['longitud']],
        radius=radius(st, label),
        color=border_color,
        weight=border_width,
        fill=True,
        fill_color=color,
        fill_opacity=0.75,
        popup=folium.Popup(popup, max_width=320),
        tooltip=nom + " | " + label + (" [reg.vinculats]" if integrat else "") + " | " + fmt(st),
    ).add_to(grups[grup_key])

for g in grups.values():
    g.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

titol = "<div style='position:fixed;top:10px;left:50%;transform:translateX(-50%);"
titol += "z-index:1000;background:white;padding:10px 20px;border-radius:8px;"
titol += "box-shadow:0 2px 8px rgba(0,0,0,0.3);font-family:Arial;font-size:14px;"
titol += "font-weight:bold;color:#1A3A5C;text-align:center'>"
titol += "Cartografia de les Ensenyances Musicals - Comunitat Valenciana 2026<br>"
titol += "<span style='font-size:11px;font-weight:normal;color:#666'>"
titol += "509 centres - Cobertura reglada 30/60 min en vehicle</span></div>"
m.get_root().html.add_child(folium.Element(titol))

llegenda = "<div style='position:fixed;bottom:30px;left:20px;z-index:1000;"
llegenda += "background:white;padding:12px;border-radius:8px;"
llegenda += "box-shadow:0 2px 6px rgba(0,0,0,0.2);font-family:Arial;font-size:11px'>"
llegenda += "<b>Cobertura de formacio reglada</b><br>"
llegenda += "<span style='color:#2E8B57'>&#9632;</span> Zona a menys de 30 min<br>"
llegenda += "<span style='color:#AED6F1'>&#9632;</span> Zona a menys de 60 min<br>"
llegenda += "<span style='color:#E8E8E8'>&#9632;</span> Zona sense cobertura<br>"
llegenda += "<br><b>Tipus de centre</b><br>"
llegenda += "<span style='color:#8B6914'>&#9679;</span> Conservatori Superior (GVA)<br>"
llegenda += "<span style='color:#E8A020'>&#9679;</span> Cons. Professional (GVA)<br>"
llegenda += "<span style='color:#F5C842'>&#9679;</span> Cons. Professional (Municipal)<br>"
llegenda += "<span style='color:#FAE08A'>&#9679;</span> Cons. Elemental (Municipal)<br>"
llegenda += "<span style='color:#8B1A1A'>&#9679;</span> Centre Autoritzat Professional<br>"
llegenda += "<span style='color:#C45C5C'>&#9679;</span> Centre Autoritzat Elemental<br>"
llegenda += "<span style='color:#2E8B57'>&#9679;</span> Escola Publica de Musica<br>"
llegenda += "<span style='color:#2E6DA4'>&#9679;</span> Escola Privada de Musica<br>"
llegenda += "<br><b>Vora negra</b> = Registres vinculats<br>"
llegenda += "<b>Mida</b> = proporcional a la subvencio 2024</div>"
m.get_root().html.add_child(folium.Element(llegenda))

out = os.path.join(MAP_DIR, "index.html")
m.save(out)
print("Mapa v4 guardat: " + out)