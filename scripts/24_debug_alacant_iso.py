import json, os

BASE = os.path.expanduser("~/ensemusCV")
with open(os.path.join(BASE, "data/processed/isocrones_centres_reglats.geojson")) as f:
    iso = json.load(f)

print("Isocrones zona Alacant/Alicante:")
for feat in iso['features']:
    lat = feat['properties'].get('centre_lat', 0)
    lon = feat['properties'].get('centre_lon', 0)
    nom = feat['properties'].get('centre_nom', '')
    val = feat['properties'].get('value', 0)
    if float(lat) < 38.5 and float(lat) > 38.1:
        bounds = feat['geometry']['coordinates']
        print(str(val) + "s | " + nom[:45] + " | lat=" + str(lat) + " lon=" + str(lon))
        print("  Tipus: " + feat['geometry']['type'])
        if feat['geometry']['type'] == 'Polygon':
            n_punts = len(feat['geometry']['coordinates'][0])
            print("  N punts polygon: " + str(n_punts))
            lats = [c[1] for c in feat['geometry']['coordinates'][0]]
            lons = [c[0] for c in feat['geometry']['coordinates'][0]]
            print("  Lat min/max: " + str(round(min(lats),3)) + " / " + str(round(max(lats),3)))
            print("  Lon min/max: " + str(round(min(lons),3)) + " / " + str(round(max(lons),3)))