from ufo_project.src.parser import parse_row_to_sighting
from ufo_project.src.models import UFOShape

"""
testy jednostkowe - parser edge cases
============================================================================
- obsługa brakujących wymaganych pól (datetime)
- obsługa błędnych formatów (nieparsowalne daty)
- obsługa dziwnych formatów duration ("about 5 seconds")
- obsługa całkowicie nieparsywalnych wartości
"""


def test_parse_row_missing_datetime():
    """
    test braku wymaganego pola datetime
    
    sprawdza:
    - parser zwraca None dla wierszy bez daty
    - nie rzuca wyjątku (graceful degradation)
    - reguła biznesowa: bez daty nie ma obserwacji
    """
    row = {'city':'A','shape':'light'}
    res = parse_row_to_sighting(row)
    assert res is None


def test_parse_row_bad_datetime():
    """
    test nieprawidłowego formatu daty
    
    sprawdza:
    - parser zwraca None dla nieparsywalnych dat
    - dateutil.parser.parse() bezpiecznie obsługuje błędy
    """
    row = {'datetime':'not a date','city':'A','shape':'light'}
    res = parse_row_to_sighting(row)
    assert res is None


def test_parse_row_weird_duration():
    """
    test dziwnego formatu duration ("about 5 seconds")
    
    sprawdza:
    - parser wyciąga liczby z tekstu używając regex
    - "about 5 seconds" -> 5.0
    - dane CSV często mają takie niestandaryzowane formaty
    """
    row = {
        'datetime':'2020-01-01 00:00:00',
        'city':'A','shape':'circle','duration':'about 5 seconds',
        'latitude':'50','longitude':'20'
    }
    res = parse_row_to_sighting(row)
    assert res is not None
    assert res.duration_seconds == 5.0


def test_parse_row_non_numeric_duration():
    """
    test całkowicie nieparsywalnego duration ("a few")
    
    sprawdza:
    - parser zwraca None dla duration gdy nie może wyekstrahować liczby
    - nie crashuje całego procesu parsowania
    - obserwacja jest tworzona (datetime jest OK), ale duration = None
    """
    row = {
        'datetime':'2020-01-01 00:00:00',
        'city':'A','shape':'circle','duration':'a few',
        'latitude':'50','longitude':'20'
    }
    res = parse_row_to_sighting(row)
    # parser tworzy obiekt, ale duration jest None
    assert res is not None
    assert res.duration_seconds is None
