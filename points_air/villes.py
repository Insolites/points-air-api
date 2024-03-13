"""Villes de compétition et leurs emplacements."""

import shapely  # type: ignore

from pathlib import Path
from pydantic import BaseModel
from pydantic_geojson import PointModel, FeatureModel
from typing import Union


NOMS = """
Laval
Rimouski
Repentigny
Shawinigan
""".strip().split()
THISDIR = Path(__file__).parent


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
    feature: Union[FeatureModel, None]
    """Feature GeoJSON de cette ville (fort probablement une MultiPolygon)"""

    @classmethod
    def from_wgs84(self, latitude: float, longitude: float) -> Union["Ville", None]:
        p = shapely.Point(longitude, latitude)
        for v, g in {}:  # FIXME
            if g.contains(p):
                return Ville(nom=v)
        return None
