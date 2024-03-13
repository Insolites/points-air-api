"""Plateaux d'activités physiques et leurs emplacements.

Ce module regroupe les fonctions pour télécharger les activités ainsi
que pour localiser les activitées à proximité d'un emplacement ou une
ville.
"""

import logging
from typing import List, Literal, Union

from pydantic import BaseModel
from pydantic_geojson import PointModel, FeatureModel  # type: ignore

LOGGER = logging.getLogger("points-air-plateaux")


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
    centroide: PointModel
    """Centroïde géométrique de ce plateau"""
    geometrie: Union[FeatureModel, None] = None
    """Géométrie GeoJSON de ce plateau (Point ou MultiPolygon)"""

    @classmethod
    def near_wgs84(self, latitude: float, longitude: float) -> List["Plateau"]:
        """ """
        # TODO
        return [
            Plateau(
                id="FIXME",
                nom="Parc de l'Île-Melville",
                ville="ville-de-shawinigan",
                saison="QuatreSaisons",
                sports=["Marche", "Course"],
                centroide=PointModel(coordinates=(-72.75478338821179, 46.53507358332476)),
            )
        ]

    @classmethod
    def from_ville(self, ville: str) -> List["Plateau"]:
        """ """
        # TODO
        return [
            Plateau(
                id="FIXME",
                nom="Parc de l'Île-Melville",
                ville="ville-de-shawinigan",
                saison="QuatreSaisons",
                sports=["Marche", "Course"],
                centroide=PointModel(coordinates=(-72.75478338821179, 46.53507358332476)),
            )
        ]
