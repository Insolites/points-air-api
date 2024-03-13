import datetime
from typing import List

from pydantic import BaseModel

from .plateaux import Sport


class Activite(BaseModel):
    id: str
    """Identificateur unique pour cette activité"""
    user: str
    """Identificateur de l'utilisateur"""
    sport: List[Sport]
    """Quels sports ont été pratiqués lors de cette activité"""
    date: datetime.datetime
    """Date de début de l'activité"""
    confirme: bool = False
    """L'activité est-elle confirmée?"""
    plateau: str
    """Identificateur du plateau d'activité où l'activité a eu lieu"""
