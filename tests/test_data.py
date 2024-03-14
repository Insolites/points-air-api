import pytest

from points_air.villes import VILLES
from points_air.data import ville_sentiers


@pytest.mark.skip("Tests sur API externe désactivés")
@pytest.mark.anyio
async def test_sentiers():
    """Trouver des sentiers à Repentigny"""
    repentigny = VILLES["ville-de-repentigny"]
    geom = await ville_sentiers(repentigny)
    assert geom
    assert len(geom.features) > 400
