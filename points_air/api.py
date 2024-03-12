import logging
import os
from contextlib import asynccontextmanager

import dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .villes import Ville
from .plateaux import Plateau

LOGGER = logging.getLogger("points-air-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    dotenv.load_dotenv()
    logging.basicConfig(level=logging.INFO)
    yield


app = FastAPI(lifespan=lifespan)
middleware_args: dict[str, str | list[str]]
if os.getenv("DEVELOPMENT", False):
    LOGGER.info("En mode développement, requêtes seront acceptés de http://localhost:*")
    middleware_args = dict(
        allow_origin_regex="http://localhost(:.*)?",
    )
else:
    origin = os.getenv("ORIGIN", "https://points-air.ecolingui.ca")
    LOGGER.info("Requêtes seront acceptés de %s", origin)
    middleware_args = dict(
        allow_origins=[origin],
    )
app.add_middleware(CORSMiddleware, allow_methods=["GET", "OPTIONS"], **middleware_args)


@app.get("/")
async def home_page(request: Request):
    return "Bonjour!"


@app.get("/ville/{latitude},{longitude}")
async def ville_wsg84(latitude: float, longitude: float):
    """
    Localiser un emplacement dans une des villes de compétition.
    """
    return Ville.from_wgs84(latitude, longitude)


@app.get("/plateaux/{latitude},{longitude}")
async def activ_wgs84(latitude: float, longitude: float):
    """
    Localiser des activités par emplacement
    """
    return Plateau.near_wgs84(latitude, longitude)


@app.get("/plateaux/{ville}")
async def activ_ville(ville: str):
    """
    Localiser des activités par ville
    """
    return Plateau.from_ville(ville)


@app.get("/palmares")
async def palmares():
    """Obtenir les palmares des villes"""
    # TODO
    return []


@app.get("/contributions")
async def contributions():
    """Obtenir les contributions d'un utilisateur"""
    # TODO
    return []


# TODO: CrUD pour activités
