import geopandas as gpd
import json, os
from shapely.ops import unary_union
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.expanduser("~/ensemusCV")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
GEO_DIR  = os.path.join(BASE_DIR, "data", "geo")

print("Carregant shapefile CV...")
gdf_esp = gpd.read_file(os.path.join(GEO_DIR, "spain_communities.geojson"))
cv = gdf_esp[gdf_esp['cod_ccaa'] == '10'].copy()
cv = cv.to_crs(epsg=4326)
cv_shape = cv.geometry.unary_union
print("CV carregada. Area aprox: " + str(round(cv_shape.area, 4)))

print("Carregant isocrones...")
with open(os.path.join(PROC_DIR, "isocrones_centres_reglats.geojson"), encoding='utf-8') as f:
    iso_data = json.load(f)

gdf_iso = gpd.GeoDataFrame.from_features(iso_data['features'], crs="EPSG:4326")
print("Isocrones carregades: " + str(len(gdf_iso)))
print("Columnes: " + str(gdf_iso.columns.tolist()))

iso_30 = gdf_iso[gdf_iso['value'] <= 1800].copy()
iso_60 = gdf_iso[gdf_iso['value'] > 1800].copy()
print("Isocrones 30 min: " + str(len(iso_30)))
print("Isocrones 60 min: " + str(len(iso_60)))

print("Dissolve i retall per la costa...")
dissolve_30 = unary_union(iso_30.geometry)
dissolve_60 = unary_union(iso_60.geometry)

dissolve_30_cv = dissolve_30.intersection(cv_shape)
dissolve_60_cv = dissolve_60.intersection(cv_shape)

result = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"tipus": "cobertura_60min", "label": "Cobertura 60 min"},
            "geometry": dissolve_60_cv.__geo_interface__
        },
        {
            "type": "Feature",
            "properties": {"tipus": "cobertura_30min", "label": "Cobertura 30 min"},
            "geometry": dissolve_30_cv.__geo_interface__
        }
    ]
}

out = os.path.join(PROC_DIR, "cobertura_dissolve.geojson")
with open(out, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print("Guardat: " + out)
print("Dissolve completat.")