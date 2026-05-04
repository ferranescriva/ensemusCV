import requests
import pdfplumber
import os

BASE_DIR = os.path.expanduser("~/ensemusCV")
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

PDFS = {
    "2025": "https://dogv.gva.es/datos/2025/12/19/pdf/2025_51124_es.pdf",
    "2024": "https://dogv.gva.es/datos/2024/07/03/pdf/2024_6438.pdf",
    "2023": "https://dogv.gva.es/datos/2023/06/13/pdf/2023_5948.pdf",
    "2022": "https://dogv.gva.es/datos/2022/08/31/pdf/2022_8169.pdf",
}

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

def download_pdf(url, path):
    r = requests.get(url, timeout=60, headers=headers)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)
    print(f"  OK: {os.path.basename(path)} ({len(r.content)//1024} KB)")

def show_sample(pdf_path, start=2000, length=600):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    print(text[start:start+length])

for year, url in PDFS.items():
    pdf_path = os.path.join(RAW_DIR, f"subvencions_escoles_musica_{year}.pdf")
    print(f"--- {year} ---")
    try:
        download_pdf(url, pdf_path)
        show_sample(pdf_path)
    except Exception as e:
        print(f"  ERROR: {e}")