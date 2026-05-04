import requests
import pandas as pd
from datetime import date
import os

CSV_URL    = "https://dadesobertes.gva.es/dataset/68eb1d94-76d3-4305-8507-e1aab7717d0e/resource/1aa53c3a-4639-41aa-ac85-d58254c428c0/download/centros-docentes-de-la-comunitat-valenciana.csv"
OUTPUT_DIR = "../data/raw"
TODAY      = date.today().strftime("%Y%m%d")

def download_dataset(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print("Descarregant dataset edu-centros...")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    output_path = os.path.join(output_dir, f"edu_centros_gva_{TODAY}.csv")
    with open(output_path, "wb") as f:
        f.write(r.content)
    df = pd.read_csv(output_path, encoding="utf-8", sep=";", low_memory=False)
    print(f"Total registres: {len(df)}")
    print(f"Fitxer guardat: {output_path}")
    print("\nColumnes disponibles:")
    for col in df.columns:
        print(f"  - {col}")
    return df

if __name__ == "__main__":
    df = download_dataset(CSV_URL, OUTPUT_DIR)
