import os, re
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import pandas as pd

BASE_DIR = os.path.expanduser("~/ensemusCV")
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw", "serie_historica")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")

YEARS_OCR = ["2022", "2023"]

def needs_ocr(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[4:8]:
            words = page.extract_words()
            if words and len(words) > 10:
                return False
    return True

def parse_line(line, year):
    line = line.strip()
    if len(line) < 10:
        return None
    cif_match = re.search(r'\b[A-Z][O0]\d{6}[A-Z0-9]\b|\b[A-Z]\d{7}[A-Z0-9]\b', line)
    if not cif_match:
        return None
    cif = cif_match.group().replace('O','0')
    if not re.match(r'^[A-Z]\d{7}[A-Z0-9]$', cif):
        return None
    amount_match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*€?', line)
    if not amount_match:
        return None
    try:
        amount = float(amount_match.group(1).replace('.','').replace(',','.'))
    except:
        return None
    if amount < 1000:
        return None
    name_part = line[:cif_match.start()].strip()
    name_part = re.sub(r'^\d+\s+', '', name_part).strip()
    return {"any": year, "cif": cif, "nom": name_part[:80],
            "quantia": amount, "tipus_subvencio": "A_escoles_no_formals"}

def ocr_pdf(pdf_path, year):
    print(f"  Convertint a imatges (dpi=200)...")
    images = convert_from_path(pdf_path, dpi=200)
    print(f"  {len(images)} pagines. Aplicant OCR (rotacio 270)...")
    records = []
    for i, img in enumerate(images):
        img_rot = img.rotate(270, expand=True)
        text = pytesseract.image_to_string(img_rot, lang="spa+cat")
        for line in text.split("\n"):
            rec = parse_line(line, year)
            if rec:
                records.append(rec)
        if (i+1) % 4 == 0:
            print(f"  Pagina {i+1}/{len(images)} - registres fins ara: {len(records)}")
    return records

all_records = []
for year in YEARS_OCR:
    pdf_path = os.path.join(RAW_DIR, f"subvencions_escoles_musica_{year}.pdf")
    if not os.path.exists(pdf_path):
        print(f"No trobat: {pdf_path}")
        continue
    print(f"\nProcessant {year}...")
    recs = ocr_pdf(pdf_path, year)
    print(f"  Registres: {len(recs)}")
    if recs:
        total = sum(r['quantia'] for r in recs)
        print(f"  Total: {total:,.0f} EUR")
        for r in recs[:3]:
            print(f"  {r}")
    all_records.extend(recs)

if all_records:
    df = pd.DataFrame(all_records)
    out = os.path.join(PROC_DIR, "serie_historica_ocr.csv")
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"\nGuardat: {out}")
    print(df.groupby('any').agg(n=('cif','count'), total=('quantia','sum')).to_string())
else:
    print("Cap registre extret.")