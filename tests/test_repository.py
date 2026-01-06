from ufo_project.src.repository import SightingRepository
from ufo_project.src.models import Sighting, Location, UFOShape
from datetime import datetime, timezone

"""
testy jednostkowe - repository
============================================================================
- dodawanie obserwacji do repository
- wyszukiwanie po kształcie (indeksowanie)
- zwracanie wszystkich obserwacji
"""


def make_dummy():
    """
    helper tworzący testowe dane
    """
    loc = Location(city='A',state='S',country='PL',latitude=1.0,longitude=1.0)
    s1 = Sighting(datetime_utc=datetime.now(timezone.utc), duration_seconds=10, comments='a', location=loc, shape=UFOShape.LIGHT)
    s2 = Sighting(datetime_utc=datetime.now(timezone.utc), duration_seconds=20, comments='b', location=loc, shape=UFOShape.TRIANGLE)
    return [s1, s2]


def test_repo_basic():
    """
    test podstawowych operacji na repository
    
    sprawdza:
    - tworzenie repository z listą obserwacji
    - pobieranie wszystkich obserwacji (all())
    - filtrowanie po kształcie (by_shape())
    - poprawność indeksowania (_by_shape)
    """
    repo = SightingRepository(make_dummy())
    assert len(repo.all()) == 2
    assert len(repo.by_shape(UFOShape.LIGHT)) == 1
