from points_air.plateaux import Plateau


def test_plateaux_wsg84():
    assert Plateau.near_wgs84(45.768380, -73.431657) is not None
