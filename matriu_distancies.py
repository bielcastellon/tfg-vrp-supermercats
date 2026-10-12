"""
Fase 2 - tasca 2.3: Matriu de distàncies i temps (24x24)
Crida l'endpoint Matrix d'OpenRouteService amb les 24 ubicacions
(23 botigues + magatzem) i desa dues matrius: distància (km) i temps (min).

Requereix la variable d'entorn ORS_API_KEY amb la teva clau gratuïta
(https://openrouteservice.org/dev/#/signup -> Token -> pla gratuït).

Us:
    export ORS_API_KEY="la_teva_clau_aqui"
    python3 matriu_distancies.py
"""
import csv
import os
import sys
import json
import requests

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "supermercats.csv")
OUT_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "matriu_distancies_km.csv")
OUT_TIME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "matriu_temps_min.csv")

ORS_URL = "https://api.heigit.org/openrouteservice/v2/matrix/driving-hgv"  # nou domini: cal el segment "openrouteservice/" al path


def carregar_ubicacions():
    with open(SRC, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    noms, coords = [], []
    for row in rows:
        if not row.get("lat") or not row.get("lon"):
            sys.exit(f"ERROR: falta lat/lon per a '{row['nom']}'. Geocodifica-ho abans.")
        noms.append(row["nom"])
        # ORS vol l'ordre [longitud, latitud]
        coords.append([float(row["lon"]), float(row["lat"])])
    return noms, coords


def demana_matriu(coords, api_key):
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json; charset=utf-8",
    }
    body = {
        "locations": coords,
        "metrics": ["distance", "duration"],
        "units": "km",
    }
    resp = requests.post(ORS_URL, headers=headers, json=body, timeout=60)
    if resp.status_code != 200:
        sys.exit(
            f"ERROR {resp.status_code} cridant ORS:\n{resp.text}\n\n"
            "Comprova que la clau és correcta i que no has superat el límit diari (2.000 peticions)."
        )
    return resp.json()


def desa_matriu(noms, matriu, path, decimals=3):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([""] + noms)
        for nom_fila, fila in zip(noms, matriu):
            writer.writerow([nom_fila] + [round(v, decimals) if v is not None else "" for v in fila])


def main():
    api_key = os.environ.get("ORS_API_KEY")
    if not api_key:
        sys.exit(
            "ERROR: no trobo la variable d'entorn ORS_API_KEY.\n"
            "Fes: export ORS_API_KEY=\"la_teva_clau\"   (i torna a executar l'script)"
        )

    noms, coords = carregar_ubicacions()
    print(f"Carregades {len(noms)} ubicacions (23 botigues + magatzem). Cridant l'API d'ORS...")

    dades = demana_matriu(coords, api_key)

    distancies = dades["distances"]  # km (per 'units': 'km')
    durades_s = dades["durations"]   # segons
    durades_min = [[v / 60 if v is not None else None for v in fila] for fila in durades_s]

    desa_matriu(noms, distancies, OUT_DIST, decimals=3)
    desa_matriu(noms, durades_min, OUT_TIME, decimals=2)

    print(f"Matriu de distàncies (km) desada a: {OUT_DIST}")
    print(f"Matriu de temps (min) desada a: {OUT_TIME}")
    print("\nFase 2 - tasca 2.3 feta. Següent: criteri de demanda ja fet (2.4) -> Fase 3 (formulació CVRP).")


if __name__ == "__main__":
    main()
