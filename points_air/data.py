"""Construction des données de base pour Points-Air.
"""

import argparse
import asyncio
import json
import logging
import urllib
from pathlib import Path
from typing import Dict, Union, List

import osm2geojson  # type: ignore
import shapely  # type: ignore
from httpx import AsyncClient
from pydantic_geojson import (  # type: ignore
    FeatureCollectionModel,
    FeatureModel,
    PointModel,
)

from .plateaux import Plateau, PlateauCollection
from .villes import Ville, VilleCollection

CLIENT = AsyncClient()
LOGGER = logging.getLogger("points-air-data")
ICHERCHE = "https://geoegl.msp.gouv.qc.ca/apis/icherche"
DQURL = "https://www.donneesquebec.ca/recherche/api/3/action"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
OVERPASS = "https://overpass-api.de/api/interpreter"
THISDIR = Path(__file__).parent


async def overpass_query(query: str) -> Union[Dict, None]:
    """Lancer une requête sur Overpass"""
    r = await CLIENT.post(OVERPASS, data={"data": query})
    if r.status_code != 200:
        return None
    return r.json()


async def nominatim_query(**kwargs) -> Union[Dict, None]:
    """Lancer une requête sur Nominatim"""
    # Voudrait utiliser GeoJSON mais pydantic_geojson est inutile (ne
    # support pas properties) .. faudrait utiliser l'autre geojson_pydantic
    params = urllib.parse.urlencode({**kwargs, "format": "jsonv2"})
    url = f"{NOMINATIM}?{params}"
    r = await CLIENT.get(url, follow_redirects=True)
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


async def ville_parcs(ville: Ville) -> Union[Dict, None]:
    """Trouver le GeoJSON des parcs pour une ville."""
    result = await dq_query(
        "package_search", q=f"(organization:{ville.id} AND title:parcs)"
    )
    if result is None:
        return None
    if result["result"]["count"] == 0:
        return None
    dataset = result["result"]["results"][0]
    LOGGER.info("Parcs trouvés pour %s: %s", ville.id, dataset["title"])
    for resource in dataset["resources"]:
        if resource["format"] == "GeoJSON":
            LOGGER.info("GeoJSON trouvé pour %s: %s", dataset["title"], resource["url"])
            r = await CLIENT.get(resource["url"])
            if r.status_code != 200:
                return None
            return r.json()
    return None


async def ville_sentiers(ville: Ville) -> Union[Dict, None]:
    """Trouver le GeoJSON des sentiers pour une ville."""
    oql = f"""
[out:json][timeout:25];
area(id:{ville.overpass})->.searchArea;
(
nwr["highway"="path"](area.searchArea);
nwr["highway"="footway"][!"footway"][!"crossing"](area.searchArea);
nwr["highway"="cycleway"]["foot"="yes"](area.searchArea);
);
out geom;
"""
    data = await overpass_query(oql)
    if data is None:
        LOGGER.error("Échec de requête OverpassQL")
        return None
    return osm2geojson.json2geojson(data)


async def find_plateaux(ville: Ville) -> List[Plateau]:
    """Chercher des plateaux d'activité extérieure pour une ville."""
    with open(THISDIR / f"{ville.id}_sentiers.json", "rt") as infh:
        fc = FeatureCollectionModel.model_validate_json(infh.read())
    # NOTE: Could use geopandas
    sentiers = []
    for f in fc.features:
        shape = shapely.geometry.shape(f.geometry.model_dump())
        shapely.prepare(shape)
        sentiers.append(shape)
    LOGGER.info("%s: %d sentiers trouvés", ville.id, len(sentiers))
    with open(THISDIR / f"{ville.id}_parcs.json", "rt") as infh:
        # FIXME: Must preserve properties because pydantic_geojson
        parcs_fc = json.load(infh)
    parcs = []
    for f in parcs_fc["features"]:
        shape = shapely.geometry.shape(f["geometry"])
        shapely.prepare(shape)
        parcs.append((shape, f))
    LOGGER.info("%s: %d parcs trouvés", ville.id, len(parcs))
    # NOTE: Could use Spatial SQL
    parcs_sentiers = []
    for shape, parc in parcs:
        found = False
        for s in sentiers:
            if shape.contains(s):
                found = True
                break
        if found:
            parcs_sentiers.append((shape, parc))
    LOGGER.info("%s: %d parcs avec sentiers", ville.id, len(parcs_sentiers))
    plateaux = []
    for shape, parc in parcs_sentiers:
        props = parc["properties"]
        nom = props.get("NOM", "INCONNU")
        print(props)
        if "LONGITUDE" in props:
            centroide = (props["LONGITUDE"], props["LATITUDE"])
        else:
            centroide = (shape.centroid.x, shape.centroid.y)
        # FIXME: ça urge de remplacer pydantic_geojson qui est mauvais
        parc["geometry"] = json.loads(shapely.to_geojson(shape))
        p = Plateau(ville=ville.id,
                    nom=nom,
                    saison="QuatreSaisons",
                    sports=["Marche", "Vélo"],
                    centroide=PointModel(coordinates=centroide),
                    feature=parc)
        plateaux.append(p)
    return plateaux


async def find_ville(nom: str) -> Union[Ville, None]:
    """Obtenir informations pour une ville des API iCherche et DQ."""
    (org, overpass, feature) = await asyncio.gather(
        ville_organization(nom), ville_overpass(nom), ville_feature(nom)
    )
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
    # Obtenir GeoJSON des parcs et sentiers pour les villes pour test (temporaire)
    sentiers, parcs = await asyncio.gather(
        asyncio.gather(*(ville_sentiers(v) for v in villes.root.values())),
        asyncio.gather(*(ville_parcs(v) for v in villes.root.values())),
    )
    vp = {}
    for ville, vsentiers, vparcs in zip(villes.root.values(), sentiers, parcs):
        if ville is None:
            continue
        with open(THISDIR / f"{ville.id}_sentiers.json", "wt") as outfh:
            json.dump(vsentiers, outfh, indent=2)
        with open(THISDIR / f"{ville.id}_parcs.json", "wt") as outfh:
            json.dump(vparcs, outfh, indent=2)
        vp[ville.id] = await find_plateaux(ville)
    plateaux = PlateauCollection(vp)
    with open(THISDIR / "plateaux.json", "wt") as outfh:
        print(plateaux.model_dump_json(indent=2), file=outfh)


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
