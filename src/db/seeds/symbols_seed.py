import csv
from importlib.resources import files

from db.snapshot import SymbolSnapshot

DEFAULT_SYMBOLS_CSV = files("resources.data") / "symbols.csv"


def loadDefaultSymbols() -> list[SymbolSnapshot]:
    return loadSymbolsFromCsv(DEFAULT_SYMBOLS_CSV)


def loadSymbolsFromCsv(csv_path) -> list[SymbolSnapshot]:
    snapshots: list[SymbolSnapshot] = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            snapshots.append(
                SymbolSnapshot(
                    symbol=row["symbol"],
                    name=row.get("name"),
                    category=row.get("category"),
                )
            )

    return snapshots


def loadSymbolsFromCsvFile(file_path: str) -> list[SymbolSnapshot]:
    return loadSymbolsFromCsv(file_path)
