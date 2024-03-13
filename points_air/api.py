import logging
from typing import Dict, List, Union

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic_geojson import PointModel  # type: ignore
from starlette.config import Config

from .especes import ESPECES, Espece, Observation
from .plateaux import Plateau
from .user import Activite
from .villes import VILLES, Score, Ville

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


@apiv1.get("/villes")
async def villes(geometry: bool = False) -> List[Ville]:
    """
    Obtenir la liste de villes de compétition.
    """
    return [
        v.model_dump(exclude=None if geometry else "geometry")
        for v in VILLES.values()
    ]


@apiv1.get("/ville/{latitude},{longitude}")
async def ville_wsg84(latitude: float, longitude: float) -> Ville:
    """
    Localiser un emplacement dans une des villes de compétition.
    """
    return Ville.from_wgs84(latitude, longitude)


@apiv1.get("/plateaux/{ville}")
async def activ_ville(ville: str) -> List[Plateau]:
    """
    Localiser des activités par ville
    """
    return Plateau.from_ville(ville)


@apiv1.get("/plateaux/{latitude},{longitude}")
async def activ_wgs84(latitude: float, longitude: float) -> List[Plateau]:
    """
    Localiser des activités par emplacement
    """
    return Plateau.near_wgs84(latitude, longitude)


@apiv1.get("/palmares")
async def palmares() -> List[Score]:
    """Obtenir les palmares des villes"""
    # TODO
    return [
        Score(ville="ville-de-rimouski", score=123),
        Score(ville="ville-de-shawinigan", score=99),
        Score(ville="ville-de-repentigny", score=49),
    ]


@apiv1.get("/contributions")
async def contributions(user: str, skip: int = 0, limit: int = 10) -> List[Activite]:
    """Obtenir les contributions d'un utilisateur"""
    # TODO
    return [
        Activite(
            id="FIXME",
            user="dhdaines",
            sport="Course",
            date="2024-03-12",
            plateau="FIXME",
        )
    ]


@apiv1.get("/observations")
async def observations() -> List[Observation]:
    """Obtenir les observations d'EEE"""
    # TODO
    return [
        Observation(
            user="dhdaines",
            date="2024-03-12",
            code_espece="RENOJ",
            emplacement=PointModel(coordinates=(45.95781529453835, -74.14215499821823)),
        )
    ]


@apiv1.get("/especes")
async def especes() -> List[Espece]:
    """Obtenir la liste d'EEE"""
    return ESPECES
