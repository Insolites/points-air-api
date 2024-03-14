import datetime
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .plateaux import Sport


class Activite(BaseModel):
    id: UUID = Field(default_factory=uuid4, description="Identificateur unique pour cette activité")
    user: UUID = Field(description="Identificateur de l'utilisateur")
    sport: List[Sport] = Field(description="Quels sports ont été pratiqués lors de cette activité")
    date: datetime.datetime = Field(description="Date de début de l'activité")
    confirme: bool = Field(False, description="L'activité est-elle confirmée?")
    plateau: UUID = Field(description="Identificateur du plateau d'activité où l'activité a eu lieu")
