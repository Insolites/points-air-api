from pydantic_geojson import FeatureCollectionModel
import asyncio
import logging
import shapely
from points_air.data import ville_parcs
from points_air.villes import VILLES


async def main():
    """Main!"""
    with open("points_air/ville-de-repentigny_sentiers.json", "rt") as infh:
        fc = FeatureCollectionModel.model_validate_json(infh.read())
    # NOTE: Could use geopandas
    sentiers = []
    for f in fc.features:
        shape = shapely.geometry.shape(f.geometry.model_dump())
        shapely.prepare(shape)
        sentiers.append(shape)
    logging.info("%d sentiers trouvés", len(sentiers))
    parcs_fc = await ville_parcs(VILLES["ville-de-repentigny"])
    parcs = []
    for f in parcs_fc["features"]:
        shape = shapely.geometry.shape(f["geometry"])
        shapely.prepare(shape)
        parcs.append((shape, f["properties"]))
    logging.info("%d parcs trouvés", len(parcs))
    # NOTE: Could use Spatial SQL
    parcs_sentiers = []
    for shape, parc in parcs:
        found = False
        for s in sentiers:
            if shape.contains(s):
                found = True
                break
        if found:
            parcs_sentiers.append(parc)
    logging.info("%d parcs avec sentiers", len(parcs_sentiers))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
