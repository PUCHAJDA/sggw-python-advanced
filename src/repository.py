from typing import List, Dict, Iterable, Tuple
from collections import defaultdict
from .models import Sighting, UFOShape, Location

"""
repository pattern - SOLID
============================================================================
1. wzorzec projektowy separujący logikę przechowywania od logiki biznesowej
2. łatwe testowanie (możemy mockować repo)
3. możliwość zmiany sposobu przechowywania (lista -> baza danych) bez zmian w kodzie klienckim

SOLID principles:
==================
S - single responsibility: 
    repository TYLKO przechowuje i agreguje dane
    parser TYLKO konwertuje CSV -> obiekty
    models TYLKO definiują strukturę danych

O - open/closed:
    możemy dodać nowe metody (by_date, by_duration) bez zmiany istniejących

L - liskov substitution:
    można stworzyć interfejs IRepository i mieć różne implementacje

I - interface segregation:
    klienci używają tylko tych metod których potrzebują

D - dependency inversion:
    main.py wstrzykuje dane do Repository (Dependency Injection)
"""


class SightingRepository:
    """
    repository przechowujące obserwacje UFO z indeksami do szybkiego wyszukiwania
    
    wzór repository:
    ====================
    enkapsuluje logikę przechowywania i dostępu do danych
    - klient (main.py) nie wie jak dane są przechowywane
    
    indeksy:
    =========
    _by_shape: Dict[UFOShape, List[Sighting]] - szybkie wyszukiwanie po kształcie
    _by_location: Dict[str, List[Sighting]] - szybkie wyszukiwanie po lokalizacji
    _all: List[Sighting] - wszystkie obserwacje
    
    dlaczego indeksy?
    - zamiast przeszukiwać listę za każdym razem (O(n)), używamy słowników (O(1))
    """
    def __init__(self, sightings: Iterable[Sighting] = ()): 
        self._by_shape: Dict[UFOShape, List[Sighting]] = defaultdict(list)
        self._by_location: Dict[str, List[Sighting]] = defaultdict(list)
        self._all: List[Sighting] = []
        for s in sightings:
            self.add(s)

    def add(self, s: Sighting) -> None:
        """
        dodanie obserwacji do wszystkich indeksów
        - jeden punkt dodawania danych
        - wszystkie indeksy zawsze spójne
        - łatwe testowanie (dodaj 1 obiekt, sprawdź czy jest we wszystkich indeksach)
        """
        self._all.append(s)
        self._by_shape[s.shape].append(s)
        key = f"{s.location.city or ''},{s.location.state or ''},{s.location.country or ''}".lower()
        self._by_location[key].append(s)

    def all(self) -> List[Sighting]:
        """
        zwraca wszystkie obserwacje
        - chroni wewnętrzny stan repository przed modyfikacją z zewnątrz
        - immutability pattern - bezpieczniejszy kod
        """
        return list(self._all)

    def by_shape(self, shape: UFOShape) -> List[Sighting]:
        """
        wyszukiwanie po kształcie UFO        
        typowanie:
        - shape: UFOShape - IDE podpowiada możliwe wartości
        - -> List[Sighting] - wiadomo co zwraca funkcja
        """
        return list(self._by_shape.get(shape, []))

    def by_country(self, country: str) -> List[Sighting]:
        """
        wyszukiwanie po kraju
        
        TODO: można ulepszyć używając normalizacji nazw krajów lub geospatial indexing
        """
        key_suffix = f",,,{country}".lower()
        results = []
        for k, v in self._by_location.items():
            if k.endswith(country.lower()):
                results.extend(v)
        return results

    def top_shapes(self, n: int = 10):
        """
        agregacja: najpopularniejsze kształty UFO
        - list comprehension zamiast pętli for
        - lambda function w sort()
        - slice [:n] zamiast oddzielnej pętli
        """
        counts: List[Tuple[UFOShape, int]] = [(shape, len(lst)) for shape, lst in self._by_shape.items()]
        counts.sort(key=lambda x: x[1], reverse=True)
        return counts[:n]

    def export_json(self) -> str:
        """
        eksport danych do JSON
        - repository wie jak dane są przechowywane
        - separacja odpowiedzialności - eksport to część zarządzania danymi
        """
        import json
        def loc_to_dict(loc: Location):
            return {
                'city': loc.city,
                'state': loc.state,
                'country': loc.country,
                'latitude': loc.latitude,
                'longitude': loc.longitude,
            }
        payload = []
        for s in self._all:
            payload.append({
                'datetime_utc': s.datetime_utc.isoformat(),
                'duration_seconds': s.duration_seconds,
                'comments': s.comments,
                'location': loc_to_dict(s.location),
                'shape': s.shape.value,
            })
        return json.dumps(payload, ensure_ascii=False, indent=2)
