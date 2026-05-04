import requests
import pdfplumber
import os

BASE_DIR = os.path.expanduser("~/ensemusCV")
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

PDFS = {
    "2024": "https://dogv.gva.es/datos/2024/10/18/pdf/2024_10698_va.pdf",
}

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

def download_pdf(url, path):
    r = requests.get(url, timeout=60, headers=headers)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)
    print(f"  OK: {os.path.basename(path)} ({len(r.content)//1024} KB)")

def show_annex_pages(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        print(f"Total pagines: {total}")
        for i in range(max(0, total-5), total):
            page = pdf.pages[i]
            words = page.extract_words()
            if not words:
                continue
            print(f"\n=== PAGINA {i+1} ===")
            for w in words[:50]:
                print(f"  x={w['x0']:6.1f} y={w['top']:6.1f}  '{w['text']}'")

for year, url in PDFS.items():
    pdf_path = os.path.join(RAW_DIR, f"subvencions_conservatoris_{year}.pdf")
    print(f"--- {year} ---")
    try:
        download_pdf(url, pdf_path)
        show_annex_pages(pdf_path)
    except Exception as e:
        print(f"  ERROR: {e}")