import geopandas as gpd
import json, os
from shapely.ops import unary_union
from shapely.validation import make_valid
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.expanduser("~/ensemusCV")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
GEO_DIR  = os.path.join(BASE_DIR, "data", "geo")

print("Carregant shapefile CV...")
gdf_esp = gpd.read_file(os.path.join(GEO_DIR, "spain_communities.geojson"))
cv = gdf_esp[gdf_esp['cod_ccaa'] == '10'].copy()
cv = cv.to_crs(epsg=4326)
cv_shape = make_valid(cv.geometry.unary_union)
print("CV bounds: " + str(cv_shape.bounds))

print("Carregant isocrones...")
with open(os.path.join(PROC_DIR, "isocrones_centres_reglats.geojson"), encoding='utf-8') as f:
    iso_data = json.load(f)

gdf_iso = gpd.GeoDataFrame.from_features(iso_data['features'], crs="EPSG:4326")
gdf_iso['geometry'] = gdf_iso['geometry'].apply(make_valid)

iso_30 = gdf_iso[gdf_iso['value'] <= 1800].copy()
iso_60 = gdf_iso[gdf_iso['value'] > 1800].copy()
print("Isocrones 30min: " + str(len(iso_30)) + " | 60min: " + str(len(iso_60)))

print("Dissolve...")
dissolve_30 = make_valid(unary_union(iso_30.geometry))
dissolve_60 = make_valid(unary_union(iso_60.geometry))

print("Dissolve 30min bounds: " + str(dissolve_30.bounds))
print("Dissolve 60min bounds: " + str(dissolve_60.bounds))

print("Retall per la costa...")
dissolve_30_cv = dissolve_30.intersection(cv_shape)
dissolve_60_cv = dissolve_60.intersection(cv_shape)

print("Resultat 30min bounds: " + str(dissolve_30_cv.bounds))
print("Resultat 60min bounds: " + str(dissolve_60_cv.bounds))

from shapely.geometry import Point
test_alacant = Point(-0.492, 38.352)
test_alacant2 = Point(-0.474, 38.165)
print("Alacant centre dins dissolve_30: " + str(dissolve_30.contains(test_alacant)))
print("Alacant centre dins dissolve_30_cv: " + str(dissolve_30_cv.contains(test_alacant)))
print("Alacant centroide mun dins dissolve_30: " + str(dissolve_30.contains(test_alacant2)))
print("Alacant centroide mun dins dissolve_30_cv: " + str(dissolve_30_cv.contains(test_alacant2)))

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