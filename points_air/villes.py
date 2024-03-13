"""Villes de compétition et leurs emplacements.

Ce module regroupe les fonctions pour télécharger les géométries des
villes, ainsi que pour localiser des emplacements à l'intérieur des villes.
"""

import argparse
import asyncio
import json
import urllib

from shapely import Point, prepare  # type: ignore
from shapely.geometry import shape  # type: ignore
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from httpx import AsyncClient

CLIENT = AsyncClient()
ICHERCHE = "https://geoegl.msp.gouv.qc.ca/apis/icherche"
VILLES = """
Laval
Rimouski
Repentigny
Shawinigan
""".strip().split()
THISDIR = Path(__file__).parent
VILLEGONS = {}
try:
    with open(THISDIR / "villes.json", "rt") as infh:
        feats = json.load(infh)
    for v, f in feats.items():
        VILLEGONS[v] = shape(f["geometry"])
        prepare(VILLEGONS[v])
except json.JSONDecodeError:  # Si on reconstruit le JSON..
    pass


class Ville(BaseModel):
    """
    Une ville de compétition.
    """

    nom: str

    @classmethod
    def from_wgs84(self, latitude: float, longitude: float) -> Optional["Ville"]:
        p = Point(longitude, latitude)
        for v, g in VILLEGONS.items():
            if g.contains(p):
                return Ville(nom=v)
        return None


async def icherche_query(action: str, **kwargs) -> Optional[dict]:
    """Lancer une requête sur iCherche"""
    params = urllib.parse.urlencode(kwargs)
    url = f"{ICHERCHE}/{action}?{params}"
    r = await CLIENT.get(url)
    if r.status_code != 200:
        return None
    return r.json()


async def async_main(args: argparse.Namespace):
    ville_dict = {}
    for v in args.villes:
        fc = await icherche_query(
            "geocode",
            type="municipalites",
            q=v,
            limit=1,
            geometry=1,
        )
        if fc is None:
            raise RuntimeError(f"Impossible de chercher {v} sur iCherche")
        ville_dict[v] = fc["features"][0]
    print(json.dumps(ville_dict, indent=2, ensure_ascii=False))


def main():
    """Télécharger GeoJSON pour toutes les villes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("villes", help="Noms des villes", nargs="*", default=VILLES)
    args = parser.parse_args()
    asyncio.run(async_main(args))
