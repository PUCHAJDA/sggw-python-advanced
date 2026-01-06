import pytest
from ufo_project.src.models import Location, Sighting, UFOShape
from datetime import datetime, timezone

"""
testy jednostkowe - pydantic validators
============================================================================
- walidacja współrzędnych GPS (latitude/longitude)
- walidacja czasu trwania (duration_seconds)
- poprawne rzucanie wyjątków ValueError
"""


def test_location_lat_long_valid():
    """
    test poprawnych współrzędnych GPS
    
    sprawdza:
    - akceptację poprawnych wartości latitude i longitude
    """
    loc = Location(city='X', state='S', country='PL', latitude=50.0, longitude=20.0)
    assert loc.latitude == 50.0


def test_location_lat_invalid():
    """
    test niepoprawnej wartości latitude
    
    sprawdza:
    - walidator check_latitude rzuca ValueError dla latitude > 90
    - pydantic validators działają przy tworzeniu obiektu (5 pkt bonus)
    """
    with pytest.raises(ValueError):
        Location(city='X', state='S', country='PL', latitude=150.0, longitude=20.0)


def test_location_long_invalid():
    """
    test niepoprawnej wartości longitude
    
    sprawdza:
    - walidator check_longitude rzuca ValueError dla longitude > 180
    """
    with pytest.raises(ValueError):
        Location(city='X', state='S', country='PL', latitude=50.0, longitude=200.0)


def test_sighting_duration_negative():
    """
    test ujemnego czasu trwania
    
    sprawdza:
    - walidator check_duration rzuca ValueError dla ujemnych wartości
    - logika biznesowa: czas trwania nie może być ujemny
    """
    with pytest.raises(ValueError):
        Sighting(datetime_utc=datetime.now(timezone.utc), duration_seconds=-5, comments='x', location=Location(city=None,state=None,country=None,latitude=None,longitude=None), shape=UFOShape.LIGHT)
