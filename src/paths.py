"""Repository paths and output directories."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
CACHE = DATA / "cache"
OUTPUT = ROOT / "output"
FIGURES = OUTPUT / "figures"
TABLES = OUTPUT / "tables"

for path in (RAW, PROCESSED, CACHE, FIGURES, TABLES):
    path.mkdir(parents=True, exist_ok=True)
