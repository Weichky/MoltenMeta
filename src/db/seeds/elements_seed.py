import csv
from importlib.resources import files

from domain.snapshot import ElementSnapshot

DEFAULT_ELEMENTS_CSV = files("resources.data") / "elements.csv"


def loadDefaultElements() -> list[ElementSnapshot]:
    return loadElementsFromCsv(DEFAULT_ELEMENTS_CSV)


def loadElementsFromCsv(csv_path) -> list[ElementSnapshot]:
    snapshots: list[ElementSnapshot] = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            atomic_mass = float(row["atomic_mass"]) if row.get("atomic_mass") else None
            melting_point = (
                float(row["melting_point"]) if row.get("melting_point") else None
            )
            boiling_point = (
                float(row["boiling_point"]) if row.get("boiling_point") else None
            )
            liquid_range = (
                float(row["liquid_range"]) if row.get("liquid_range") else None
            )

            snapshots.append(
                ElementSnapshot(
                    symbol_id=int(row["symbol_id"]),
                    atomic_mass=atomic_mass,
                    melting_point=melting_point,
                    boiling_point=boiling_point,
                    liquid_range=liquid_range,
                )
            )

    return snapshots


def loadElementsFromCsvFile(file_path: str) -> list[ElementSnapshot]:
    return loadElementsFromCsv(file_path)
