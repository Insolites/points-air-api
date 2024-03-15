import datetime
from typing import List, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .plateaux import Sport


class Utilisateur(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="Identificateur unique pour cet utilisateur",
    )
    nom: str = Field(
        description="Identificateur court pour cet utilisateur", examples=["dhdaines"]
    )
    nom_complet: Union[str, None] = Field(
        None,
        description="Nom complet de cet utilisateur",
        examples=["David Huggins-Daines"],
    )
    sports: List[Sport] = Field(
        description="Sports pratiqués par cet utilisateur",
    )
    debut: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="Date de création de l'utilisateur",
    )
    dernier: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="Date de dernière utilisation",
    )


class Activite(BaseModel):
    id: UUID = Field(
        default_factory=uuid4, description="Identificateur unique pour cette activité"
    )
    user: UUID = Field(description="Identificateur de l'utilisateur")
    sport: List[Sport] = Field(
        description="Quels sports ont été pratiqués lors de cette activité"
    )
    date: datetime.datetime = Field(
        default_factory=datetime.datetime.now, description="Date de début de l'activité"
    )
    confirme: bool = Field(False, description="L'activité est-elle confirmée?")
    plateau: UUID = Field(
        description="Identificateur du plateau d'activité où l'activité a eu lieu"
    )
