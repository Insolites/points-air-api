import pytest

from points_air.villes import ville_json, Ville


@pytest.mark.anyio
async def test_laval():
    """Trouver Laval avec iCherche"""
    geom = await ville_json("Laval")
    # inutile de faire assert parce que ça va planter tout de suite si
    # ces membres sont absents!
    features = geom["features"]
    laval = features[0]
    geometry = laval["geometry"]
    assert geometry["type"] == "MultiPolygon"
    assert geometry["coordinates"]


def test_find_laval():
    """Trouver Laval sur une carte"""
    quelque_part_a_laval = [45.617610, -73.764797]
    laval = Ville.from_wgs84(*quelque_part_a_laval)
    # On se trouve bel et bien à Laval
    assert laval.nom == "Laval"
