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
    conditions: dict
    title: str


class ResultResolver:
    def __init__(self, config: dict):
        self._config = config
        self._plot_type = config.get("plotType", "line_2d")
        coords = config.get("coords", {})
        self._scatters = coords.get("scatters")
        self._default_coord_index = config.get("default_coord_index", 0)
        self._x_label_override = coords.get("xLabel", "")
        self._y_label_override = coords.get("yLabel", "")
        self._z_label_override = coords.get("zLabel", "")
        self._current_coord_index = 0
        self._title_template = config.get("title", "")

        if self._scatters is None:
            single_coord = {
                "x": coords.get("x", ""),
                "y": coords.get("y", []),
            }
            self._scatters = [single_coord]

    def _replaceTitlePlaceholders(self, title: str, conditions: dict) -> str:
        for key, value in conditions.items():
            placeholder = "{" + key + "}"
            if placeholder in title:
                title = title.replace(placeholder, str(value))
        return title

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
            "conditions": result.get("conditions", {}),
            "title": self._replaceTitlePlaceholders(
                self._title_template, result.get("conditions", {})
            ),
        }

    def _resolve_contour_triangular(self, result: dict) -> ResolvedData | None:
        latex = result.get("latex", {})
        units = result.get("units", {})
        dims = result.get("dims", [])
        values = result.get("values", [])

        z_key = "Z_ABC"
        if values and isinstance(values[0], dict):
            for k in values[0]:
                if k not in ("x_A", "x_B", "x_C"):
                    z_key = k
                    break
        elif dims:
            for d in dims:
                if d not in ("x_A", "x_B", "x_C"):
                    z_key = d
                    break

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
            "conditions": result.get("conditions", {}),
            "title": self._replaceTitlePlaceholders(
                self._title_template, result.get("conditions", {})
            ),
        }

    def _resolve_scatter_3d(self, result: dict) -> ResolvedData | None:
        if not self._scatters:
            return None

        coord = self._scatters[self._current_coord_index]
        values = result.get("values", [])
        latex = result.get("latex", {})
        units = result.get("units", {})
        dims = result.get("dims", [])
        main_dim = result.get("main_dim")

        def _resolve_key(coord_key: str, fallback_key: str | None) -> str:
            if coord_key in dims and (not values or coord_key in values[0]):
                return coord_key
            if fallback_key and fallback_key in dims:
                return fallback_key
            if main_dim and main_dim in dims:
                return main_dim
            return coord_key

        x_key = coord.get("x", "")
        y_value = coord.get("y", [])
        if isinstance(y_value, str):
            y_keys = [y_value]
        else:
            y_keys = y_value
        z_key = coord.get("z", "")

        x_key = _resolve_key(x_key, None)
        y_keys = [_resolve_key(k, dims[1] if len(dims) > 1 else None) for k in y_keys]
        z_key = _resolve_key(z_key, main_dim)

        x_data = [v.get(x_key, 0) for v in values]

        if self._x_label_override:
            x_label = self._x_label_override
        else:
            x_label = latex.get(x_key, x_key)
        x_unit = units.get(x_key, "")
        if x_unit:
            x_label = f"{x_label} ({x_unit})"

        y_axis = []
        for y_key in y_keys:
            if self._y_label_override:
                y_label = self._y_label_override
            else:
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
            if self._z_label_override:
                z_label = self._z_label_override
            else:
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
            "dims": dims,
            "available_coords": self._scatters,
            "current_coord_index": self._current_coord_index,
            "plot_type": "scatter_3d",
            "mesh_data": None,
            "conditions": result.get("conditions", {}),
            "title": self._replaceTitlePlaceholders(
                self._title_template, result.get("conditions", {})
            ),
        }

    def _resolve_2d(self, result: dict) -> ResolvedData | None:
        if not self._scatters:
            return None

        coord = self._scatters[self._current_coord_index]
        values = result.get("values", [])
        latex = result.get("latex", {})
        units = result.get("units", {})
        dims = result.get("dims", [])
        main_dim = result.get("main_dim")

        def _resolve_key(coord_key: str, fallback_key: str | None) -> str:
            if coord_key in dims and (not values or coord_key in values[0]):
                return coord_key
            if fallback_key and fallback_key in dims:
                return fallback_key
            if main_dim and main_dim in dims:
                return main_dim
            return coord_key

        x_key = coord.get("x", "")
        y_value = coord.get("y", [])
        if isinstance(y_value, str):
            y_keys = [y_value]
        else:
            y_keys = y_value

        x_key = _resolve_key(x_key, dims[1] if len(dims) > 1 else None)
        y_keys = [_resolve_key(k, main_dim) for k in y_keys]

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
            "dims": dims,
            "available_coords": self._scatters,
            "current_coord_index": self._current_coord_index,
            "plot_type": self._plot_type,
            "mesh_data": None,
            "conditions": result.get("conditions", {}),
            "title": self._replaceTitlePlaceholders(
                self._title_template, result.get("conditions", {})
            ),
        }

    def setCurrentCoord(self, index: int) -> None:
        if 0 <= index < len(self._scatters):
            self._current_coord_index = index

    def useDefaultCoord(self) -> None:
        if 0 <= self._default_coord_index < len(self._scatters):
            self._current_coord_index = self._default_coord_index

    @property
    def available_coords(self) -> list[dict]:
        return self._scatters

    @property
    def has_multiple_coords(self) -> bool:
        return len(self._scatters) > 1

    @property
    def plot_type(self) -> str:
        return self._plot_type
