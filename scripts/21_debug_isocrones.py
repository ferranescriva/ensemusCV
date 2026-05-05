import json, os, pandas as pd
import unicodedata

BASE = os.path.expanduser("~/ensemusCV")

with open(os.path.join(BASE, "data/processed/isocrones_centres_reglats.geojson")) as f:
    iso = json.load(f)

noms_iso = set()
for feat in iso['features']:
    noms_iso.add(feat['properties'].get('centre_nom',''))

print("Total centres amb isocrona: " + str(len(noms_iso)))

df = pd.read_csv(os.path.join(BASE, "data/processed/centres_musicals_enriquits.csv"))

def norm(s):
    if not isinstance(s, str): return ''
    return ''.join(c for c in unicodedata.normalize('NFD', s.upper())
                   if unicodedata.category(c) != 'Mn')

reglats = df[df['denominacion_generica_es'].apply(
    lambda x: any(k in norm(str(x)) for k in
    ['CONSERVATORIO','CONSERVATORI','AUTORIZADO','AUTORITZAT','INTEGRADO','INTEGRAT'])
)]

print("Centres reglats al dataset: " + str(len(reglats)))
print()
print("Centres SENSE isocrona:")
for _, row in reglats.iterrows():
    nom = str(row['denominacion'])[:50]
    if nom not in noms_iso:
        print("  " + nom + " | " + str(row.get('localidad','')))