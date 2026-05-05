import geopandas as gpd, os
import warnings
warnings.filterwarnings('ignore')

BASE = os.path.expanduser("~/ensemusCV")
gdf_cob = gpd.read_file(os.path.join(BASE, "data/processed/cobertura_dissolve.geojson"))
gdf_mun = gpd.read_file(os.path.join(BASE, "data/geo/municipis_cv.geojson"))
gdf_mun = gdf_mun.to_crs(epsg=4326)

alacant = gdf_mun[gdf_mun['nombre'].str.contains('Alicante', na=False)]
print("Files Alacant: " + str(len(alacant)))
print("Centroid: " + str(alacant.geometry.centroid.values))

cob_30 = gdf_cob[gdf_cob['tipus']=='cobertura_30min'].geometry.unary_union
cob_60 = gdf_cob[gdf_cob['tipus']=='cobertura_60min'].geometry.unary_union

cent = alacant.geometry.centroid.values[0]
print("Dins 30min: " + str(cob_30.contains(cent)))
print("Dins 60min: " + str(cob_60.contains(cent)))

print("\nBounds cobertura 30min: " + str(cob_30.bounds))
print("Bounds cobertura 60min: " + str(cob_60.bounds))