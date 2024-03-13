import datetime
import logging
from typing import Dict, List, Tuple, Union

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.config import Config

from .plateaux import Plateau, Sport
from .villes import Ville

LOGGER = logging.getLogger("points-air-api")
CONFIG = Config()
logging.basicConfig(level=logging.INFO)
app = FastAPI()
middleware_args: Dict[str, Union[str, List[str]]]
if CONFIG("DEVELOPMENT", default=False):
    LOGGER.info("En mode développement, requêtes seront acceptés de http://localhost:*")
    middleware_args = dict(
        allow_origin_regex="http://localhost(:.*)?",
    )
else:
    origins = CONFIG(
        "ORIGIN", default="https://points-air.ecolingui.ca https://insolites.github.io"
    ).split()
    LOGGER.info("Requêtes seront acceptés de: %s", origins)
    middleware_args = dict(allow_origins=origins)
app.add_middleware(
    CORSMiddleware,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS"],
    **middleware_args
)
apiv1 = FastAPI()
app.mount("/api/v1", apiv1)


@apiv1.get("/")
async def home_page(request: Request) -> str:
    return "Bonjour!"


@apiv1.get("/ville/{latitude},{longitude}")
async def ville_wsg84(latitude: float, longitude: float) -> Ville:
    """
    Localiser un emplacement dans une des villes de compétition.
    """
    return Ville.from_wgs84(latitude, longitude)


@apiv1.get("/plateaux/{latitude},{longitude}")
async def activ_wgs84(latitude: float, longitude: float) -> List[Plateau]:
    """
    Localiser des activités par emplacement
    """
    return Plateau.near_wgs84(latitude, longitude)


@apiv1.get("/plateaux/{ville}")
async def activ_ville(ville: str) -> List[Plateau]:
    """
    Localiser des activités par ville
    """
    return Plateau.from_ville(ville)


class Score(BaseModel):
    ville: str
    score: int


@apiv1.get("/palmares")
async def palmares() -> List[Score]:
    """Obtenir les palmares des villes"""
    # TODO
    return [
        Score(ville="Rimouski", score=123),
        Score(ville="Shawinigan", score=99),
        Score(ville="Repentigny", score=49),
        Score(ville="Laval", score=33),
    ]


class Activite(BaseModel):
    user: str
    sport: Sport
    date: datetime.datetime


@apiv1.get("/contributions")
async def contributions(user: str, skip: int = 0, limit: int = 10) -> List[Activite]:
    """Obtenir les contributions d'un utilisateur"""
    # TODO
    return [Activite(user="dhdaines", sport="Course", date="2024-03-12")]


class Observation(BaseModel):
    user: str
    date: datetime.datetime
    code_espece: str
    # FIXME: Utiliser les modeles pydantic_geojson
    location: Tuple[float, float]


@apiv1.get("/observations")
async def observations() -> List[Observation]:
    """Obtenir les observations d'EEE"""
    # TODO
    return [
        Observation(
            user="dhdaines",
            date="2024-03-12",
            code_espece="RENOJ",
            location=(45.95781529453835, -74.14215499821823),
        )
    ]
