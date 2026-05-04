import pandas as pd
import os

BASE_DIR = os.path.expanduser("~/ensemusCV")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")

df = pd.read_csv(os.path.join(PROC_DIR, "centres_musicals_enriquits.csv"))
df['cif'] = df['cif'].astype(str).str.strip()
df['centre_integrat'] = False
df['nota_relacio'] = ''

NOTES = {
    'B96641865': {
        'nota': 'Complex educatiu privat Mas Camarena Arts. Elemental a Betera (seu fiscal, Urb. Mas Camarena C/n1 s/n), Professional a Paterna (Parc Tecnologic, C/ Charles Robert Darwin 6). Dos registres administratius per nivell educatiu en seus fisiques diferenciades pero mateixa titularitat.',
        'integrat': True,
        'marcador_principal': 'BÉTERA',
    },
    'G03165875': {
        'nota': 'Societat Musical La Paz de Sant Joan d Alacant. Mateixa entitat gestora: escola privada de musica (no formal, Linia A) i centre autoritzat professional (reglat, Linia B). Comparteixen instal·lacions i professorat.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G09689241': {
        'nota': 'Asociacion Cultural Juan Sebastian Bach de Sagunt. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G12039145': {
        'nota': 'Union Musical Santa Cecilia d Onda. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G12097028': {
        'nota': 'Centro de Estudios y Actividades Musicales Maestro Goterris de Vila-real. Escola privada de musica i dansa (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G46001947': {
        'nota': 'Societat Coral El Micalet de Valencia. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G46065678': {
        'nota': 'Sociedad Artistico-Musical de Benifaio. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G46084679': {
        'nota': 'Union Musical de Benaguasil. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G46086401': {
        'nota': 'Ateneu Musical de Cullera. Escola privada de musica (Linia A) i centre autoritzat elemental (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G46094736': {
        'nota': 'Sociedad Musical d Alzira. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G46150793': {
        'nota': 'Sociedad Musical Santa Cecilia de Cullera. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G46172664': {
        'nota': 'Unio Artistico Musical Sant Francesc de Borja de Gandia. Escola privada de musica (Linia A), centre autoritzat elemental i centre autoritzat professional (Linia B). Tots els nivells educatius sota una mateixa entitat.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G46173746': {
        'nota': 'Societat Artistica Musical d Alginet. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G46192654': {
        'nota': 'Societat Instructiva Unio Musical de Tavernes de la Valldigna. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G46274056': {
        'nota': 'Unio Musical d Alaquas. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G53300935': {
        'nota': 'Joventuts Musicals del Comtat (Muro de Alcoy). Dos registres d escola privada de musica amb noms diferenciats (Escola Tradicional La Xafiaga i Escola Comarcal del Comtat) sota la mateixa entitat gestora.',
        'integrat': False,
        'marcador_principal': None,
    },
    'G96164579': {
        'nota': 'Joventuts Musicals de la Vall d Albaida. Xarxa territorial: seus a Ontinyent, Rotova i Otos. Tres centres fisics diferenciats sota la mateixa entitat gestora.',
        'integrat': False,
        'marcador_principal': None,
    },
    'G96330444': {
        'nota': 'Associacio Musical Jove de Valencia (Taller de Musica Jove). Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G96343223': {
        'nota': 'Escola de Musica Districte Maritim Grau de Gandia. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G96365994': {
        'nota': 'Societat Instructiva Unio Musical de Montserrat. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G97289672': {
        'nota': 'Union Musical de Mislata (Liceu de Musica Ciutat de Mislata). Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'G98763964': {
        'nota': 'Asociacion Musical Montealegre de l Eliana. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'P0304000C': {
        'nota': 'Ajuntament de Benimeli. Escola de Musica Municipal Pascual Rubert i Conservatori Elemental Vicente Perello. Dos registres administratius per a dos nivells educatius. Comparteixen instal·lacions, professorat i titularitat municipal.',
        'integrat': True,
        'marcador_principal': None,
    },
    'P0310100C': {
        'nota': 'Ajuntament de Pedreguer. Escola de Musica Municipal i Conservatori Elemental. Dos registres administratius per a dos nivells educatius. Comparteixen instal·lacions, professorat i titularitat municipal.',
        'integrat': True,
        'marcador_principal': None,
    },
    'Q1200347A': {
        'nota': 'Centre Municipal de les Arts Rafael Marti de Viciana de Borriana. Conservatori Elemental Abel Mus i Escola Municipal de Musica Pascual Rubert. Organisme autonom local que gestiona ambdos centres. Mes de 1.200 alumnes i 33 professors.',
        'integrat': True,
        'marcador_principal': None,
    },
    'R2802525B': {
        'nota': 'Fundacion Educativa Franciscanas de la Inmaculada de Valencia. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'R4600418J': {
        'nota': 'Casa Comunidad Escolapia Landriani de Castello de la Plana. Escola privada de musica i dansa (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'R4600429G': {
        'nota': 'HH. de la Caridad de Santa Ana de Valencia. Escola privada de musica (Linia A) i centre autoritzat professional (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'V46065298': {
        'nota': 'Centro Artistico Musical de Moncada. Escola privada de musica (Linia A) i centre autoritzat elemental (Linia B). Una sola seu fisica.',
        'integrat': True,
        'marcador_principal': None,
    },
    'V96798533': {
        'nota': 'Asociacion Musical Centro Alsina de Valencia. Centre elemental: C/ Doctor Sanchis Sivera 23 (46008). Centre professional: C/ Gregorio Gea 21 (46009). Dos registres administratius per a dos nivells en seus fisiques diferenciades en barris distints de Valencia.',
        'integrat': False,
        'marcador_principal': None,
    },
}

for cif, info in NOTES.items():
    mask = df['cif'] == cif
    df.loc[mask, 'nota_relacio'] = info['nota']
    df.loc[mask, 'centre_integrat'] = info['integrat']

print("Resum anotacions:")
print(f"  Centres integrats (vora negra al mapa): {df['centre_integrat'].sum()}")
print(f"  Centres amb nota de relacio: {(df['nota_relacio'] != '').sum()}")
print(f"\nDistribucio centre_integrat per tipologia:")
print(df[df['centre_integrat']][
    'denominacion_generica_es'].value_counts().to_string())

out = os.path.join(PROC_DIR, "centres_musicals_enriquits.csv")
df.to_csv(out, index=False, encoding="utf-8")
print(f"\nGuardat: {out}")