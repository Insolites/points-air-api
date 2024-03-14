"""Construction des données de base pour Points-Air.
"""

import argparse
import asyncio
import logging
import urllib
from pathlib import Path
from typing import Dict, Union

import shapely  # type: ignore
from httpx import AsyncClient
from pydantic_geojson import (  # type: ignore
    FeatureCollectionModel,
    FeatureModel,
    PointModel,
)

from .plateaux import Plateau
from .villes import Ville, VilleCollection

CLIENT = AsyncClient(follow_redirects=True)
LOGGER = logging.getLogger("points-air-data")
ICHERCHE = "https://geoegl.msp.gouv.qc.ca/apis/icherche"
DQURL = "https://www.donneesquebec.ca/recherche/api/3/action"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
THISDIR = Path(__file__).parent


async def nominatim_query(**kwargs) -> Union[Dict, None]:
    """Lancer une requête sur Nominatim"""
    # Voudrait utiliser GeoJSON mais pydantic_geojson est inutile (ne
    # support pas properties) .. faudrait utiliser l'autre geojson_pydantic
    params = urllib.parse.urlencode({**kwargs, "format": "jsonv2"})
    url = f"{NOMINATIM}?{params}"
    r = await CLIENT.get(url)
    if r.status_code != 200:
        return None
    return r.json()


async def icherche_query(action: str, **kwargs) -> Union[FeatureCollectionModel, None]:
    """Lancer une requête sur iCherche"""
    params = urllib.parse.urlencode(kwargs)
    url = f"{ICHERCHE}/{action}?{params}"
    r = await CLIENT.get(url)
    if r.status_code != 200:
        return None
    return FeatureCollectionModel.model_validate_json(r.text)


async def dq_query(action: str, **kwargs) -> Union[Dict, None]:
    """Lancer une requête sur Données Québec"""
    params = urllib.parse.urlencode(kwargs)
    url = f"{DQURL}/{action}?{params}"
    r = await CLIENT.get(url)
    if r.status_code != 200:
        return None
    return r.json()


async def ville_overpass(ville: str) -> Union[int, None]:
    """Obtenir la region Overpass pour une ville"""
    data = await nominatim_query(city=ville, countrycodes="ca")
    if data is None or len(data) == 0:
        return None
    osm_id = data[0]["osm_id"]
    osm_type = data[0]["osm_type"]
    LOGGER.info("OSM %s %d trouvée pour %s", osm_type, osm_id, ville)
    # Don't care about the rest, iCherche est meilleur
    if osm_type == "relation":
        return osm_id + 3600000000
    elif osm_type == "way":  # FIXME: probablement ne fonctionne pas!
        return osm_id + 2400000000
    else:
        LOGGER.error("OSM type %s inconnu", osm_type)
        return None


async def ville_feature(ville: str) -> Union[FeatureModel, None]:
    """Obtenir le contour d'une ville en GeoJSON"""
    fc = await icherche_query(
        "geocode",
        type="municipalites",
        q=ville,
        limit=1,
        geometry=1,
    )
    if fc is None or len(fc.features) == 0:
        return None
    LOGGER.info("%s trouvée pour %s", fc.features[0].geometry.type, ville)
    return fc.features[0]


async def ville_organization(ville: str) -> Union[Dict, None]:
    """Trouver le nom d'organisme pour une ville"""
    villes = await dq_query("organization_autocomplete", q=ville)
    if villes is None:
        return None
    for org in villes["result"]:
        if "ville" in org["name"]:
            return org
        elif "municipal" in org["name"]:
            return org
    return villes["result"][0]


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


async def find_plateaux(ville: str):
    """Chercher des plateaux d'activité extérieure pour une ville."""
    parcs = await ville_parcs(ville)
    if parcs is None:
        LOGGER.warning("Aucun données de parcs trouvé pour %s", ville)


async def find_ville(nom: str) -> Union[Ville, None]:
    """Obtenir informations pour une ville des API iCherche et DQ."""
    (org, overpass, feature) = await asyncio.gather(ville_organization(nom), ville_overpass(nom), ville_feature(nom))
    if org is None:
        LOGGER.error("Aucun organisme trouvé pour %s", nom)
        return None
    if feature is None:
        LOGGER.error("Aucune géométrie trouvé pour %s", nom)
        return None
    LOGGER.info("Ville trouvée pour %s: %s", nom, org["name"])
    shape = shapely.geometry.shape(feature.geometry.model_dump())
    LOGGER.info("Centroïde de %s: %s", nom, shape.centroid)
    return Ville(
        id=org["name"],
        nom=nom,
        overpass=overpass,
        # FIXME: THERE MUST BE A BETTER WAY!
        centroide=PointModel.model_validate_json(shapely.to_geojson(shape.centroid)),
        feature=feature,
    )


async def async_main(args: argparse.Namespace):
    """Fonction principale async."""
    v = await asyncio.gather(*(find_ville(nom) for nom in args.villes))
    villes = VilleCollection({ville.id: ville for ville in v if ville is not None})
    with open(THISDIR / "villes.json", "wt") as outfh:
        print(villes.model_dump_json(indent=2), file=outfh)


def main():
    """Télécharger GeoJSON pour toutes les villes."""
    with open(THISDIR / "villes.txt") as infh:
        villes = [spam.strip() for spam in infh]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("villes", help="Noms des villes", nargs="*", default=villes)
    parser.add_argument(
        "-v", "--verbose", help="Informations verboses pour debug", action="store_true"
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
