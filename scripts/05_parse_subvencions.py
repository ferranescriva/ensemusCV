import pdfplumber
import pandas as pd
import re
import os

BASE_DIR = os.path.expanduser("~/ensemusCV")
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

def rev(s):
    return s[::-1]

def parse_pdf(pdf_path, year):
    records = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            words = page.extract_words(x_tolerance=3, y_tolerance=3)
            if not words:
                continue

            cols = {}
            for w in words:
                key = round(w['x0'])
                cols.setdefault(key, []).append(w)

            for col_x in sorted(cols.keys()):
                col_words = sorted(cols[col_x], key=lambda w: w['top'])
                tokens = [rev(w['text']) for w in col_words]

                cif = None
                amount = None
                name_parts = []

                for t in tokens:
                    if re.match(r'^[A-Z]\d{7}[A-Z0-9]$', t):
                        cif = t
                    m = re.match(r'^(\d{1,3}(?:\.\d{3})*,\d{2})$', t)
                    if m:
                        try:
                            amount = float(m.group(1).replace(".", "").replace(",", "."))
                        except:
                            pass

                if cif is None:
                    continue

                cif_idx = next((j for j,t in enumerate(tokens) if t == cif), None)
                if cif_idx:
                    candidates = tokens[1:cif_idx]
                    skip = {"€", "ESCOLA", "ESCUELA", "PRIVADA", "DE", "MÚSICA",
                            "MUSICA", "DANSA", "DANZA", "Y", "I", "PÚBLICA",
                            "PUBLICA", "ARTS", "ESCENICAS", "ESCENIQUES"}
                    name_parts = [t for t in candidates
                                  if t.upper() not in skip and len(t) > 2]

                name = " ".join(name_parts).strip()
                if cif:
                    records.append({"any": year, "nom": name, "cif": cif,
                                    "quantia": amount})
    return records

all_records = []
for year in ["2024", "2025"]:
    pdf_path = os.path.join(RAW_DIR, f"subvencions_escoles_musica_{year}.pdf")
    if not os.path.exists(pdf_path):
        continue
    print(f"\nProcessant {year}...")
    recs = parse_pdf(pdf_path, year)
    print(f"  Registres: {len(recs)}")
    for r in recs[:5]:
        print(f"  {r}")
    all_records.extend(recs)

if all_records:
    df = pd.DataFrame(all_records)
    out = os.path.join(PROC_DIR, "proxy_subvencions.csv")
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"\nTotal: {len(df)} registres guardats a {out}")
    print(df[df.quantia.notna()].head(10).to_string())
else:
    print("Cap registre extret.")