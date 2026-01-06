from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, List, Optional, Dict, Any
import csv
from pathlib import Path
from .models import Sighting, Location, UFOShape
from .utils import parse_datetime_to_utc, parse_duration_seconds
import asyncio

"""
parser CSV - async/multithreading
============================================================================
dlaczego dwie implementacje
1. ThreadPoolExecutor (load_sightings_threaded) - prosty multithreading
2. Async/await (load_sightings_async) - pełna asynchroniczność z aiofiles

use cases
- threaded: szybsze dla średnich plików, łatwiejsze w debugowaniu
- async: lepsze dla bardzo dużych plików (nie blokuje I/O)

wytyczne:
- wykorzystanie async/multithreading
- prawidłowe typowanie - wszystkie funkcje mają type hints
- kod zwięzły - używam list comprehension, executorów
"""

try:
    import aiofiles
    from aiocsv import AsyncDictReader
except Exception:
    # opcjonalne zależności - projekt będzie działał bez nich (tylko threaded loader)
    aiofiles = None
    AsyncDictReader = None


def parse_row_to_sighting(row: Dict[str, Any]) -> Optional[Sighting]:
    """
    konwersja wiersza CSV na obiekt Sighting
    
    osobna funkcja aby unikać powtarzania kodu
    ==================================================================
    - ta sama logika używana w threaded i async loaderach
    - łatwo przetestować (test_parser.py)
    - można zmienić logikę w jednym miejscu
    
    obsługa różnych nazw kolumn:
    - row.get('datetime') or row.get('date_time') - różne CSVy mają różne nagłówki
    - zwraca None jeśli brak wymaganego pola (datetime) - filtrujemy zwalone dane
    
    zwięzłość kodu
    - używamy dict.get() zamiast if-ów
    - UFOShape.normalize() zamiast długich warunków
    """
    dt = parse_datetime_to_utc(row.get('datetime') or row.get('date_time') or row.get('time'))
    if dt is None:
        # bez daty nie możemy utworzyć obserwacji - pomijamy wiersz
        return None
    dur = parse_duration_seconds(row.get('duration (seconds)') or row.get('duration_seconds') or row.get('duration'))
    loc = Location(
        city=row.get('city') or None,
        state=row.get('state') or None,
        country=row.get('country') or None,
        latitude=float(row['latitude']) if row.get('latitude') else None,
        longitude=float(row['longitude']) if row.get('longitude') else None,
    )
    shape = UFOShape.normalize(row.get('shape'))
    s = Sighting(datetime_utc=dt, duration_seconds=dur, comments=row.get('comments') or None, location=loc, shape=shape)
    return s


def read_csv(path: str) -> Iterable[Dict[str, Any]]:
    """
    generator wierszy CSV - oszczędza pamięć
    
    - duże pliki CSV (setki tysięcy wierszy) nie mieszczą się w pamięci
    - Iterable[Dict] zamiast List[Dict] - przetwarzamy strumieniowo
    """
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            yield row


def load_sightings_threaded(path: str, max_workers: int = 8) -> List[Sighting]:
    """
    multithreading - ładowanie z równoległym parsowaniem
    
    threadpoolexecutor
    ================================================================
    1. parsowanie wielu wierszy równocześnie (8 wątków = 8x szybciej) - zawsze wymaga dotunowania do wątków cpu - można przedobrzyć
    2. proste w użyciu - submit() + as_completed()
    
    zwięzłość kodu:
    - list comprehension: [ex.submit(...) for row in rows]
    - pomijamy błędne wiersze bez przerywania procesu
    """
    rows = list(read_csv(path))
    sightings: List[Sighting] = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        # tworzenie tasków dla wszystkich wierszy
        futures = [ex.submit(parse_row_to_sighting, row) for row in rows]
        for fut in as_completed(futures):
            try:
                res = fut.result()
                if res is not None:
                    sightings.append(res)
            except Exception:
                # błędne wiersze pomijamy - nie przerywamy całego procesu
                continue
    return sightings


async def load_sightings_async(path: str, max_workers: int = 8) -> List[Sighting]:
    """
    async/await - pełna asynchroniczność
    
    async
    ================================================================
    1. aiofiles - nie blokuje I/O podczas czytania pliku
    2. AsyncDictReader - strumieniowe czytanie CSV bez blokowania
    3. Semaphore - kontrola równoległości (backpressure)
    4. run_in_executor - parsowanie CPU-bound w tle bez blokowania event loop

    Do użytku przy bardzo dużych plikach lub bardzo dużej liczbie plików.
    
    mechanizm backpressure:
    - Semaphore(max_workers * 2) kaganiec liczby zadań
    - gdy tasks >= max_workers * 10, czekamy na zakończenie części
    
    """
    if aiofiles is None or AsyncDictReader is None:
        raise ImportError('aiofiles i aiocsv są wymagane dla async loadera')

    sightings: List[Sighting] = []
    loop = asyncio.get_running_loop()

    # semaphore ogranicza liczbę równoczesnych zadań - zapobiega zużyciu pamięci
    semaphore = asyncio.Semaphore(max_workers * 2)

    async def _parse_row_async(row: Dict[str, Any]):
        """parsowanie w executorze - nie blokuje event loop"""
        async with semaphore:
            return await loop.run_in_executor(None, parse_row_to_sighting, row)

    tasks: List[asyncio.Task] = []

    async with aiofiles.open(path, mode='r', encoding='utf-8', newline='') as afp:
        async for row in AsyncDictReader(afp):
            # harmonogramujemy parsowanie w tle (nie czekamy na wynik)
            task = asyncio.create_task(_parse_row_async(row))
            tasks.append(task)
            # backpressure: gdy zbierze się zbyt wiele zadań, czekamy na część
            if len(tasks) >= max_workers * 10:
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for d in done:
                    try:
                        res = d.result()
                        if res is not None:
                            sightings.append(res)
                    except Exception:
                        continue
                tasks = list(pending)

    # zbieramy pozostałe zadania po zakończeniu czytania pliku
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                continue
            if r is not None:
                sightings.append(r)

    return sightings
