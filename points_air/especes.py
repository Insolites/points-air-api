import csv
import datetime
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel
from pydantic_geojson import PointModel  # type: ignore

THISDIR = Path(__file__).parent
CATEGORIES = {
    "Insectes",
    "Oiseaux et mammifères",
    "Plantes de milieux terrestres",
    "Plantes émergentes",
}


class Observation(BaseModel):
    user: UUID
    date: datetime.datetime
    code_espece: str
    emplacement: PointModel


class Espece(BaseModel):
    """Espèce Exotique Envahissante"""
    regne: str
    categorie: str
    code_espece: str
    nom_francais: str
    nom_latin: str
    nom_anglais: str


ESPECES = []
with open(THISDIR / "sentinelle_liste_sp.csv", "rt") as infh:
    rows = (r for r in csv.DictReader(infh) if r["Categorie"] in CATEGORIES)
    for row in rows:
        ESPECES.append(Espece(**{k.lower(): v for k, v in row.items()}))
