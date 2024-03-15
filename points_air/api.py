import logging
from pathlib import Path
from typing import Annotated, Dict, List, Tuple, Union
from uuid import UUID

from fastapi import Body, FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.config import Config

from .especes import ESPECES, Espece, Observation
from .plateaux import PLATEAUX, Plateau
from .user import Activite, Utilisateur
from .villes import VILLES, Palmares, Score, Ville

# FLAT FILES ARE THE FUTURE!!!
DATADIR = Path("data")
DATADIR.mkdir(parents=True, exist_ok=True)

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
    **middleware_args,
)
apiv1 = FastAPI(title="Points-Air API")
apiv1.add_middleware(
    CORSMiddleware,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS"],
    **middleware_args,
)
app.mount("/api/v1", apiv1)


@apiv1.get("/", summary="Bonjour!")
async def home_page(request: Request) -> str:
    return "Bonjour!"


@apiv1.get("/villes", summary="Liste de villes")
async def villes(
    geometrie: Annotated[
        bool, Query(description="Retourner perimètre en GeoJSON")
    ] = False
) -> List[Ville]:
    """
    Obtenir la liste de villes de compétition.
    """
    return [
        v.model_dump(exclude=None if geometrie else "feature") for v in VILLES.values()
    ]


@apiv1.get("/ville/{latitude},{longitude}", summary="Ville par emplacement")
async def ville_wsg84(
    latitude: float,
    longitude: float,
    geometrie: Annotated[
        bool, Query(description="Retourner perimètre en GeoJSON")
    ] = False,
) -> Union[Ville, None]:
    """
    Localiser un emplacement dans une des villes de compétition.
    """
    ville = Ville.from_wgs84(latitude, longitude)
    if ville is None:
        return None
    if geometrie:
        return ville
    else:
        return ville.model_dump(exclude="feature")


@apiv1.get("/ville/{id}", summary="Ville par identificateur")
async def ville_id(id: str, geometrie: bool = False) -> Ville:
    """
    Obtenir les informations pour une ville de compétition.
    """
    return VILLES[id].model_dump(exclude=None if geometrie else "feature")


@apiv1.get("/plateaux/{latitude},{longitude}", summary="Plateaux par emplacement")
async def activ_wgs84(
    latitude: float,
    longitude: float,
    proximite: Annotated[float, Query(description="Distance maximale en km")] = 10,
    limit: Annotated[
        int, Query(description="Nombre maximal de plateaux à retourner")
    ] = 10,
    geometrie: Annotated[
        bool, Query(description="Retourner perimètre en GeoJSON")
    ] = False,
) -> List[Tuple[float, Plateau]]:
    """
    Localiser des activités par emplacement
    """
    return [
        (dist, p.model_dump(exclude=None if geometrie else "feature"))
        for dist, p in Plateau.near_wgs84(latitude, longitude, proximite, limit)
    ]


@apiv1.get("/plateaux/{ville}", summary="Plateaux par ville")
async def activ_ville(ville: str, geometrie: bool = False) -> List[Plateau]:
    """
    Localiser des activités par ville
    """
    return [
        p.model_dump(exclude=None if geometrie else "feature") for p in PLATEAUX[ville]
    ]


@apiv1.get("/palmares", summary="Palmarès des villes")
async def palmares() -> Palmares:
    """Obtenir les palmares des villes"""
    scores: Dict[str, int] = {ville: 0 for ville in VILLES}
    # FIXME: Faut clairement une vraie DB!!!
    for path in (DATADIR / "activites").iterdir():
        if path.suffix != ".json":
            continue
        with open(path, "rt") as infh:
            act = Activite.model_validate_json(infh.read())
            p = Plateau.from_uuid(act.plateau)
            if p is not None:
                scores[p.ville] += 1
    return Palmares([Score(ville=k, score=v) for k, v in scores.items()])


@apiv1.put("/activite", summary="Création/MÀJ activité")
async def put_activite(activite: Activite) -> Activite:
    """Creer ou mettre a jour une activite"""
    # FIXME: Faut clairement de l'authentification, etc!!!
    acpath = DATADIR / "activites" / f"{activite.id}.json"
    acpath.parent.mkdir(parents=True, exist_ok=True)
    with open(acpath, "wt") as outfh:
        print(activite.model_dump_json(indent=2), file=outfh)
    LOGGER.info("Creation/MAJ activité: %s dans %s", activite.id, acpath)
    return activite


@apiv1.get("/activites")
async def activites(user: UUID) -> List[Activite]:
    """Obtenir les contributions d'un utilisateur"""
    # FIXME: Faut clairement une vraie DB!!!
    acts = []
    for path in (DATADIR / "activites").iterdir():
        if path.suffix != ".json":
            continue
        with open(path, "rt") as infh:
            act = Activite.model_validate_json(infh.read())
            if act.user != user:
                continue
            acts.append(act)
    return acts


@apiv1.put("/observation", summary="Création/MÀJ observation")
async def put_observation(obs: Observation) -> Observation:
    """Creer ou mettre a jour une observation"""
    # FIXME: Faut clairement de l'authentification, etc!!!
    obpath = DATADIR / "observations" / f"{obs.id}.json"
    obpath.parent.mkdir(parents=True, exist_ok=True)
    with open(obpath, "wt") as outfh:
        print(obs.model_dump_json(indent=2), file=outfh)
    LOGGER.info("Creation/MAJ observation: %s dans %s", obs.id, obpath)
    return obs


@apiv1.get("/observations")
async def observations(user: Union[str, None] = None) -> List[Observation]:
    """Obtenir les observations d'EEE"""
    # FIXME: Faut clairement une vraie DB!!!
    obss = []
    for path in (DATADIR / "observations").iterdir():
        if path.suffix != ".json":
            continue
        with open(path, "rt") as infh:
            obs = Observation.model_validate_json(infh.read())
            if user is not None and obs.user != user:
                continue
            obss.append(obs)
    return obss


@apiv1.get("/especes")
async def especes() -> List[Espece]:
    """Obtenir la liste d'EEE"""
    return ESPECES


@apiv1.put("/user", summary="Création ou MÀJ utilisateur")
async def put_user(
    user: Annotated[
        Utilisateur,
        Body(
            example={
                "nom": "foobie",
                "nom_complet": "Foobie McBletch",
                "sports": ["Marche"],
            }
        ),
    ]
) -> Utilisateur:
    """Création d'un utilisateur"""
    # FIXME: Faut clairement de l'authentification, etc!!!
    userpath = DATADIR / "users" / f"{user.id}.json"
    userpath.parent.mkdir(parents=True, exist_ok=True)
    with open(userpath, "wt") as outfh:
        print(user.model_dump_json(indent=2), file=outfh)
    LOGGER.info("Creation/MAJ utilisateur: %s dans %s", user, userpath)
    return user


@apiv1.get("/user/{id}", summary="utilisateur par ID")
async def get_user(id: UUID) -> Union[Utilisateur, None]:
    """Recherche d'un utilisateur"""
    userpath = DATADIR / "users" / f"{id}.json"
    try:
        with open(userpath, "rt") as infh:
            return Utilisateur.model_validate_json(infh.read())
    except FileNotFoundError:
        return None
