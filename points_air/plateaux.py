"""Plateaux d'activités physiques et leurs emplacements.

Ce module regroupe les fonctions pour télécharger les activités ainsi
que pour localiser les activitées à proximité d'un emplacement ou une
ville.
"""

import argparse
import asyncio
import json
import logging
import urllib
from typing import Dict, List, Literal, Union

from pydantic import BaseModel
from pydantic_geojson import Point, Feature

from .villes import CLIENT, THISDIR, VILLES

LOGGER = logging.getLogger("points-air-plateaux")
DQURL = "https://www.donneesquebec.ca/recherche/api/3/action"
try:
    with open(THISDIR / "plateaux.json", "rt") as infh:
        PLATEAUX = json.load(infh)
except json.JSONDecodeError:  # Si on reconstruit le JSON..
    PLATEAUX = {}


Saison = Literal["Hiver", "TroisSaisons", "QuatreSaisons"]
Sport = Literal["Marche", "Course", "Vélo"]


class Plateau(BaseModel):
    """
    Plateau d'activité physique pour participer dans la compétition.
    """

    id: str
    """Identificateur unique pour ce plateau d'activité"""
    nom: str
    """Nom usuel de ce plateau"""
    ville: str
    """Identificateur de la ville où se trouve ce plateau"""
    saison: Saison
    """Saisons d'utilisation de ce plateau"""
    sports: List[Sport]
    """Sports pratiqués à cet endroits"""
    centroide: Point
    """Centroïde géométrique de ce plateau"""
    geometrie: Union[Feature, None]
    """Géométrie GeoJSON de ce plateau (Point ou MultiPolygon)"""

    @classmethod
    def near_wgs84(self, latitude: float, longitude: float) -> List["Plateau"]:
        """ """
        # TODO
        return [
            Plateau(
                nom="Parc de l'Île-Melville",
                ville="Shawinigan",
                saison="QuatreSaisons",
                sports=["Marche", "Course"],
                emplacement=(46.53507358332476, -72.75478338821179),
            )
        ]

    @classmethod
    def from_ville(self, ville: str) -> List["Plateau"]:
        """ """
        # TODO
        return [
            Plateau(
                nom="Parc de l'Île-Melville",
                ville="Shawinigan",
                saison="QuatreSaisons",
                sports=["Marche", "Course"],
                emplacement=(46.53507358332476, -72.75478338821179),
            )
        ]


async def dq_query(action: str, **kwargs) -> Union[Dict, None]:
    """Lancer une requête sur Données Québec"""
    params = urllib.parse.urlencode(kwargs)
    url = f"{DQURL}/{action}?{params}"
    r = await CLIENT.get(url)
    if r.status_code != 200:
        return None
    return r.json()


async def ville_organization(ville: str) -> Union[str, None]:
    """Trouver le nom d'organisme pour une ville"""
    villes = await dq_query("organization_autocomplete", q=ville)
    if villes is None:
        return None
    for org in villes["result"]:
        if "ville" in org["name"]:
            return org["name"]
        elif "municipal" in org["name"]:
            return org["name"]
    return villes["result"][0]["name"]


async def ville_parcs(org: str) -> Union[str, None]:
    """Trouver le GeoJSON des parcs pour une ville."""
    result = await dq_query("package_search", q=f"(organization:{org} AND title:parcs)")
    if result is None:
        return None
    if result["result"]["count"] == 0:
        return None
    dataset = result["result"]["results"][0]
    LOGGER.info("Parcs trouvés pour %s: %s", org, dataset["title"])
    for resource in dataset["resources"]:
        if resource["format"] == "GeoJSON":
            LOGGER.info("GeoJSON trouvé pour %s: %s", dataset["title"], resource["url"])
            return resource["url"]
    return None


async def async_main(args: argparse.Namespace):
    """fonction principale async"""
    for v in args.villes:
        org = await ville_organization(v)
        if org is None:
            LOGGER.error("Aucun organisme trouvé pour %s", v)
            continue
        LOGGER.info("Ville trouvée pour %s: %s", v, org)
        parcs = await ville_parcs(org)
        if parcs is None:
            LOGGER.warning("Aucun données de parcs trouvé pour %s", org)
            continue


def main():
    """Créer les jeux de données pour les plateaux d'activité."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("villes", help="Noms des villes", nargs="*", default=VILLES)
    args = parser.parse_args()
    asyncio.run(async_main(args))
