import requests, os, zipfile
import geopandas as gpd
from shapely.ops import unary_union
import json

BASE_DIR = os.path.expanduser("~/ensemusCV")
GEO_DIR  = os.path.join(BASE_DIR, "data", "geo")
os.makedirs(GEO_DIR, exist_ok=True)

# Descarregar shapefile de municipis espanyols (Natural Earth / IGN)
URL = "https://github.com/codeforgermany/click_that_hood/raw/main/public/data/spain-communities.geojson"

print("Descarregant limits territorials...")
r = requests.get(URL, timeout=60)
r.raise_for_status()

path = os.path.join(GEO_DIR, "spain_communities.geojson")
with open(path, 'wb') as f:
    f.write(r.content)
print("Guardat: " + path)

gdf = gpd.read_file(path)
print("Comunitats disponibles:")
print(gdf.columns.tolist())
print(gdf.head(3).to_string())