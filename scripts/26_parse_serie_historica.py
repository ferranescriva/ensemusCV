import pdfplumber
import pandas as pd
import re
import os

BASE_DIR = os.path.expanduser("~/ensemusCV")
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw", "serie_historica")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)

def rev(s):
    return s[::-1]

def parse_pdf(pdf_path, year):
    records = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
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
                cif_idx = next((j for j, t in enumerate(tokens) if t == cif), None)
                skip = {"EUR", "DE", "I", "Y", "LA", "EL", "LES", "LOS",
                        "MUSICA", "MÚSICA", "DANSA", "DANZA", "PRIVADA",
                        "ESCOLA", "ESCUELA", "PUBLICA", "PÚBLICA", "MUNICIPAL"}
                name_parts = []
                if cif_idx:
                    name_parts = [t for t in tokens[1:cif_idx]
                                  if t.upper() not in skip and len(t) > 2]
                name = " ".join(name_parts).strip()
                if cif:
                    records.append({
                        "any": year,
                        "cif": cif,
                        "nom": name,
                        "quantia": amount,
                        "tipus_subvencio": "A_escoles_no_formals"
                    })
    return records

all_records = []
years = ["2022", "2023", "2024", "2025"]

for year in years:
    pdf_path = os.path.join(RAW_DIR, f"subvencions_escoles_musica_{year}.pdf")
    if not os.path.exists(pdf_path):
        print(f"No trobat: {pdf_path}")
        continue
    print(f"Processant {year}...")
    recs = parse_pdf(pdf_path, year)
    valids = [r for r in recs if r['quantia'] and r['quantia'] > 100]
    print(f"  Registres: {len(recs)} | Amb quantia: {len(valids)}")
    if valids:
        total = sum(r['quantia'] for r in valids)
        print(f"  Total: {total:,.0f} EUR")
    all_records.extend(valids)

df = pd.DataFrame(all_records)
df['any'] = df['any'].astype(str)

print(f"\nTOTAL SERIE: {len(df)} registres")
print(f"CIFs únics: {df['cif'].nunique()}")
print(f"\nPer any:")
print(df.groupby('any').agg(n=('cif','count'), total=('quantia','sum')).to_string())

out = os.path.join(PROC_DIR, "serie_historica_subvencions.csv")
df.to_csv(out, index=False, encoding="utf-8")
print(f"\nGuardat: {out}")