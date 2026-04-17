from typing import TypedDict


class ResolvedAxis(TypedDict):
    key: str
    label: str
    unit: str
    data: list


class ResolvedData(TypedDict):
    x_axis: ResolvedAxis
    y_axis: list[ResolvedAxis]
    dims: list[str]
    available_coords: list[dict]
    current_coord_index: int


class ResultResolver:
    def __init__(self, config: dict):
        self._config = config
        coords = config.get("coords", {})
        self._scatters = coords.get("scatters")
        self._current_coord_index = 0

        if self._scatters is None:
            single_coord = {
                "x": coords.get("x", ""),
                "y": coords.get("y", []),
            }
            self._scatters = [single_coord]

    def resolve(self, result: dict) -> ResolvedData | None:
        if not self._scatters:
            return None

        coord = self._scatters[self._current_coord_index]
        values = result.get("values", [])
        latex = result.get("latex", {})
        units = result.get("units", {})

        x_key = coord.get("x", "")
        y_keys = coord.get("y", [])

        x_data = [v.get(x_key, 0) for v in values]

        y_data_list = []
        for y_key in y_keys:
            y_data_list.append([v.get(y_key, 0) for v in values])

        x_label = latex.get(x_key, x_key)
        x_unit = units.get(x_key, "")
        if x_unit:
            x_label = f"{x_label} ({x_unit})"

        y_axis = []
        for y_key in y_keys:
            y_label = latex.get(y_key, y_key)
            y_unit = units.get(y_key, "")
            if y_unit:
                y_label = f"{y_label} ({y_unit})"
            y_axis.append(
                {
                    "key": y_key,
                    "label": y_label,
                    "unit": y_unit,
                    "data": [v.get(y_key, 0) for v in values],
                }
            )

        return {
            "x_axis": {
                "key": x_key,
                "label": x_label,
                "unit": x_unit,
                "data": x_data,
            },
            "y_axis": y_axis,
            "dims": result.get("dims", []),
            "available_coords": self._scatters,
            "current_coord_index": self._current_coord_index,
        }

    def setCurrentCoord(self, index: int) -> None:
        if 0 <= index < len(self._scatters):
            self._current_coord_index = index

    @property
    def available_coords(self) -> list[dict]:
        return self._scatters

    @property
    def has_multiple_coords(self) -> bool:
        return len(self._scatters) > 1
