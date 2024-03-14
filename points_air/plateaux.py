"""Plateaux d'activités physiques et leurs emplacements.

Ce module regroupe les fonctions pour télécharger les activités ainsi
que pour localiser les activitées à proximité d'un emplacement ou une
ville.
"""

import logging
from typing import List, Literal, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from pydantic_geojson import PointModel, FeatureModel  # type: ignore

LOGGER = logging.getLogger("points-air-plateaux")


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
    geometrie: Union[FeatureModel, None] = Field(
        None, description="Géométrie GeoJSON de ce plateau (Point ou MultiPolygon)"
    )

    @classmethod
    def near_wgs84(self, latitude: float, longitude: float) -> List["Plateau"]:
        """ """
        # TODO
        return [
            Plateau(
                nom="Parc de l'Île-Melville",
                ville="ville-de-shawinigan",
                saison="QuatreSaisons",
                sports=["Marche", "Course"],
                centroide=PointModel(
                    coordinates=(-72.75478338821179, 46.53507358332476)
                ),
            )
        ]

    @classmethod
    def from_ville(self, ville: str) -> List["Plateau"]:
        """ """
        # TODO
        return [
            Plateau(
                nom="Parc de l'Île-Melville",
                ville="ville-de-shawinigan",
                saison="QuatreSaisons",
                sports=["Marche", "Course"],
                centroide=PointModel(
                    coordinates=(-72.75478338821179, 46.53507358332476)
                ),
            )
        ]
