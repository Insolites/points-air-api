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
    # On se trouve nulle part (sur la Rive-Nord)
    not_laval = Ville.from_wgs84(45.628861, -73.804224)
    assert not_laval is None
    # On se trouve à Repentigny (et pas à Laval)
    repentigny = Ville.from_wgs84(45.768380, -73.431657)
    assert repentigny.nom != "Laval"
