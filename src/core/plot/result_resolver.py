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
    availableCoords: list[dict]
    currentCoordIndex: int
    plotType: str
    meshData: dict | None
    conditions: dict
    title: str


class ResultResolver:
    def __init__(self, config: dict):
        self._config = config
        self._plotType = config.get("plotType", "line_2d")
        coords = config.get("coords", {})
        self._scatters = coords.get("scatters")
        self._defaultCoordIndex = config.get("default_coord_index", 0)
        self._xLabelOverride = coords.get("xLabel", "")
        self._yLabelOverride = coords.get("yLabel", "")
        self._zLabelOverride = coords.get("zLabel", "")
        self._currentCoordIndex = 0
        self._titleTemplate = config.get("title", "")

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

    def _resolveKey(
        self,
        coord_key: str,
        dims: list[str],
        values: list,
        main_dim: str | None,
        fallback_key: str | None,
    ) -> str:
        if coord_key in dims and (not values or coord_key in values[0]):
            return coord_key
        if fallback_key and fallback_key in dims:
            return fallback_key
        if main_dim and main_dim in dims:
            return main_dim
        return coord_key

    def resolve(self, result: dict) -> ResolvedData | None:
        # Dispatch to the appropriate resolution path based on plot type.
        # Each path returns a ResolvedData structure with axis definitions,
        # raw values, and metadata for the GUI layer to render.
        if self._plotType == "contour":
            return self._resolveContour(result)
        elif self._plotType == "contour_triangular":
            return self._resolveContourTriangular(result)
        elif self._plotType == "scatter_3d":
            return self._resolveScatter3d(result)
        else:
            return self._resolve2d(result)

    def _resolveContour(self, result: dict) -> ResolvedData | None:
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
            "availableCoords": [],
            "currentCoordIndex": 0,
            "plotType": "contour",
            "meshData": mesh_data,
            "conditions": result.get("conditions", {}),
            "title": self._replaceTitlePlaceholders(
                self._titleTemplate, result.get("conditions", {})
            ),
        }

    def _resolveContourTriangular(self, result: dict) -> ResolvedData | None:
        # For triangular contour, the resolver extracts the Z key (the property being plotted)
        # by scanning for the first key in values[0] that is not a composition coordinate.
        # Fallback: scan dims if values is empty or not a dict.
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
            "availableCoords": [],
            "currentCoordIndex": 0,
            "plotType": "contour_triangular",
            "meshData": None,
            "values": result.get("values", []),
            "conditions": result.get("conditions", {}),
            "title": self._replaceTitlePlaceholders(
                self._titleTemplate, result.get("conditions", {})
            ),
        }

    def _resolveScatter3d(self, result: dict) -> ResolvedData | None:
        if not self._scatters:
            return None

        coord = self._scatters[self._currentCoordIndex]
        values = result.get("values", [])
        latex = result.get("latex", {})
        units = result.get("units", {})
        dims = result.get("dims", [])
        main_dim = result.get("main_dim")

        x_key = coord.get("x", "")
        y_value = coord.get("y", [])
        if isinstance(y_value, str):
            y_keys = [y_value]
        else:
            y_keys = y_value
        z_key = coord.get("z", "")

        x_key = self._resolveKey(x_key, dims, values, main_dim, None)
        y_keys = [
            self._resolveKey(
                k, dims, values, main_dim, dims[1] if len(dims) > 1 else None
            )
            for k in y_keys
        ]
        z_key = self._resolveKey(z_key, dims, values, main_dim, main_dim)

        x_data = [v.get(x_key, 0) for v in values]

        if self._xLabelOverride:
            x_label = self._xLabelOverride
        else:
            x_label = latex.get(x_key, x_key)
        x_unit = units.get(x_key, "")
        if x_unit:
            x_label = f"{x_label} ({x_unit})"

        y_axis = []
        for y_key in y_keys:
            if self._yLabelOverride:
                y_label = self._yLabelOverride
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
            if self._zLabelOverride:
                z_label = self._zLabelOverride
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
            "availableCoords": self._scatters,
            "currentCoordIndex": self._currentCoordIndex,
            "plotType": "scatter_3d",
            "meshData": None,
            "conditions": result.get("conditions", {}),
            "title": self._replaceTitlePlaceholders(
                self._titleTemplate, result.get("conditions", {})
            ),
        }

    def _resolve2d(self, result: dict) -> ResolvedData | None:
        if not self._scatters:
            return None

        coord = self._scatters[self._currentCoordIndex]
        values = result.get("values", [])
        latex = result.get("latex", {})
        units = result.get("units", {})
        dims = result.get("dims", [])
        main_dim = result.get("main_dim")

        x_key = coord.get("x", "")
        y_value = coord.get("y", [])
        if isinstance(y_value, str):
            y_keys = [y_value]
        else:
            y_keys = y_value

        x_key = self._resolveKey(
            x_key, dims, values, main_dim, dims[1] if len(dims) > 1 else None
        )
        y_keys = [self._resolveKey(k, dims, values, main_dim, main_dim) for k in y_keys]

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
            "availableCoords": self._scatters,
            "currentCoordIndex": self._currentCoordIndex,
            "plotType": self._plotType,
            "meshData": None,
            "conditions": result.get("conditions", {}),
            "title": self._replaceTitlePlaceholders(
                self._titleTemplate, result.get("conditions", {})
            ),
        }

    def setCurrentCoord(self, index: int) -> None:
        if index < 0 or index >= len(self._scatters):
            return
        self._currentCoordIndex = index

    def useDefaultCoord(self) -> None:
        if 0 <= self._defaultCoordIndex < len(self._scatters):
            self._currentCoordIndex = self._defaultCoordIndex

    @property
    def availableCoords(self) -> list[dict]:
        return self._scatters

    @property
    def hasMultipleCoords(self) -> bool:
        return len(self._scatters) > 1

    @property
    def plotType(self) -> str:
        return self._plotType
