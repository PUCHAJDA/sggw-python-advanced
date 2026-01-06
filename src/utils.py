from datetime import datetime, timezone
from dateutil import parser
from typing import Optional

"""
utility functions - pomocnicze funkcje parsowania
============================================================================
zgodnie z wytycznymi osobny moduł aby unikać powtarzania kodu
- funkcje używane w wielu miejscach (parser.py, testy)
- single responsibility - każda funkcja robi JEDNĄ rzecz

"""
def parse_datetime_to_utc(s: str) -> Optional[datetime]:
    """
    parsowanie daty z różnych formatów do datetime w UTC
    
    dateutil.parser
    =========================
    - potrafi sparsować wiele formatów dat ("2020-01-01", "01/01/2020", "Jan 1 2020")
    - lepsza obsługa edge cases niż datetime.strptime()
    
    zwraca Optional[datetime]:
    - None dla pustych/błędnych dat
    """
    if not s:
        return None
    try:
        dt = parser.parse(s)
    except Exception:
        # jeśli nie da się sparsować, zwracamy None zamiast rzucać wyjątek
        return None
    
    # jeśli data jest "naive" (bez timezone), przyjmujemy UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        # jeśli ma timezone, konwertujemy do UTC
        dt = dt.astimezone(timezone.utc)
    return dt


def parse_duration_seconds(s: Optional[str]) -> Optional[float]:
    """
    parsowanie czasu trwania obserwacji do sekund
    
    obsługa różnych formatów:
    ==========================
    - "12.5" -> 12.5
    - "about 5 minutes" -> 5.0
    - "a few" -> None
    - None -> None
    
    dlaczego regex?
    - dane CSV mają różne zapisy ("5", "5.0", "about 5", "approximately 5 seconds")
    - zwraca Optional[float]:
    - None dla braków lub błędnych danych
    """
    if s is None:
        return None
    s = s.strip()
    if not s:
        return None
    
    # próba bezpośredniej konwersji na float
    try:
        return float(s)
    except ValueError:
        # jeśli nie jest czystą liczbą, próbujemy wyciągnąć liczbę z tekstu
        import re
        m = re.search(r"([0-9]+(\.[0-9]+)?)", s)
        if m:
            return float(m.group(1))
    
    # jeśli nie udało się wyekstrahować liczby, zwracamy None
    return None
