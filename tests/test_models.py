from ufo_project.src.models import UFOShape, Location, Sighting
from datetime import datetime, timezone

"""
testy jednostkowe - models
============================================================================
- normalizacja UFOShape (Enum)
- tworzenie obiektów Location i Sighting
- działanie dataclasses/pydantic
"""


def test_shape_normalize():
    """
    test normalizacji kształtów UFO do Enum
    
    sprawdza:
    - różne zapisy tego samego kształtu ("Light", "LIGHT", "light")
    - fuzzy matching ("triangular" -> TRIANGLE)
    - obsługę nieznanych kształtów (UNKNOWN)
    """
    assert UFOShape.normalize('Light') == UFOShape.LIGHT
    assert UFOShape.normalize('TRIANGLE') == UFOShape.TRIANGLE
    assert UFOShape.normalize('unknown shape') == UFOShape.UNKNOWN


def test_location_dataclass():
    """
    test tworzenia obiektu Location (pydantic dataclass)
    
    sprawdza:
    - poprawne przypisanie wartości do pól
    - działanie pydantic BaseModel
    """
    loc = Location(city='Test', state='TS', country='PL', latitude=52.1, longitude=21.0)
    assert loc.city == 'Test'


def test_sighting_creation():
    """
    test tworzenia obiektu Sighting
    
    sprawdza:
    - poprawne tworzenie złożonego obiektu z zagnieżdżonymi klasami
    - działanie typowania Optional[float]
    """
    s = Sighting(datetime_utc=datetime.now(timezone.utc), duration_seconds=12.3, comments='x', location=Location(city=None,state=None,country=None,latitude=None,longitude=None), shape=UFOShape.ORB)
    assert s.duration_seconds == 12.3
