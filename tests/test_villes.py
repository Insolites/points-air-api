import pytest

from points_air.villes import ville_json


@pytest.mark.anyio
async def test_laval():
    """Trouver Laval sur une carte"""
    geom = await ville_json("Laval")
    # inutile de faire assert parce que ça va planter tout de suite si
    # ces membres sont absents!
    features = geom["features"]
    laval = features[0]
    geometry = laval["geometry"]
    assert geometry["type"] == "MultiPolygon"
    assert geometry["coordinates"]
