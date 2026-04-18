from typing import TypedDict


class ResolvedAxis(TypedDict):
    key: str
    label: str
    unit: str
    data: list


class ResolvedData(TypedDict):
    x_axis: ResolvedAxis
    y_axis: list[ResolvedAxis]
    z_axis: ResolvedAxis | None
    dims: list[str]
    available_coords: list[dict]
    current_coord_index: int
    plot_type: str
    mesh_data: dict | None


class ResultResolver:
    def __init__(self, config: dict):
        self._config = config
        self._plot_type = config.get("plotType", "line_2d")
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
        if self._plot_type == "contour":
            return self._resolve_contour(result)
        elif self._plot_type == "contour_triangular":
            return self._resolve_contour_triangular(result)
        elif self._plot_type == "scatter_3d":
            return self._resolve_scatter_3d(result)
        else:
            return self._resolve_2d(result)

    def _resolve_contour(self, result: dict) -> ResolvedData | None:
        latex = result.get("latex", {})
        units = result.get("units", {})

        z_key = "Z_ABC"
        z_label = latex.get(z_key, z_key)
        z_unit = units.get(z_key, "")
        if z_unit:
            z_label = f"{z_label} ({z_unit})"

        mesh_data = {
            "x_i": result.get("x_i", []),
            "x_j": result.get("x_j", []),
            "Z_ABC": result.get("Z_ABC", []),
            "plane": result.get("plane", ""),
        }

        return {
            "x_axis": {
                "key": "x_i",
                "label": "x_i",
                "unit": "",
                "data": [],
            },
            "y_axis": [],
            "z_axis": {
                "key": z_key,
                "label": z_label,
                "unit": z_unit,
                "data": [],
            },
            "dims": result.get("dims", []),
            "available_coords": [],
            "current_coord_index": 0,
            "plot_type": "contour",
            "mesh_data": mesh_data,
        }

    def _resolve_contour_triangular(self, result: dict) -> ResolvedData | None:
        latex = result.get("latex", {})
        units = result.get("units", {})

        z_key = "Z_ABC"
        z_label = latex.get(z_key, z_key)
        z_unit = units.get(z_key, "")
        if z_unit:
            z_label = f"{z_label} ({z_unit})"

        return {
            "x_axis": {
                "key": "x_A",
                "label": "x_A",
                "unit": "",
                "data": [],
            },
            "y_axis": [],
            "z_axis": {
                "key": z_key,
                "label": z_label,
                "unit": z_unit,
                "data": [],
            },
            "dims": result.get("dims", []),
            "available_coords": [],
            "current_coord_index": 0,
            "plot_type": "contour_triangular",
            "values": result.get("values", []),
        }

    def _resolve_scatter_3d(self, result: dict) -> ResolvedData | None:
        if not self._scatters:
            return None

        coord = self._scatters[self._current_coord_index]
        values = result.get("values", [])
        latex = result.get("latex", {})
        units = result.get("units", {})

        x_key = coord.get("x", "")
        y_keys = coord.get("y", [])
        z_key = coord.get("z", "")

        x_data = [v.get(x_key, 0) for v in values]

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

        z_axis = None
        if z_key:
            z_label = latex.get(z_key, z_key)
            z_unit = units.get(z_key, "")
            if z_unit:
                z_label = f"{z_label} ({z_unit})"
            z_axis = {
                "key": z_key,
                "label": z_label,
                "unit": z_unit,
                "data": [v.get(z_key, 0) for v in values],
            }

        return {
            "x_axis": {
                "key": x_key,
                "label": x_label,
                "unit": x_unit,
                "data": x_data,
            },
            "y_axis": y_axis,
            "z_axis": z_axis,
            "dims": result.get("dims", []),
            "available_coords": self._scatters,
            "current_coord_index": self._current_coord_index,
            "plot_type": "scatter_3d",
            "mesh_data": None,
        }

    def _resolve_2d(self, result: dict) -> ResolvedData | None:
        if not self._scatters:
            return None

        coord = self._scatters[self._current_coord_index]
        values = result.get("values", [])
        latex = result.get("latex", {})
        units = result.get("units", {})

        x_key = coord.get("x", "")
        y_keys = coord.get("y", [])

        x_data = [v.get(x_key, 0) for v in values]

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
            "z_axis": None,
            "dims": result.get("dims", []),
            "available_coords": self._scatters,
            "current_coord_index": self._current_coord_index,
            "plot_type": self._plot_type,
            "mesh_data": None,
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

    @property
    def plot_type(self) -> str:
        return self._plot_type
