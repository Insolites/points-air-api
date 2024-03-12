import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.config import Config

from .villes import Ville
from .plateaux import Plateau

LOGGER = logging.getLogger("points-air-api")
CONFIG = Config()
logging.basicConfig(level=logging.INFO)
app = FastAPI()
middleware_args: dict[str, str | list[str]]
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
async def home_page(request: Request):
    return "Bonjour!"


@apiv1.get("/ville/{latitude},{longitude}")
async def ville_wsg84(latitude: float, longitude: float):
    """
    Localiser un emplacement dans une des villes de compétition.
    """
    return Ville.from_wgs84(latitude, longitude)


@apiv1.get("/plateaux/{latitude},{longitude}")
async def activ_wgs84(latitude: float, longitude: float):
    """
    Localiser des activités par emplacement
    """
    return Plateau.near_wgs84(latitude, longitude)


@apiv1.get("/plateaux/{ville}")
async def activ_ville(ville: str):
    """
    Localiser des activités par ville
    """
    return Plateau.from_ville(ville)


@apiv1.get("/palmares")
async def palmares():
    """Obtenir les palmares des villes"""
    # TODO
    return []


@apiv1.get("/contributions")
async def contributions():
    """Obtenir les contributions d'un utilisateur"""
    # TODO
    return []


# TODO: CrUD pour activités
