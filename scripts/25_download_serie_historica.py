import requests, os, time

BASE_DIR = os.path.expanduser("~/ensemusCV")
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw", "serie_historica")
os.makedirs(RAW_DIR, exist_ok=True)

PDFS = {
    "2019_7803": "https://dogv.gva.es/datos/2019/08/02/pdf/2019_7803.pdf",
    "2019_7804": "https://dogv.gva.es/datos/2019/08/02/pdf/2019_7804.pdf",
    "2021_A":    "https://dogv.gva.es/datos/2021/11/08/pdf/2021_10985.pdf",
    "2021_B":    "https://dogv.gva.es/datos/2021/10/27/pdf/2021_10840.pdf",
    "2022":      "https://dogv.gva.es/datos/2022/08/31/pdf/2022_7333.pdf",
    "2023":      None,
    "2024":      "https://dogv.gva.es/datos/2024/07/03/pdf/2024_6438.pdf",
    "2025":      "https://dogv.gva.es/datos/2025/12/19/pdf/2025_51124_es.pdf",
}

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

for key, url in PDFS.items():
    if url is None:
        print(f"{key}: ja tenim (manual)")
        continue
    filename = f"subvencions_escoles_musica_{key}.pdf"
    path = os.path.join(RAW_DIR, filename)
    if os.path.exists(path):
        print(f"{key}: ja existeix ({os.path.getsize(path)//1024} KB)")
        continue
    print(f"{key}: descarregant...")
    try:
        r = requests.get(url, headers=headers, timeout=60)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"  OK: {os.path.getsize(path)//1024} KB")
    except Exception as e:
        print(f"  ERROR: {e}")
    time.sleep(1)

print("\nFitxers disponibles:")
for f in sorted(os.listdir(RAW_DIR)):
    size = os.path.getsize(os.path.join(RAW_DIR, f))
    print(f"  {f}: {size//1024} KB")