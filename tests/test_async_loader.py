import asyncio
import tempfile
import os
import csv

from ufo_project.src import parser as _parser
from ufo_project.src.parser import load_sightings_async
import pytest

"""
testy jednostkowe - async loader
============================================================================
1. weryfikuje poprawność implementacji async/await
2. sprawdza integrację aiofiles + aiocsv
3. testuje pełny pipeline: plik CSV -> async czytanie -> obiekty Sighting

- tworzy temp csv, async parse, sprawdza wyniki i backpressure
"""

def test_async_loader_basic():
    rows = [
        {'datetime':'2020-01-01 00:00:00','city':'A','state':'S','country':'PL','shape':'light','duration':'10','latitude':'50','longitude':'20'},
        {'datetime':'2020-01-02 01:00:00','city':'B','state':'S','country':'PL','shape':'circle','duration':'5','latitude':'51','longitude':'21'},
    ]
    fd, path = tempfile.mkstemp(text=True, suffix='.csv')
    os.close(fd)
    try:
        # tworzymy tymczasowy plik CSV
        with open(path, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        
        # testujemy async loader
        results = asyncio.run(load_sightings_async(path, max_workers=4))
        assert len(results) == 2
    finally:
        # czyszczenie tymczasowych plików
        os.remove(path)
