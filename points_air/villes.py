"""Villes de compétition et leurs emplacements."""

import logging
from pathlib import Path
from typing import Dict, Union

import shapely  # type: ignore
from pydantic import BaseModel, RootModel
from pydantic_geojson import FeatureModel, PointModel  # type: ignore

LOGGER = logging.getLogger("points-air-villes")
SHAPES: Dict[str, shapely.Geometry] = {}
VILLES: Dict[str, "Ville"]


class Ville(BaseModel):
    """
    Une ville de compétition.
    """

    id: str
    """Identifieur pour cette ville (nom d'organisme dans l'api DQ)"""
    nom: str
    """Nom usuel de cette ville"""
    centroide: PointModel
    """Centroïde géométrique de cette ville"""
    feature: Union[FeatureModel, None] = None
    """Feature GeoJSON de cette ville (fort probablement une MultiPolygon)"""

    @classmethod
    def from_wgs84(self, latitude: float, longitude: float) -> Union["Ville", None]:
        p = shapely.Point(longitude, latitude)
        for v, s in SHAPES.items():
            if s.contains(p):
                return VILLES[v]
        return None


class Score(BaseModel):
    ville: str
    """Identificateur d'une ville"""
    score: int
    """Score d'activité physique"""


THISDIR = Path(__file__).parent
VilleCollection = RootModel[Dict[str, Ville]]
with open(THISDIR / "villes.json") as infh:
    data = infh.read()
    VILLES = VilleCollection.model_validate_json(data).root
    for v in VILLES.values():
        if v.feature is None:
            LOGGER.warning(
                "feature pour %s ne devrait pas être None dans villes.json", v.id
            )
            continue
        # FIXME: THERE MUST BE A BETTER WAY
        shape = shapely.from_geojson(v.feature.model_dump_json())
        shapely.prepare(shape)
        SHAPES[v.id] = shape
