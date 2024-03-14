"""Villes de compétition et leurs emplacements."""

import logging
from pathlib import Path
from typing import Dict, Union, List

import shapely  # type: ignore
from pydantic import BaseModel, RootModel, Field
from pydantic_geojson import FeatureModel, PointModel  # type: ignore

LOGGER = logging.getLogger("points-air-villes")
SHAPES: Dict[str, shapely.Geometry] = {}
VILLES: Dict[str, "Ville"]


class Ville(BaseModel):
    """
    Une ville de compétition.
    """

    id: str = Field(
        description="Identifieur pour cette ville (nom d'organisme dans l'api DQ)",
        examples=["ville-de-repentigny"],
    )
    nom: str = Field(description="Nom usuel de cette ville", examples=["Repentigny"])
    overpass: Union[int, None] = Field(
        None,
        description="Référent Overpass pour cette ville (area)",
        examples=[3607706380],
    )
    centroide: PointModel = Field(
        description="Centroïde géométrique de cette ville",
        examples=[PointModel(coordinates=(-73.47093577802768, 45.76110925573926))],
    )
    feature: Union[FeatureModel, None] = Field(
        None,
        description="Feature GeoJSON de cette ville (fort probablement une MultiPolygon)",
    )

    @classmethod
    def from_wgs84(self, latitude: float, longitude: float) -> Union["Ville", None]:
        p = shapely.Point(longitude, latitude)
        for v, s in SHAPES.items():
            if s.contains(p):
                return VILLES[v]
        return None


class Score(BaseModel):
    ville: str = Field(
        description="Identificateur d'une ville", examples=["ville-de-repentigny"]
    )
    score: int = Field(description="Score d'activité physique", examples=[42])


Palmares = RootModel[List[Score]]

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
