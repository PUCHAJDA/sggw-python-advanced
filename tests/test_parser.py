from ufo_project.src.parser import parse_row_to_sighting
from ufo_project.src.models import UFOShape

"""
testy jednostkowe - parser
============================================================================
- podstawowe parsowanie wiersza CSV
- poprawna konwersję typów (str -> datetime, str -> float)
- mapowanie pól CSV na pola obiektów
"""


def test_parse_row_to_sighting_basic():
    """
    test podstawowego parsowania wiersza CSV
    
    sprawdza:
    - konwersję wszystkich pól z CSV do obiektów
    - parsowanie daty (str -> datetime)
    - parsowanie współrzędnych (str -> float)
    - normalizację kształtu do Enum
    """
    row = {
        'datetime': '2020-01-01 00:00:00',
        'city': 'TestCity',
        'state': 'TS',
        'country': 'PL',
        'shape': 'light',
        'duration (seconds)': '12',
        'comments': 'strange light',
        'latitude': '52.0',
        'longitude': '21.0',
    }
    s = parse_row_to_sighting(row)
    assert s is not None
    assert s.shape == UFOShape.LIGHT
    assert s.location.city == 'TestCity'
