import geopandas as gpd
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.expanduser("~/ensemusCV")
GEO_DIR  = os.path.join(BASE_DIR, "data", "geo")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")

print("Carregant municipis CV...")
gdf_mun = gpd.read_file(os.path.join(GEO_DIR, "municipis_cv.geojson"))
gdf_mun = gdf_mun.to_crs(epsg=4326)
gdf_mun['pop'] = pd.to_numeric(gdf_mun['pop'], errors='coerce').fillna(0).astype(int)
gdf_mun['area'] = gdf_mun.geometry.area

before = len(gdf_mun)
gdf_mun = gdf_mun.sort_values('area', ascending=False).drop_duplicates(subset='codine', keep='first')
print("Municipis abans: " + str(before) + " | despres dedup: " + str(len(gdf_mun)))

gdf_mun['rep_point'] = gdf_mun.geometry.representative_point()

print("Carregant cobertura dissolve...")
gdf_cob = gpd.read_file(os.path.join(PROC_DIR, "cobertura_dissolve.geojson"))
gdf_cob = gdf_cob.to_crs(epsg=4326)

cob_30 = gdf_cob[gdf_cob['tipus'] == 'cobertura_30min'].geometry.unary_union
cob_60 = gdf_cob[gdf_cob['tipus'] == 'cobertura_60min'].geometry.unary_union

def check_cobertura(point):
    if cob_30 and cob_30.contains(point):
        return '30min'
    elif cob_60 and cob_60.contains(point):
        return '60min'
    else:
        return 'fora'

print("Creuant municipis amb cobertura...")
gdf_mun['cobertura'] = gdf_mun['rep_point'].apply(check_cobertura)

resum = gdf_mun.groupby('cobertura').agg(
    municipis=('nombre', 'count'),
    poblacio=('pop', 'sum')
).reset_index()
print("\n=== RESUM DE COBERTURA ===")
print(resum.to_string())

fora = gdf_mun[gdf_mun['cobertura'] == 'fora'].sort_values('pop', ascending=False)
print("\n=== MUNICIPIS FORA DE COBERTURA (60 min) ===")
print("Total municipis: " + str(len(fora)))
print("Total poblacio: " + str(fora['pop'].sum()))
print()
print(fora[['nombre','provincia','pop']].to_string())

out = os.path.join(PROC_DIR, "municipis_cobertura.csv")
gdf_mun[['codine','nombre','provincia','pop','cobertura']].to_csv(out, index=False)
print("\nGuardat: " + out)