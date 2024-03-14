"""Plateaux d'activités physiques et leurs emplacements.

Ce module regroupe les fonctions pour télécharger les activités ainsi
que pour localiser les activitées à proximité d'un emplacement ou une
ville.
"""

import logging
from pathlib import Path
from typing import Dict, List, Literal, Tuple, Union
from uuid import UUID, uuid4

import pyproj
import shapely  # type: ignore
from pydantic import BaseModel, Field, RootModel
from pydantic_geojson import FeatureModel, PointModel  # type: ignore

LOGGER = logging.getLogger("points-air-plateaux")
WGS84 = pyproj.Geod(ellps="WGS84")
SHAPES: Dict[UUID, shapely.Geometry] = {}
PLATEAUX: Dict[str, List["Plateau"]]
PLATEAUX_UUID: Dict[UUID, "Plateau"]


Saison = Literal["Hiver", "TroisSaisons", "QuatreSaisons"]
Sport = Literal["Marche", "Vélo"]


class Plateau(BaseModel):
    """
    Plateau d'activité physique pour participer dans la compétition.
    """

    id: UUID = Field(
        description="Identificateur unique pour ce plateau d'activité",
        default_factory=uuid4,
    )
    nom: str = Field(
        description="Nom usuel de ce plateau", examples=["Parc de l'Île-Melville"]
    )
    ville: str = Field(
        description="Identificateur de la ville où se trouve ce plateau",
        examples=["ville-de-shawinigan"],
    )
    saison: Saison = Field(
        description="Saisons d'utilisation de ce plateau", examples=["QuatreSaisons"]
    )
    sports: List[Sport] = Field(
        description="Sports pratiqués à cet endroits", examples=[["Marche", "Vélo"]]
    )
    centroide: PointModel = Field(
        description="Centroïde géométrique de ce plateau",
        examples=[PointModel(coordinates=(-72.75478338821179, 46.53507358332476))],
    )
    feature: Union[FeatureModel, None] = Field(
        None, description="Feature GeoJSON de ce plateau"
    )

    @classmethod
    def near_wgs84(
        self, latitude: float, longitude: float, proximite: float = 10, limit: int = 10
    ) -> List[Tuple[float, "Plateau"]]:
        """Plateaux a proximité et distances"""
        # FIXME: Pourrait vraiment utiliser Spatial SQL ;-)
        ns = len(SHAPES)
        _, _, distances = WGS84.inv(
            [longitude] * ns,
            [latitude] * ns,
            [shape.centroid.x for shape in SHAPES.values()],
            [shape.centroid.y for shape in SHAPES.values()],
        )
        plateaux = list(zip(distances, SHAPES.keys()))
        plateaux.sort()
        return [
            (dist, PLATEAUX_UUID[uid])
            for dist, uid in plateaux[:limit]
            if dist < proximite * 1000
        ]


PlateauCollection = RootModel[Dict[str, List[Plateau]]]
THISDIR = Path(__file__).parent
with open(THISDIR / "plateaux.json") as infh:
    data = infh.read()
    PLATEAUX = PlateauCollection.model_validate_json(data).root
    PLATEAUX_UUID = {}
    for v in PLATEAUX.values():
        for p in v:
            if p.feature is None:
                LOGGER.warning(
                    "feature pour %s ne devrait pas être None dans plateaux.json", p.id
                )
                continue
            # FIXME: THERE MUST BE A BETTER WAY
            shape = shapely.from_geojson(p.feature.model_dump_json())
            shapely.prepare(shape)
            SHAPES[p.id] = shape
            PLATEAUX_UUID[p.id] = p
