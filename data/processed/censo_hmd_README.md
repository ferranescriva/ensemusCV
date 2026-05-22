# Censo de centros con la vía de Música y Artes Escénicas (Batxillerat d'Arts) — Comunitat Valenciana

**Materia de interés:** *Historia de la Música y de la Danza* (materia de modalidad de 2º de
Bachillerato, vía de Música y Artes Escénicas).
**Cobertura:** Comunitat Valenciana (Alacant, Castelló, València).
**Fecha de extracción:** 2026-05-22.
**Nº de centros:** 46 (todos de titularidad pública).

## Qué contiene este conjunto

| Archivo | Descripción |
|---|---|
| `censo_hmd_cv_20260522.csv` | Censo final. Separador `;`, codificación UTF-8. Una fila por centro, con código oficial, denominación, municipio, comarca, provincia, régimen y coordenadas. |
| `censo_hmd_cv_20260522_API_raw.json` | Respuesta cruda de la API (prueba documental de la extracción). |
| `request_spec.json` | Especificación exacta de la consulta que generó el censo (endpoint y parámetros). |
| `censo_hmd_cv.py` | Script de extracción (consulta paginada + cruce con el CSV oficial de centros). |

## Fuentes

1. **Guía de Centros Docentes de la Conselleria d'Educació, Cultura i Universitats (GVA).**
   Aplicación `xacen-frontend`, respaldada por la API `xacen-backend`.
   - Endpoint de búsqueda:
     `https://xacen-backend.gva.es/xacen-backend/api/v1/guiadecentros/listaCentrosAularios`
   - Parámetros: `tipoEstudio=BACHILLERATO`, `codModalidadBach=05007701130`
     (código interno de la vía *Música y Artes Escénicas*), `nocturnoBachFP=N`, `idioma=es`.
   - La búsqueda devolvió la lista completa en una sola página (`numLlamada=0`).

2. **Centros docentes de la Comunitat Valenciana** (Portal de Dades Obertes de la GVA),
   usado para enriquecer cada centro (comarca, provincia, coordenadas) mediante cruce por
   código de centro.
   - `https://dadesobertes.gva.es/es/dataset/edu-centros`

## Campos del CSV

`codigo` · `denominacion` · `municipio` · `comarca` · `provincia` · `regimen` ·
`lat` · `lon` · `materia_confirmada` · `fuente` · `fecha_consulta`

## Notas metodológicas y advertencias

- **Ofertar la vía ≠ impartir la materia cada curso.** *Historia de la Música y de la Danza*
  es una de las cinco materias de modalidad de 2º de la vía de Música y Artes Escénicas, de las
  que el alumnado cursa dos. Es de oferta obligada en los centros públicos *siempre que haya
  disponibilidad horaria de profesorado con destino definitivo*. Por tanto, este censo identifica
  los centros donde la materia **puede** impartirse, no necesariamente donde se imparte en un
  curso concreto.
- El censo refleja la oferta vigente en la fecha de extracción. Para series temporales o
  comprobación posterior, conviene re-ejecutar la consulta y conservar el JSON crudo de cada
  extracción.
- `materia_confirmada` solo se rellena cuando se ejecuta la consulta de ficha por centro
  (no usada en esta extracción, `--no-detail`).

## Reproducción

```bash
pip install requests
python3 censo_hmd_cv.py --generar-plantilla   # crea request_spec.json (luego se rellena)
python3 censo_hmd_cv.py --no-detail           # genera el censo
```

## Cita sugerida

Escrivà-Llorca, F. (2026). *Censo de centros con la vía de Música y Artes Escénicas
(Batxillerat d'Arts) en la Comunitat Valenciana* [conjunto de datos]. Extracción de la Guía de
Centros Docentes de la Generalitat Valenciana, 22 de mayo de 2026. Proyecto ensemusCV.
