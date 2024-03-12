"""Villes de compétition et leurs emplacements.

Ce module regroupe les fonctions pour télécharger les géométries des
villes, ainsi que pour localiser des emplacements à l'intérieur des villes.
"""

import urllib

from pydantic import BaseModel
from typing import Optional
from httpx import AsyncClient

CLIENT = AsyncClient()


def icherche_url(ville: str) -> str:
    """Construire le URL pour chercher une ville dans iCherche"""
    params = urllib.parse.urlencode(
        {
            "type": "municipalites",
            "q": ville,
            "limit": 1,
            "geometry": 1,
        }
    )
    return f"https://geoegl.msp.gouv.qc.ca/apis/icherche/geocode?{params}"


async def ville_json(name: str) -> Optional[dict]:
    url = icherche_url(name)
    r = await CLIENT.get(url)
    if r.status_code != 200:
        return None
    return r.json()


class Ville(BaseModel):
    """
    Une ville de compétition.
    """
    @classmethod
    def from_wgs84(self, latitude: float, longitude: float) -> "Ville":
        # TODO
        return Ville()
