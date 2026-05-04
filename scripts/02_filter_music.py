import pandas as pd
from datetime import date
import os

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE  = os.path.join(BASE_DIR, "data", "raw", "edu_centros_gva_20260504.csv")
OUTPUT_DIR  = os.path.join(BASE_DIR, "data", "processed")
TODAY       = date.today().strftime("%Y%m%d")

TIPOLOGIES_MUSICALS = [
    "ESCUELA PRIVADA DE MUSICA",
    "CONSERVATORIO PROFESIONAL DE MUSICA",
    "CENTRO AUTORIZADO DE ENSENANZAS ARTISTICAS PROFESIONALES DE MUSICA",
    "ESCUELA PRIVADA DE MUSICA Y DANZA",
    "ESCUELA PUBLICA DE MUSICA",
    "CENTRO AUTORIZADO ELEMENTAL DE MUSICA",
    "CONSERVATORIO ELEMENTAL DE MUSICA",
    "CONSERVATORIO SUPERIOR DE MUSICA",
    "CENTRO AUTORIZADO SUPERIOR DE MUSICA",
    "ESCUELA PUBLICA DE MUSICA Y DANZA",
    "CONSERVATORIO PROFESIONAL DE MUSICA Y ELEMENTAL DE DANZA",
    "CENTRO INTEGRADO DE MUSICA Y ENSENANZAS DE REGIMEN GENERAL",
    "ESCUELA PRIVADA DE MUSICA Y ARTES ESCENICAS",
]

os.makedirs(OUTPUT_DIR, exist_ok=True)
df = pd.read_csv(INPUT_FILE, sep=";", low_memory=False)

# Normalitzar per comparar sense accents ni majuscules
import unicodedata
def norm(s):
    if not isinstance(s, str):
        return ""
    s = s.upper()
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

df["_tipus_norm"] = df["denominacion_generica_es"].apply(norm)
df_music = df[df["_tipus_norm"].isin(TIPOLOGIES_MUSICALS)].copy()
df_music = df_music.drop(columns=["_tipus_norm"])

output_path = os.path.join(OUTPUT_DIR, f"centres_musicals_cv_{TODAY}.csv")
df_music.to_csv(output_path, index=False, encoding="utf-8")

print(f"Total centres musicals: {len(df_music)}")
print(f"Fitxer guardat: {output_path}")
print(f"\nDistribucio per tipologia:")
print(df_music["denominacion_generica_es"].value_counts().to_string())
print(f"\nDistribucio per comarca (top 10):")
print(df_music["comarca"].value_counts().head(10).to_string())
print(f"\nDistribucio per provincia:")
print(df_music["provincia"].value_counts().to_string())
