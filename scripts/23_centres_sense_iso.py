import json, os, pandas as pd
import unicodedata

BASE = os.path.expanduser("~/ensemusCV")

with open(os.path.join(BASE, "data/processed/isocrones_centres_reglats.geojson")) as f:
    iso = json.load(f)

iso_coords = set()
for feat in iso['features']:
    lat = feat['properties'].get('centre_lat')
    lon = feat['properties'].get('centre_lon')
    if lat and lon:
        iso_coords.add((round(float(lat),4), round(float(lon),4)))

print("Coordenades amb isocrona: " + str(len(iso_coords)))

df = pd.read_csv(os.path.join(BASE, "data/processed/centres_musicals_enriquits.csv"))

def norm(s):
    if not isinstance(s, str): return ''
    return ''.join(c for c in unicodedata.normalize('NFD', s.upper())
                   if unicodedata.category(c) != 'Mn')

reglats = df[df['denominacion_generica_es'].apply(
    lambda x: any(k in norm(str(x)) for k in
    ['CONSERVATORIO','CONSERVATORI','AUTORIZADO','AUTORITZAT','INTEGRADO','INTEGRAT'])
)].copy()

reglats['lat_r'] = reglats['latitud'].apply(lambda x: round(float(x),4) if pd.notna(x) else None)
reglats['lon_r'] = reglats['longitud'].apply(lambda x: round(float(x),4) if pd.notna(x) else None)

print("Centres reglats: " + str(len(reglats)))
print()
print("Centres SENSE isocrona (per coordenades):")
sense = []
for _, row in reglats.iterrows():
    coord = (row['lat_r'], row['lon_r'])
    if coord not in iso_coords:
        sense.append(row)
        print("  " + str(row['denominacion'])[:55] + " | " + str(row['localidad']))

print()
print("Total sense isocrona: " + str(len(sense)))