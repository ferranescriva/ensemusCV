import pandas as pd, os, unicodedata

def norm(s):
    if not isinstance(s, str): return ''
    return ''.join(c for c in unicodedata.normalize('NFD', s.upper())
                   if unicodedata.category(c) != 'Mn')

PROC = os.path.expanduser("~/ensemusCV/data/processed")
df = pd.read_csv(os.path.join(PROC, "centres_musicals_enriquits.csv"))

reglats = df[df['denominacion_generica_es'].apply(
    lambda x: any(k in norm(str(x)) for k in
    ['CONSERVATORIO','CONSERVATORI','AUTORIZADO','AUTORITZAT','INTEGRADO','INTEGRAT'])
)]

comarques_amb = set(reglats['comarca'].dropna().unique())
all_comarques = set(df['comarca'].dropna().unique())
sense_reglats = all_comarques - comarques_amb

print("=== COMARQUES AMB CENTRES REGLATS ===")
for c in sorted(comarques_amb):
    n = len(reglats[reglats['comarca']==c])
    print("  " + c + ": " + str(n))

print()
print("=== COMARQUES AMB ESCOLES PERO SENSE CENTRES REGLATS ===")
for c in sorted(sense_reglats):
    n = len(df[df['comarca']==c])
    print("  " + c + ": " + str(n) + " escoles no formals")