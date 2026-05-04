import pandas as pd
import os

PROC_DIR = os.path.expanduser("~/ensemusCV/data/processed")

df_a = pd.read_csv(os.path.join(PROC_DIR, "proxy_subvencions.csv"))
df_a['tipus_subvencio'] = 'A_escoles_no_formals'
df_a['any'] = df_a['any'].astype(str)

df_b = pd.read_csv(os.path.join(PROC_DIR, "proxy_subvencions_conservatoris.csv"))
df_b['any'] = df_b['any'].astype(str)

df = pd.concat([df_a, df_b], ignore_index=True)

print(f"Total registres combinats: {len(df)}")
print(f"\nPer tipus:")
print(df.groupby('tipus_subvencio')['quantia'].agg(['count','sum']).rename(
    columns={'count':'N','sum':'Total EUR'}).to_string())
print(f"\nPer any:")
print(df.groupby('any')['quantia'].agg(['count','sum']).rename(
    columns={'count':'N','sum':'Total EUR'}).to_string())
print(f"\nCIFs únics totals: {df['cif'].nunique()}")

out = os.path.join(PROC_DIR, "proxy_subvencions_complet.csv")
df.to_csv(out, index=False, encoding="utf-8")
print(f"\nGuardat: {out}")