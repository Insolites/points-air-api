import uuid
from points_air.plateaux import Plateau


def test_plateaux_wsg84():
    assert Plateau.near_wgs84(45.768380, -73.431657) is not None
    nearby = Plateau.near_wgs84(45.768380, -73.431657)
    dist, p = nearby[0]
    assert abs(dist - 164) < 1
    assert "Sanguinet" in p.nom

    nearby = Plateau.near_wgs84(45.768380, -73.431657, limit=1)
    assert len(nearby) == 1
    dist, p = nearby[0]
    assert abs(dist - 164) < 1
    assert "Sanguinet" in p.nom

    nearby = Plateau.near_wgs84(45.768380, -73.431657, proximite=0.5)
    assert len(nearby) == 1
    dist, p = nearby[0]
    assert abs(dist - 164) < 1
    assert "Sanguinet" in p.nom

    nearby = Plateau.near_wgs84(45.768380, -73.431657, proximite=1)
    assert len(nearby) == 3
    dist, p = nearby[0]
    assert abs(dist - 164) < 1
    assert "Sanguinet" in p.nom


def test_plateau_uuid():
    p = Plateau.from_uuid(uuid.UUID("17aa7a09-e295-499c-845a-41a01e061a64"))
    assert p.nom == "Parc du Bic"
