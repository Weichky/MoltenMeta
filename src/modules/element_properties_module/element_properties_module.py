from dataclasses import dataclass


@dataclass(frozen=True)
class ElementProperties:
    symbol: str
    atomic_mass: float | None = None
    melting_point: float | None = None
    boiling_point: float | None = None
    liquid_range: float | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "ElementProperties":
        return cls(
            symbol=data.get("symbol", ""),
            atomic_mass=_nullable_float(data.get("atomic_mass")),
            melting_point=_nullable_float(data.get("melting_point")),
            boiling_point=_nullable_float(data.get("boiling_point")),
            liquid_range=_nullable_float(data.get("liquid_range")),
        )


def _nullable_float(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class ElementPropertiesCalc:
    def getProperty(self, symbol: str, property_name: str) -> float | None:
        props = self._data.get(symbol)
        if props is None:
            return None
        return getattr(props, property_name, None)

    def getAtomicMass(self, symbol: str) -> float | None:
        return self.getProperty(symbol, "atomic_mass")

    def getMeltingPoint(self, symbol: str) -> float | None:
        return self.getProperty(symbol, "melting_point")

    def getBoilingPoint(self, symbol: str) -> float | None:
        return self.getProperty(symbol, "boiling_point")

    def getLiquidRange(self, symbol: str) -> float | None:
        return self.getProperty(symbol, "liquid_range")

    def getAllAtomicMasses(self) -> dict[str, float]:
        return {
            symbol: props.atomic_mass
            for symbol, props in self._data.items()
            if props.atomic_mass is not None
        }

    def __init__(self):
        self._data: dict[str, ElementProperties] = {}
        self._loadFromCsv()

    def _loadFromCsv(self) -> None:
        import csv
        from importlib.resources import files

        csv_path = (
            files("modules.element_properties_module.data") / "element_properties.csv"
        )
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                symbol = row.get("symbol", "")
                if not symbol:
                    continue
                self._data[symbol] = ElementProperties.from_dict(row)
