import os
import pytesseract
from pdf2image import convert_from_path

BASE_DIR = os.path.expanduser("~/ensemusCV")
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw", "serie_historica")

for year in ["2022", "2023"]:
    pdf_path = os.path.join(RAW_DIR, f"subvencions_escoles_musica_{year}.pdf")
    print(f"\n=== OCR {year} (pagines 5-7) ===")
    images = convert_from_path(pdf_path, dpi=200, first_page=5, last_page=7)
    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img, lang="spa+cat")
        print(f"--- Pagina {i+5} ---")
        print(text[:1500])
        print("...")