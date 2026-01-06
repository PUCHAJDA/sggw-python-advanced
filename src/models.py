from __future__ import annotations
from pydantic import BaseModel, field_validator
from enum import Enum
from typing import Optional
from datetime import datetime

"""
modele danych - pydantic BaseModel zamiast standardowych @dataclass
============================================================================
spełnienie wytycznych:
- wykorzystanie dataclasses - ponieważ pydantic BaseModel to rozszerzone dataclasses
- pydantic dataclasses do walidacji
- prawidłowe typowanie - wszystkie pola mają określone typy
- dobre wykorzystanie Enum - UFOShape
"""


class UFOShape(Enum):
    """
    enum do reprezentacji kształtów UFO
    ============================================================================
    zastosowanie SOLID:
    - Single Responsibility: Enum odpowiada TYLKO za reprezentację kształtów
    """
    LIGHT = "light"
    TRIANGLE = "triangle"
    CIRCLE = "circle"
    DISK = "disk"
    FIREBALL = "fireball"
    ORB = "orb"
    UNKNOWN = "unknown"

    @classmethod
    def normalize(cls, s: Optional[str]) -> 'UFOShape':
        """
        normalizacja tekstu do enumu z prostym fuzzy-matching
        ============================================================================
        dlaczego tak
        - dane CSV mają różne zapisy tego samego kształtu ("triangle", "Triangle", "triangular")
        - zamiast wielu if-ów w kodzie centralizacja logiki normalizacji
        - unikamy powtarzania kodu
        """
        if not s:
            return cls.UNKNOWN
        s = s.strip().lower()
        for member in cls:
            if member.value == s:
                return member
        # fuzzy matching dla popularnych wariantów
        if 'triang' in s:
            return cls.TRIANGLE
        if 'disc' in s or 'disk' in s:
            return cls.DISK
        if 'light' in s:
            return cls.LIGHT
        if 'fire' in s:
            return cls.FIREBALL
        if 'orb' in s:
            return cls.ORB
        if 'circle' in s:
            return cls.CIRCLE
        return cls.UNKNOWN


class Location(BaseModel):
    """
    klasa reprezentująca lokalizację obserwacji UFO
    
    pydantic validators:
    - automatyczna walidacja zakresu współrzędnych przy tworzeniu obiektu
    - lepsze komunikaty błędów niż ręczne sprawdzanie
    """
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

    @field_validator('latitude')
    def check_latitude(cls, v: Optional[float]):
        """
        walidator współrzędnej latitude
        
        - latitude musi być w zakresie [-90, 90] (standard)
        - automatyczne sprawdzanie przy tworzeniu obiektu Location
        """
        if v is None:
            return v
        if not (-90.0 <= v <= 90.0):
            raise ValueError(f'latitude poza zakresem: {v}')
        return v

    @field_validator('longitude')
    def check_longitude(cls, v: Optional[float]):
        """
        walidator współrzędnej longitude      

        - longitude musi być w zakresie [-180, 180] (geograficzny standard)
        - chroni przed błędnymi danymi w CSV
        """
        if v is None:
            return v
        if not (-180.0 <= v <= 180.0):
            raise ValueError(f'longitude poza zakresem: {v}')
        return v


class Sighting(BaseModel):
    """
    główna klasa reprezentująca obserwację UFO
    
    - datetime_utc: datetime 
    - wszystkie daty przechowywane w UTC (wskazówka 4 - czas w UTC)
    - można łatwo konwertować do czasu lokalnego przy wyświetlaniu
    
    optional
    - dane z CSV mogą być niekompletne (brak duration, coordinates, etc.)
    - Optional[float] zamiast float pozwala na None bez błędów
    
    związki między klasami:
    - Sighting zawiera Location (kompozycja)
    - Sighting zawiera UFOShape (Enum)
    - "kolekcja powiązanych ze sobą obiektów"
    """
    datetime_utc: datetime
    duration_seconds: Optional[float]
    comments: Optional[str]
    location: Location
    shape: UFOShape
    raw_id: Optional[int] = None

    @field_validator('duration_seconds')
    def check_duration(cls, v: Optional[float]):
        """
        walidator czasu trwania obserwacji
        
        - duration nie może być ujemny (logika biznesowa)
        - automatyczne sprawdzanie przy parsowaniu CSV
        - chroni przed błędnymi danymi
        """
        if v is None:
            return v
        try:
            if v < 0:
                raise ValueError(f'duration_seconds musi być >= 0: {v}')
        except TypeError:
            raise ValueError(f'duration_seconds musi być liczbą: {v}')
        return v
