import requests, json, os, time
import pandas as pd
import folium

BASE_DIR = os.path.expanduser("~/ensemusCV")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
MAP_DIR  = os.path.join(BASE_DIR, "maps")
OUT_DIR  = os.path.join(BASE_DIR, "data", "processed")

API_KEY = os.environ.get("ORS_API_KEY")
if not API_KEY:
    raise ValueError("ORS_API_KEY no trobada. Executa: source ~/.zshrc")

df = pd.read_csv(os.path.join(PROC_DIR, "centres_musicals_enriquits.csv"))
df['lat'] = pd.to_numeric(df['latitud'], errors='coerce')
df['lon'] = pd.to_numeric(df['longitud'], errors='coerce')
df = df.dropna(subset=['lat','lon'])

import unicodedata
def norm(s):
    if not isinstance(s, str): return ''
    return ''.join(c for c in unicodedata.normalize('NFD', s.upper())
                   if unicodedata.category(c) != 'Mn')

reglats = df[df['denominacion_generica_es'].apply(
    lambda x: any(k in norm(str(x)) for k in
    ['CONSERVATORIO','CONSERVATORI','AUTORIZADO','AUTORITZAT','INTEGRADO','INTEGRAT'])
)].copy()

print("Centres reglats a processar: " + str(len(reglats)))

URL = "https://api.openrouteservice.org/v2/isochrones/driving-car"
HEADERS = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

all_features = []
errors = 0

for i, (_, row) in enumerate(reglats.iterrows()):
    nom = str(row.get('denominacion',''))
    lon = float(row['lon'])
    lat = float(row['lat'])

    body = {
        "locations": [[lon, lat]],
        "range": [1800, 3600],
        "range_type": "time",
        "attributes": ["area"]
    }

    try:
        r = requests.post(URL, headers=HEADERS, json=body, timeout=30)
        if r.status_code == 200:
            data = r.json()
            for feat in data.get('features', []):
                feat['properties']['centre_nom'] = nom
                feat['properties']['centre_lat'] = lat
                feat['properties']['centre_lon'] = lon
                all_features.append(feat)
            print(str(i+1) + "/" + str(len(reglats)) + " OK: " + nom[:40])
        else:
            print(str(i+1) + "/" + str(len(reglats)) + " ERROR " + str(r.status_code) + ": " + nom[:40])
            errors += 1
    except Exception as e:
        print(str(i+1) + "/" + str(len(reglats)) + " EXCEPCIO: " + str(e))
        errors += 1

    time.sleep(0.6)

geojson = {"type": "FeatureCollection", "features": all_features}
out_path = os.path.join(OUT_DIR, "isocrones_centres_reglats.geojson")
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(geojson, f, ensure_ascii=False)

print()
print("Isocrones generades: " + str(len(all_features)))
print("Errors: " + str(errors))
print("Guardat: " + out_path)