from points_air.villes import Ville


def test_find_laval():
    """Trouver Repentigny sur une carte"""
    # On se trouve nulle part (sur la Rive-Nord)
    not_repentigny = Ville.from_wgs84(45.628861, -73.804224)
    assert not_repentigny is None
    # On se trouve à Repentigny
    repentigny = Ville.from_wgs84(45.768380, -73.431657)
    assert repentigny.nom == "Repentigny"
