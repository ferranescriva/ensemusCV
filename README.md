# Cartografia de les Ensenyances Musicals a la Comunitat Valenciana

**Dataset i mapa interactiu de centres d'ensenyament musical de la Comunitat Valenciana**

🗺️ **[Accés al mapa interactiu](https://ferranescriva.github.io/ensemusCV/maps/index.html)**

---

## Descripció

Aquest projecte construeix una base de dades integrada i una cartografia interactiva de tots els centres d'ensenyament musical de la Comunitat Valenciana, incloent-hi:

- Escoles de música (privades i públiques)
- Conservatoris (elementals, professionals i superiors)
- Centres autoritzats d'ensenyaments artístics
- Centres integrats de música i ensenyaments de règim general

## Dades

| Camp | Detall |
|---|---|
| **Font principal** | [Dades Obertes GVA](https://dadesobertes.gva.es/es/dataset/edu-centros) |
| **Data de descàrrega** | 04/05/2026 |
| **Total centres musicals** | 509 |
| **Cobertura territorial** | Comunitat Valenciana (València, Alacant, Castelló) |
| **Llicència dades** | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

## Estructura del repositori

ensemusCV/
├── data/
│   ├── raw/                  # Dades originals sense modificar
│   └── processed/            # Dades netes i integrades
├── scripts/
│   ├── 01_download_gva.py    # Descàrrega dataset GVA
│   ├── 02_filter_music.py    # Filtratge centres musicals
│   └── 03_build_map.py       # Generació mapa interactiu
├── maps/
│   └── index.html            # Mapa interactiu (GitHub Pages)
├── docs/                     # Documentació metodològica
├── LIMITACIONS.md            # Llacunes i biaixos coneguts
└── CHANGELOG.md              # Historial de versions
## Com reproduir

```bash
git clone https://github.com/ferranescriva/ensemusCV.git
cd ensemusCV
pip3 install pandas geopandas folium requests pdfplumber geopy openpyxl
python3 scripts/01_download_gva.py
python3 scripts/02_filter_music.py
python3 scripts/03_build_map.py
```

## Limitacions conegudes

Vegeu [LIMITACIONS.md](LIMITACIONS.md) per a una descripció detallada dels biaixos i llacunes del dataset.

## Com citar

Escrivà-Llorca, F. (2026). Cartografia de les Ensenyances Musicals a la Comunitat Valenciana (ensemusCV) (v0.1) [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.20041738

## Autor

**Ferran Escrivà-Llorca**  
Profesor Ayudante Doctor — Didàctica de l'Expressió Musical  
Facultat de Magisteri, Universitat de València  

## Llicència

Codi: [MIT License](LICENSE)  
Dades i documentació: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
