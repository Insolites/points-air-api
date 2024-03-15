import tempfile
from pathlib import Path

import points_air.api
from fastapi.testclient import TestClient

tempdir = tempfile.TemporaryDirectory()
points_air.api.DATADIR = Path(tempdir.name)
client = TestClient(points_air.api.apiv1)


def test_hello():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Bonjour!"


def test_villes():
    response = client.get("/villes")
    assert response.status_code == 200
    villes = response.json()
    assert len(villes) > 0


def test_crud():
    response = client.get("/plateaux/45.768380,-73.431657?limite=1&proximite=1000")
    assert response.status_code == 200
    plateaux = response.json()
    assert len(plateaux) == 1
    dist, plateau = plateaux[0]
    response = client.put(
        "/user",
        json={
            "nom": "foobie",
            "nom_complet": "Foobie McBletch",
            "sports": ["Marche"],
        },
    )
    assert response.status_code == 200
    user = response.json()
    assert user["nom"] == "foobie"
    assert user["id"]
    assert user["debut"]
    assert user["dernier"]
    response = client.put(
        "/activite",
        json={"user": user["id"], "sport": ["Marche"], "plateau": plateau["id"]},
    )
    assert response.status_code == 200
    activite = response.json()
    response = client.get(f"/activites?user={user['id']}")
    assert response.status_code == 200
    activites = response.json()
    assert activites[0] == activite
    response = client.get("/palmares")
    assert response.status_code == 200
    palmares = response.json()
    assert {"ville": "ville-de-repentigny", "score": 1} in palmares
    assert {"ville": "ville-de-rimouski", "score": 0} in palmares
    assert {"ville": "ville-de-shawinigan", "score": 0} in palmares
    response = client.put(
        "/activite",
        json={"user": user["id"], "sport": ["Vélo"], "plateau": plateau["id"]},
    )
    response = client.get("/palmares")
    palmares = response.json()
    assert {"ville": "ville-de-repentigny", "score": 2} in palmares
