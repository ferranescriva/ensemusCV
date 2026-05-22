#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
censo_hmd_cv.py
================
Censo de centros de la Comunitat Valenciana que ofertan la vía de
*Música y Artes Escénicas* del Batxillerat d'Arts (donde puede impartirse
"Historia de la Música y de la Danza").

Fuente autoritativa: Guía de Centros Docentes de la Conselleria, que desde
2023-24 es una SPA ("xacen-frontend") respaldada por una API JSON.

    Frontend : https://ceice.gva.es/xacen-frontend/index.html?lang=es
    API      : se descubre con DevTools (ver INSTRUCCIONES más abajo)

Estrategia (3 etapas):
  1. Consulta a la API xacen filtrando por la enseñanza de bachillerato
     "Arts: Música i Arts Escèniques" -> lista autoritativa y ACTUAL.
  2. (Opcional) Ficha por código de cada centro -> materias concretas
     (para confirmar "Historia de la Música y de la Danza") y datos de contacto.
  3. Cruce con el CSV oficial de centros (datos abiertos GVA) por código ->
     denominación normalizada, municipio, comarca, coordenadas, régimen.

Diseñado para correr de forma desatendida (cron) en un servidor de scraping.
Es idempotente (cachea respuestas) y reanudable.

------------------------------------------------------------------------------
INSTRUCCIONES PARA CAPTURAR EL ENDPOINT REAL (una sola vez, ~1 min)
------------------------------------------------------------------------------
1. Abre en Chrome:  https://ceice.gva.es/xacen-frontend/index.html?lang=es
2. F12 -> pestaña "Network" (Red) -> filtro "Fetch/XHR".
3. En la propia guía, filtra por: Enseñanza = Bachillerato ->
   Modalidad Artes -> "Música y Artes Escénicas" (o el itinerario equivalente)
   y lanza la búsqueda.
4. En Network verás la llamada de búsqueda (normalmente algo bajo
   ".../xacen/..." que devuelve JSON con la lista de centros). Haz clic en ella:
     - Copia la URL (pestaña "Headers").
     - Copia el método (GET/POST) y, si es POST, el "Request Payload".
     - Copia las cabeceras relevantes (Content-Type, y si hubiera, Authorization).
5. Repite para la llamada de FICHA: pulsa un centro y captura la llamada de
   detalle (suele incluir el código de centro en la URL o en el cuerpo).
6. Vuelca todo eso en el fichero JSON de configuración 'request_spec.json'
   (hay una plantilla de ejemplo al final de este archivo: GENERAR_PLANTILLA).

Con eso el script se adapta a la API real sin depender de suposiciones frágiles.
------------------------------------------------------------------------------
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import os
import sys
import time
from datetime import date
from pathlib import Path

import requests  # pip install requests

# --------------------------------------------------------------------------- #
# Constantes
# --------------------------------------------------------------------------- #
CSV_OFICIAL_URL = (
    "https://dadesobertes.gva.es/dataset/"
    "68eb1d94-76d3-4305-8507-e1aab7717d0e/resource/"
    "1aa53c3a-4639-41aa-ac85-d58254c428c0/download/"
    "centros-docentes-de-la-comunitat-valenciana.csv"
)
USER_AGENT = (
    "censo-hmd-cv/1.0 (investigacion academica; ensemusCV; "
    "contacto: tu-email@uv.es)"
)
TIMEOUT = 30

log = logging.getLogger("censo_hmd")


# --------------------------------------------------------------------------- #
# Utilidades de red
# --------------------------------------------------------------------------- #
def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json, */*"})
    return s


def get_with_retries(session, method, url, *, retries=4, backoff=2.0, **kw):
    """GET/POST con reintentos exponenciales. Devuelve requests.Response."""
    last = None
    for intento in range(1, retries + 1):
        try:
            r = session.request(method, url, timeout=TIMEOUT, **kw)
            if r.status_code >= 500:
                raise requests.HTTPError(f"{r.status_code} servidor")
            return r
        except (requests.RequestException,) as e:
            last = e
            espera = backoff ** intento
            log.warning("  intento %d/%d falló (%s); espero %.0fs",
                        intento, retries, e, espera)
            time.sleep(espera)
    raise RuntimeError(f"Sin éxito tras {retries} intentos: {url} ({last})")


# --------------------------------------------------------------------------- #
# Etapa 0: CSV oficial (universo / cruce)
# --------------------------------------------------------------------------- #
def descargar_csv_oficial(session, cache_dir: Path) -> dict:
    """
    Descarga (y cachea) el CSV oficial de centros y lo indexa por código.
    Devuelve {codigo: {campos...}}. Autodetecta delimitador (; o ,).
    """
    cache = cache_dir / "centros_oficial.csv"
    if cache.exists():
        raw = cache.read_text(encoding="utf-8", errors="replace")
        log.info("CSV oficial leído de caché (%s)", cache)
    else:
        log.info("Descargando CSV oficial de centros…")
        r = get_with_retries(session, "GET", CSV_OFICIAL_URL)
        r.encoding = r.apparent_encoding or "utf-8"
        raw = r.text
        cache.write_text(raw, encoding="utf-8")
        log.info("CSV oficial guardado en %s", cache)

    sample = raw[:4096]
    delim = ";" if sample.count(";") >= sample.count(",") else ","
    reader = csv.DictReader(io.StringIO(raw), delimiter=delim)

    # Localiza la columna de código de forma flexible.
    cols = [c.strip() for c in (reader.fieldnames or [])]
    col_cod = next((c for c in cols if c.lower() in
                    ("codigo", "código", "codi", "cod_centre", "codcentro")), None)
    if not col_cod:
        col_cod = next((c for c in cols if "cod" in c.lower()), cols[0] if cols else None)
    log.info("Columna de código detectada en CSV oficial: %r", col_cod)

    indexado = {}
    for fila in reader:
        cod = (fila.get(col_cod) or "").strip()
        if cod:
            indexado[cod] = {k.strip(): (v or "").strip() for k, v in fila.items()}
    log.info("CSV oficial indexado: %d centros", len(indexado))
    return indexado


# --------------------------------------------------------------------------- #
# Etapa 1: consulta a la API xacen (búsqueda por enseñanza)
# --------------------------------------------------------------------------- #
def cargar_spec(path: Path) -> dict:
    if not path.exists():
        log.error("No existe %s. Genera la plantilla con --generar-plantilla "
                  "y rellénala con la captura de DevTools.", path)
        sys.exit(2)
    return json.loads(path.read_text(encoding="utf-8"))


def consultar_busqueda(session, spec: dict, cache_dir: Path) -> list[dict]:
    """
    Ejecuta la búsqueda paginada según 'spec["busqueda"]'.
    spec["busqueda"] = {
        "method": "POST"|"GET",
        "url": "...",
        "headers": {...},
        "body": {...},                 # plantilla; usa "{page}" donde vaya la página
        "param_pagina": "page",        # nombre del campo/param de página (informativo)
        "pagina_inicial": 0,
        "tam_pagina": 50,
        "ruta_resultados": ["content"],# ruta hasta la lista de centros en el JSON
        "ruta_total_paginas": ["totalPages"]  # opcional
    }
    """
    b = spec["busqueda"]
    cache = cache_dir / "busqueda_resultados.json"
    if cache.exists():
        log.info("Resultados de búsqueda leídos de caché (%s)", cache)
        return json.loads(cache.read_text(encoding="utf-8"))

    resultados, pagina = [], b.get("pagina_inicial", 0)
    while True:
        cuerpo = json.loads(json.dumps(b.get("body", {})).replace('"{page}"', str(pagina)))
        log.info("Búsqueda · página %s", pagina)
        if b["method"].upper() == "POST":
            r = get_with_retries(session, "POST", b["url"],
                                 headers=b.get("headers"), json=cuerpo)
        else:
            params = json.loads(json.dumps(b.get("params", {})).replace("{page}", str(pagina)))
            r = get_with_retries(session, "GET", b["url"],
                                 headers=b.get("headers"), params=params)
        data = r.json()
        lote = _por_ruta(data, b.get("ruta_resultados", []))
        if not isinstance(lote, list):
            log.error("La ruta_resultados no apunta a una lista. Revisa el spec. "
                      "Volcado de claves de nivel superior: %s", list(data)[:20])
            break
        resultados.extend(lote)
        log.info("  +%d centros (acumulado %d)", len(lote), len(resultados))

        total_pag = _por_ruta(data, b.get("ruta_total_paginas", []))
        if isinstance(total_pag, int):
            if pagina >= total_pag - 1:
                break
        elif not lote:  # sin info de total: paramos cuando una página viene vacía
            break
        pagina += 1
        time.sleep(spec.get("delay", 1.0))

    cache.write_text(json.dumps(resultados, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    log.info("Búsqueda completada: %d centros (cacheado)", len(resultados))
    return resultados


def _por_ruta(obj, ruta):
    """Navega un dict/list por una lista de claves/índices. [] => el propio obj."""
    cur = obj
    for paso in ruta:
        try:
            cur = cur[paso]
        except (KeyError, IndexError, TypeError):
            return None
    return cur


# --------------------------------------------------------------------------- #
# Etapa 2: ficha por centro (opcional)
# --------------------------------------------------------------------------- #
def consultar_ficha(session, spec: dict, codigo: str, cache_dir: Path) -> dict | None:
    fdir = cache_dir / "fichas"
    fdir.mkdir(exist_ok=True)
    fcache = fdir / f"{codigo}.json"
    if fcache.exists():
        return json.loads(fcache.read_text(encoding="utf-8"))

    f = spec.get("ficha")
    if not f:
        return None
    url = f["url"].replace("{codigo}", codigo)
    if f["method"].upper() == "POST":
        cuerpo = json.loads(json.dumps(f.get("body", {})).replace("{codigo}", codigo))
        r = get_with_retries(session, "POST", url, headers=f.get("headers"), json=cuerpo)
    else:
        r = get_with_retries(session, "GET", url, headers=f.get("headers"))
    try:
        data = r.json()
    except ValueError:
        log.warning("Ficha %s no devolvió JSON", codigo)
        return None
    fcache.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    time.sleep(spec.get("delay", 1.0))
    return data


# --------------------------------------------------------------------------- #
# Extracción flexible de campos
# --------------------------------------------------------------------------- #
def _buscar_clave(d: dict, *fragmentos) -> str:
    """Devuelve el primer valor cuya clave contenga alguno de los fragmentos."""
    for k, v in d.items():
        kl = k.lower()
        if any(fr in kl for fr in fragmentos) and isinstance(v, (str, int, float)):
            return str(v).strip()
    return ""


def normaliza_centro(rec: dict) -> dict:
    """Heurística para extraer código/denominación/municipio del registro xacen."""
    return {
        "codigo": _buscar_clave(rec, "codi", "codcen", "codigo", "código"),
        "denominacion": _buscar_clave(rec, "denomin", "nombre", "nom"),
        "municipio": _buscar_clave(rec, "municipi", "localidad", "poblac"),
        "regimen": _buscar_clave(rec, "regim", "naturaleza", "titular"),
    }


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="Censo HMD Comunitat Valenciana (API xacen GVA)")
    ap.add_argument("--spec", default="request_spec.json",
                    help="Fichero con la especificación de las peticiones (DevTools)")
    ap.add_argument("--out", default=f"censo_hmd_cv_{date.today():%Y%m%d}.csv")
    ap.add_argument("--cache-dir", default=".cache_censo")
    ap.add_argument("--delay", type=float, default=1.0, help="Segundos entre peticiones")
    ap.add_argument("--limit", type=int, default=0, help="Procesar solo N centros (pruebas)")
    ap.add_argument("--no-detail", action="store_true", help="No consultar fichas")
    ap.add_argument("--generar-plantilla", action="store_true",
                    help="Escribe una plantilla request_spec.json y termina")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s",
                        datefmt="%H:%M:%S")

    if args.generar_plantilla:
        Path(args.spec).write_text(PLANTILLA_SPEC, encoding="utf-8")
        log.info("Plantilla escrita en %s. Rellénala con la captura de DevTools.", args.spec)
        return

    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(exist_ok=True)
    session = make_session()

    spec = cargar_spec(Path(args.spec))
    session.headers.update({"delay": ""})  # noop; el delay se aplica entre llamadas
    spec.setdefault("delay", args.delay)

    oficial = descargar_csv_oficial(session, cache_dir)
    crudos = consultar_busqueda(session, spec, cache_dir)
    if args.limit:
        crudos = crudos[: args.limit]

    # Vuelca el primer registro crudo para que puedas mapear campos con precisión.
    if crudos:
        (cache_dir / "muestra_registro.json").write_text(
            json.dumps(crudos[0], ensure_ascii=False, indent=2), encoding="utf-8")
        log.info("Muestra de registro crudo -> %s/muestra_registro.json", cache_dir)

    filas = []
    for i, rec in enumerate(crudos, 1):
        base = normaliza_centro(rec)
        cod = base["codigo"]
        log.info("[%d/%d] %s %s", i, len(crudos), cod, base["denominacion"])

        materias = ""
        if not args.no_detail and cod:
            ficha = consultar_ficha(session, spec, cod, cache_dir)
            if ficha:
                blob = json.dumps(ficha, ensure_ascii=False).lower()
                # marca si la ficha menciona explícitamente la materia
                if "història de la música" in blob or "historia de la música" in blob:
                    materias = "Historia de la Música y de la Danza (en ficha)"

        ofi = oficial.get(cod, {})
        filas.append({
            "codigo": cod,
            "denominacion": base["denominacion"] or _buscar_clave(ofi, "denomin", "nombre"),
            "municipio": base["municipio"] or _buscar_clave(ofi, "municipi", "localidad"),
            "comarca": _buscar_clave(ofi, "comarca"),
            "provincia": _buscar_clave(ofi, "provinci"),
            "regimen": base["regimen"] or _buscar_clave(ofi, "regim", "titular"),
            "lat": _buscar_clave(ofi, "lat", "_y"),
            "lon": _buscar_clave(ofi, "lon", "lng", "_x"),
            "materia_confirmada": materias,
            "fuente": "API xacen (Guía de Centros GVA)",
            "fecha_consulta": date.today().isoformat(),
        })

    campos = ["codigo", "denominacion", "municipio", "comarca", "provincia",
              "regimen", "lat", "lon", "materia_confirmada", "fuente", "fecha_consulta"]
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, delimiter=";")
        w.writeheader()
        w.writerows(filas)
    log.info("✔ Censo escrito: %s (%d centros)", args.out, len(filas))


# --------------------------------------------------------------------------- #
# Plantilla de especificación (rellénala con DevTools)
# --------------------------------------------------------------------------- #
PLANTILLA_SPEC = r"""{
  "_comentario": "Rellena con la captura de Network (DevTools). Ver INSTRUCCIONES en el .py",
  "delay": 1.0,

  "busqueda": {
    "method": "POST",
    "url": "https://ceice.gva.es/xacen/REEMPLAZA/buscar",
    "headers": { "Content-Type": "application/json" },
    "body": {
      "ensenanza": "BACHILLERATO",
      "modalidad": "ARTES",
      "via": "MUSICA_Y_ARTES_ESCENICAS",
      "page": "{page}",
      "size": 50
    },
    "params": {},
    "pagina_inicial": 0,
    "tam_pagina": 50,
    "ruta_resultados": ["content"],
    "ruta_total_paginas": ["totalPages"]
  },

  "ficha": {
    "method": "GET",
    "url": "https://ceice.gva.es/xacen/REEMPLAZA/centro/{codigo}",
    "headers": {}
  }
}
"""

if __name__ == "__main__":
    main()
