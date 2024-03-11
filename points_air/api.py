import logging
import os
from contextlib import asynccontextmanager

import dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

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
def home_page(request: Request):
    return "Bonjour!"
