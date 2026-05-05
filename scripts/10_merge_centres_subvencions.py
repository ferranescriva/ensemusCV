import pandas as pd
import os

BASE_DIR = os.path.expanduser("~/ensemusCV")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")

centres = pd.read_csv(os.path.join(PROC_DIR, "centres_musicals_cv_20260504.csv"))
subv    = pd.read_csv(os.path.join(PROC_DIR, "proxy_subvencions_complet.csv"))

subv['any'] = subv['any'].astype(str)
subv['cif'] = subv['cif'].str.strip().str.upper()
centres['cif'] = centres['cif'].astype(str).str.strip().str.upper()

subv_2024 = subv[subv['any'] == '2024'].copy()

subv_pivot = subv_2024.pivot_table(
    index='cif',
    columns='tipus_subvencio',
    values='quantia',
    aggfunc='sum'
).reset_index()
subv_pivot.columns.name = None
subv_pivot = subv_pivot.rename(columns={
    'A_escoles_no_formals': 'subv_linia_A_2024',
    'B_conservatoris_centres_autoritzats': 'subv_linia_B_2024'
})

cols = ['subv_linia_A_2024', 'subv_linia_B_2024']
for c in cols:
    if c not in subv_pivot.columns:
        subv_pivot[c] = None

subv_pivot['subv_total_2024'] = subv_pivot['subv_linia_A_2024'].fillna(0) + \
                                 subv_pivot['subv_linia_B_2024'].fillna(0)
subv_pivot.loc[subv_pivot['subv_total_2024'] == 0, 'subv_total_2024'] = None

df = centres.merge(subv_pivot, on='cif', how='left')

n_match = df['subv_total_2024'].notna().sum()
print(f"Centres totals: {len(df)}")
print(f"Centres amb subvencio 2024: {n_match} ({n_match/len(df)*100:.1f}%)")
print(f"\nTop 10 per subvencio 2024:")
top = df[df['subv_total_2024'].notna()].nlargest(10, 'subv_total_2024')[
    ['denominacion','localidad','subv_total_2024','subv_linia_A_2024','subv_linia_B_2024']]
print(top.to_string())
print(f"\nMitjana Linia A 2024: {df['subv_linia_A_2024'].mean():,.0f} EUR")
print(f"Mitjana Linia B 2024: {df['subv_linia_B_2024'].mean():,.0f} EUR")

out = os.path.join(PROC_DIR, "centres_musicals_enriquits.csv")
df.to_csv(out, index=False, encoding="utf-8")
print(f"\nGuardat: {out}")
