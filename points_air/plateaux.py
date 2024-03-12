"""Plateaux d'activités physiques et leurs emplacements.

Ce module regroupe les fonctions pour télécharger les activités ainsi
que pour localiser les activitées à proximité d'un emplacement ou une
ville.
"""

from pydantic import BaseModel
from typing import Literal, List

Saison = Literal["Hiver", "TroisSaisons", "QuatreSaisons"]


class Plateau(BaseModel):
    """
    Plateau d'activité physique pour participer dans la compétition.
    """
    nom: str
    saison: Saison

    @classmethod
    def near_wgs84(self, latitude: float, longitude: float) -> List["Plateau"]:
        """
        """
        # TODO
        return []

    @classmethod
    def from_ville(self, ville: str) -> List["Plateau"]:
        """
        """
        # TODO
        return []
