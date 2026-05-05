import json, os

BASE = os.path.expanduser("~/ensemusCV")
with open(os.path.join(BASE, "data/processed/isocrones_centres_reglats.geojson")) as f:
    iso = json.load(f)

noms = sorted(set(feat['properties'].get('centre_nom','') for feat in iso['features']))
print("Noms al GeoJSON (" + str(len(noms)) + "):")
for n in noms:
    print("  " + n)