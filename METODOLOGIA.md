# Metodologia — Cartografia de les Ensenyances Musicals a la Comunitat Valenciana

## Versió 0.1 — Maig 2026

---

## 1. Objectiu i pregunta de recerca

Aquest projecte construeix una infraestructura de dades i una cartografia interactiva de tots els centres d'ensenyament musical de la Comunitat Valenciana. La pregunta de recerca principal és:

> **Existeix equitat territorial en l'accés a la formació musical reglada a la Comunitat Valenciana?**

Les preguntes secundàries son:
- Quina és la distribució geogràfica dels centres de formació musical per tipologia i titularitat?
- Quins municipis valencians queden fora de la cobertura de 30 i 60 minuts en vehicle d'algun centre de formació musical reglada?
- Quin és el volum de finançament públic que rep el sistema musical valencià i com es distribueix territorialment?

---

## 2. Fonts de dades

### 2.1 Centres educatius

**Font principal**: Dataset `edu-centros` de dadesobertes.gva.es (Conselleria d'Educació, Universitats i Ocupació, Generalitat Valenciana). Descarregat via API CKAN el 04/05/2026.

- Total registres originals: 3.685 centres docents de la CV
- Filtrat per tipologia: 509 centres musicals de totes les categories
- Camps principals usats: denominacion_generica_es, denominacion, regimen, titular, cif, localidad, comarca, provincia, latitud, longitud, fe_constitucion

**Llicència de la font**: Dades obertes GVA — reutilització lliure amb atribució.

### 2.2 Subvencions públiques (proxy de finançament)

**Línia A — Escoles no formals de música**: Resolucions de concessió de subvencions destinades a escoles que imparteixen ensenyament no formal de música, dependents d'entitats locals o privades. Convocatòria anual de la Direcció General de Centres Docents (DOGV). Anys disponibles: 2024 (n=385 centres, 11.300.000 EUR) i 2025 (n=380 centres, 11.290.990 EUR).

**Línia B — Conservatoris i centres autoritzats**: Resolucions de concessió de subvencions a conservatoris municipals, centres autoritzats i centres integrats d'ensenyaments artístics professionals. Convocatòria anual de la Direcció General de Centres Docents (DOGV). Any disponible: 2024 (n=67 centres, 10.470.000 EUR).

**Nota metodològica**: Les Línies A i B no son comparables entre si. La Línia A finança despeses ordinàries d'escoles no formals; la Línia B finança centres de formació reglada amb criteris de baremació i imports molt superiors. El dataset inclou la columna tipus_subvencio per fer explícita aquesta distinció. Les quanties del proxy corresponen a l'exercici 2024 (any de referència).

**Extracció**: Els PDFs de les resolucions del DOGV s'han processat amb pdfplumber. Les pàgines dels annexos estaven girades 90 graus i amb text invertit; el parser aplica inversió de text per columna i expressió regular per a la detecció de CIF i quanties.

### 2.3 Capa geogràfica de municipis

Capa cartogràfica de municipis de la Comunitat Valenciana (font ICV, via josemamira/GitHub). 548 registres originals, 539 despres de deduplicació per codi INE (mantenint el polígon de major àrea per a municipis amb geometries múltiples). Projecció: EPSG:4326.

### 2.4 Límits territorials de la Comunitat Valenciana

Shapefile de comunitats autònomes espanyoles (CodeForGermany/click_that_hood). Filtrat per cod_ccaa = '10'. Usat per al retall costaner de les isocrones.

---

## 3. Processament de dades

### 3.1 Filtratge de centres musicals

Del total de 3.685 centres docents, s'han seleccionat els centres amb tipologia musical mitjançant comparació normalitzada (sense accents, en majúscules) de la columna denominacion_generica_es. Categories incloses: 13 tipologies musicals i mixtes. Categories excloses: centres d'ensenyament general sense component musical específic.

### 3.2 Creuament centres — subvencions

El creuament entre el dataset de centres (coordenades i tipologia) i el proxy de subvencions (CIF i quantia) s'ha realitzat per la columna CIF com a clau primària. Cobertura del creuament: 435 de 509 centres (85,5%) disposen de dada de finançament per a 2024.

### 3.3 Identificació d'entitats amb doble registre administratiu

S'han identificat 30 CIFs duplicats que afecten 64 registres. Per a cada cas s'ha realitzat verificació externa (web oficial de l'entitat, registre mercantil, bases de dades de subvencions) per determinar si els registres corresponen a:
- Una mateixa seu física (etiquetats com "Registres vinculats" al mapa)
- Seus físiques diferenciades (mantinguts com a punts separats amb nota de relació)
- Xarxes territorials (mantinguts com a punts separats amb camp gestora)

Vegeu LIMITACIONS.md per a la descripció detallada de cada cas i els criteris de tractament.

### 3.4 Isocrones d'accessibilitat

S'han calculat isocrones de 30 i 60 minuts en vehicle per als 96 centres de formació musical reglada (conservatoris, centres autoritzats i centres integrats) mitjançant l'API d'OpenRouteService (perfil driving-car). Total: 192 isocrones (96 centres x 2 intervals temporals). Les isocrones s'han fusionat (dissolve) mitjançant unary_union de Shapely i retallat per la línia de costa de la CV per eliminar àrees marítimes.

### 3.5 Anàlisi de cobertura municipal

El creuament entre els polígons de cobertura i els 539 municipis (deduplicats) de la CV s'ha realitzat mitjançant representative_point() de Shapely — un punt garantit dins del polígon municipal, més proper al nucli urbà que el centroide geomètric. Dades de població: columna pop del GeoJSON de municipis (any de referència del dataset original).

---

## 4. Resultats principals

### 4.1 Distribució de centres

- Total centres musicals identificats: 509
- Centres de formació reglada (conservatoris + centres autoritzats): 96
- Distribució per titularitat: 22 conservatoris de la Generalitat Valenciana, 29 de titularitat municipal, 44 de titularitat privada/associativa
- Comarques amb centres reglats: 25 de 33

### 4.2 Finançament públic (2024)

- Línia A (escoles no formals): 11.300.000 EUR / 385 centres (mitjana: 29.350 EUR/centre)
- Línia B (conservatoris i centres autoritzats): 10.470.000 EUR / 67 centres (mitjana: 156.269 EUR/centre)
- Total finançament públic GVA al sistema musical (2024): 21.770.000 EUR

### 4.3 Cobertura territorial

- Municipis amb cobertura a 30 min en vehicle: 399 (74,0%)
- Municipis amb cobertura entre 30 i 60 min: 103 (19,1%)
- Municipis fora de cobertura a 60 min: 37 (6,9%)
- Poblacio coberta a 60 min: 4.975.262 habitants (98,7% de la poblacio total CV)
- Poblacio fora de cobertura: 16.944 habitants (1,3%)
- Perfil dels municipis fora de cobertura: interior de Castelló (22 municipis) i interior de Valencia (15 municipis). Tots de menys de 2.500 habitants excepte Morella (2.430 hab.)

---

## 5. Eines i entorn tecnològic

- Python 3.9/3.14 amb les biblioteques: pandas, geopandas, folium, shapely, pdfplumber, requests, geopy
- Control de versions: Git / GitHub (github.com/ferranescriva/ensemusCV)
- Isocrones: OpenRouteService API (perfil driving-car, pla gratuït)
- Visualització: Folium/Leaflet.js, publicat via GitHub Pages
- Repositori de dades: Zenodo (DOI pendent, versió 1.0 prevista per a desembre 2026)

---

## 6. Reproducibilitat

Tot el codi de processament és públic i reproducible. Per a reproduir l'anàlisi completa des de zero:

```bash
git clone https://github.com/ferranescriva/ensemusCV.git
cd ensemusCV
python3 -m venv .venv
source .venv/bin/activate
pip install pandas geopandas folium requests pdfplumber geopy openpyxl
python3 scripts/01_download_gva.py
python3 scripts/02_filter_music.py
python3 scripts/03_build_map.py
python3 scripts/10_merge_centres_subvencions.py
python3 scripts/11_build_map_v2.py
python3 scripts/14_isocrones.py  # Requereix clau API OpenRouteService
python3 scripts/17_dissolve_isocrones.py
python3 scripts/18_build_map_v4.py
python3 scripts/19_municipis_cobertura.py
```

---

## 7. Com citar

Escrivà-Llorca, F. (2026). *Cartografia de les Ensenyances Musicals a la Comunitat Valenciana* (v0.1) [Dataset, codi i mapa interactiu]. GitHub / Zenodo. https://github.com/ferranescriva/ensemusCV