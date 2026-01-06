from ufo_project.src.parser import load_sightings_threaded, load_sightings_async
from ufo_project.src.repository import SightingRepository
from pathlib import Path
import asyncio

"""
main - dependency injection (SOLID - D: dependency inversion)
============================================================================
dlaczego dependency injection
1. kod nie jest sprzężony z konkretną implementacją loadera
2. łatwe testowanie - można wstrzyknąć mock loader
3. łatwa zmiana implementacji (sync -> async) bez zmian w logice biz

SOLID - D (dependency inversion principle):
- high-level module (run_with_loader) nie zależy od low-level module (konkretny loader)
- oba zależą od abstrakcji (funkcja przyjmująca path i zwracająca List[Sighting])
"""


def run_with_loader(loader_func, *args, **kwargs):
    """
    uruchomienie aplikacji z wstrzykniętym loaderem
    
    dependency injection:
    =====================
    - loader_func może być load_sightings_threaded lub load_sightings_async
    - nie musimy zmieniać kodu poniżej gdy dodamy nowy loader
    - ++ możemy wstrzyknąć mock zwracający testowe dane
    
    obsługa sync i async:
    =====================
    - asyncio.iscoroutinefunction() sprawdza czy funkcja jest async
    - asyncio.run() uruchamia async funkcję
    - jednocześnie działa z normalnym multithreading - multi jako default
    """
    if asyncio.iscoroutinefunction(loader_func):
        sightings = asyncio.run(loader_func(*args, **kwargs))
    else:
        sightings = loader_func(*args, **kwargs)
    
    # repository pattern - wstrzykujemy dane do repository
    repo = SightingRepository(sightings)
    total = len(repo.all())
    print(f'Załadowano {total:,} obserwacji UFO z pliku scrubbed.csv')
    print('Top 6 kształtów UFO:')
    for shape, cnt in repo.top_shapes(6):
        percent = (cnt / total * 100) if total > 0 else 0
        print(f'  {shape.name}: {cnt:,} ({percent:.0f}%)')


def main():
    """
    program demonstruje **obie implementacje równolegle**:
    1. multithreading loader (ThreadPoolExecutor, 8 workerów)
    2. async loader (aiofiles + asyncio)
    
    oba loadery ładują te same dane, różnica tylko w podejściu:
    - multithreading: równoległe przetwarzanie wierszy w wątkach
    - async: nieblokujące I/O z asyncio event loop
    
    obsługa błędów:
    ===============
    - sprawdzamy czy plik istnieje
    - opcjonalne zależności (async) nie przerywają działania programu
    """
    # ścieżka względna do CSV 
    data_csv = Path(__file__).parent / 'data' / 'scrubbed.csv'
    if not data_csv.exists():
        print('Umieść plik scrubbed.csv w ufo_project/data/ i uruchom ponownie')
        return

    # przykład 1: multithreading loader 
    print('Ładowanie obserwacji (multithreading loader z 8 workerami)...')
    run_with_loader(load_sightings_threaded, str(data_csv), max_workers=8)

    # przykład 2: async loader
    try:
        print('\nPróba uruchomienia async loadera (jeśli dostępny)...')
        run_with_loader(load_sightings_async, str(data_csv))
    except ImportError as e:
        # jeśli brak zależności async, pomijamy bez exit 1
        print('Async loader został pominięty (brak opcjonalnych bibliotek aiofiles/aiocsv),\nale program działa poprawnie z multithreading loaderem.')


if __name__ == '__main__':
    main()
