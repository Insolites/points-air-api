from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import dotenv
import logging

LOGGER = logging.getLogger("points-air-api")
dotenv.load_dotenv()
app = FastAPI()
middleware_args: dict[str, str | list[str]]
if os.getenv("DEVELOPMENT", False):
    LOGGER.info(
        "Running in development mode, will allow requests from http://localhost:*"
    )
    # Allow requests from localhost dev servers
    middleware_args = dict(
        allow_origin_regex="http://localhost(:.*)?",
    )
else:
    # Allow requests from application
    middleware_args = dict(
        allow_origins=[
            os.getenv("ORIGIN", "https://points-air.ecolingui.ca"),
        ],
    )
app.add_middleware(CORSMiddleware, allow_methods=["GET", "OPTIONS"], **middleware_args)


@app.get("/")
def home_page(request: Request):
    return "Bonjour!"
