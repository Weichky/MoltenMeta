from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt

from .ui import UiSimulationPage
from .controller import SimulationController
from .plot_panel import PlotPanel
from .result_resolver import ResultResolver

from core.plot import PlotStyleService


class ResultTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._columns: list[str] = []
        self._data: list[list] = []

    def update(self, columns: list[str], data: list[list]) -> None:
        self.beginResetModel()
        self._columns = columns
        self._data = data
        self.endResetModel()

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(self._columns)

    def data(self, index: QtCore.QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        row = index.row()
        col = index.column()
        if row < len(self._data) and col < len(self._columns):
            return str(self._data[row][col])
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> str | None:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal and section < len(self._columns):
            return self._columns[section]
        return None


class SimulationPage(QtWidgets.QWidget):
    configureClicked = QtCore.Signal()
    calculateClicked = QtCore.Signal()

    def __init__(self, context):
        super().__init__(parent=None)
        self._context = context
        self._i18n = context.i18n
        self._theme_service = context.theme
        self._controller = SimulationController(context)
        self._plot_style_service = PlotStyleService()

        self._current_category: str = ""
        self._current_module: str = ""
        self._current_method: str = ""
        self._result_resolver: ResultResolver | None = None
        self._current_result: dict | None = None
        self._module_widget: QtWidgets.QWidget | None = None

        self.ui = UiSimulationPage()
        self.ui.setupUi(self)

        self._plot_panel = PlotPanel()
        self.ui.plotContainer.addWidget(self._plot_panel)

        self._result_model = ResultTableModel()
        self.ui.resultTable.setModel(self._result_model)
        self.ui.resultTable.horizontalHeader().setStretchLastSection(True)

        self._connectSignals()
        self._populateCategories()
        self._applyTheme()

    def _clearModuleWidget(self) -> None:
        if self._module_widget is not None:
            self._module_widget.setParent(None)
            self._module_widget = None

    def _loadModuleWidget(self) -> None:
        pass

    def _connectSignals(self) -> None:
        self.ui.categoryCombo.currentIndexChanged.connect(self._onCategoryChanged)
        self.ui.moduleCombo.currentIndexChanged.connect(self._onModuleChanged)
        self.ui.methodCombo.currentIndexChanged.connect(self._onMethodChanged)
        self.ui.configureBtn.clicked.connect(self._onConfigureClicked)
        self.ui.calculateBtn.clicked.connect(self._onCalculateClicked)
        self._i18n.language_changed.connect(self._retranslateUi)
        self._theme_service.theme_changed.connect(self._applyTheme)
        if hasattr(self.ui, "coordSelector"):
            self.ui.coordSelector.currentIndexChanged.connect(self._onCoordChanged)

    def _applyTheme(self) -> None:
        settings = self._context.settings
        plot_color_scheme = settings.plot_color_scheme
        if plot_color_scheme == "follow":
            scheme = self._theme_service.scheme
        else:
            scheme = plot_color_scheme
        self._plot_panel.setScheme(scheme)

    def _populateCategories(self) -> None:
        categories = self._controller.getCategories()
        self.ui.categoryCombo.clear()
        for cat in categories:
            self.ui.categoryCombo.addItem(cat)

    def _onCategoryChanged(self, index: int) -> None:
        if index < 0:
            return
        self._current_category = self.ui.categoryCombo.currentText()
        modules = self._controller.getModulesByCategory(self._current_category)
        self.ui.moduleCombo.clear()
        for m in modules:
            self.ui.moduleCombo.addItem(m["name"], m["package_name"])

    def _onModuleChanged(self, index: int) -> None:
        if index < 0:
            return
        self._current_module = self.ui.moduleCombo.currentData()

        self._clearModuleWidget()

        if self._controller.hasModuleWidget(self._current_module):
            self._loadModuleWidget()

        if self._current_module:
            methods = self._controller.getMethodsByModule(self._current_module)
            self.ui.methodCombo.clear()
            for method in methods:
                self.ui.methodCombo.addItem(method)

    def _onMethodChanged(self, index: int) -> None:
        if index < 0:
            return
        self._current_method = self.ui.methodCombo.currentText()
        if self._current_module and self._current_method:
            self._controller.loadModuleConfig(
                self._current_module, self._current_method
            )
            method_config = self._controller.getCurrentConfig().get(
                self._current_method, {}
            )
            self._result_resolver = ResultResolver(method_config.get("plot", {}))
            self._setupCoordSelector()

    def _onConfigureClicked(self) -> None:
        if not self._current_module or not self._current_method:
            return

        if self._controller.hasModuleWidget(self._current_module):
            dialog = self._controller.getModuleWidget(
                self._current_module, self._current_method
            )
            if dialog is None:
                self.ui.statusLabel.setText("Error: No wizard for this method")
                return
            dialog.resultReady.connect(self._onModuleWidgetResult)
            dialog.exec()
        else:
            accepted, inputs = self._controller.showInputDialog(
                self._current_method, self
            )
            if accepted:
                self._pending_inputs = inputs
                self.ui.statusLabel.setText(f"Ready: {len(inputs)} inputs configured")

    def _onCalculateClicked(self) -> None:
        if not self._current_module or not self._current_method:
            return

        inputs = getattr(self, "_pending_inputs", {})
        if not inputs:
            self._onConfigureClicked()
            return

        try:
            result = self._controller.callCalculation(
                self._current_module, self._current_method, **inputs
            )
            self._displayResult(result)
            self.ui.statusLabel.setText("Calculation complete")
        except Exception as e:
            self.ui.statusLabel.setText(f"Error: {e}")

    def _onModuleWidgetResult(self, result: dict) -> None:
        if not self._current_module:
            return

        try:
            self._displayResult(result)
            self.ui.statusLabel.setText("Calculation complete")
        except Exception as e:
            self.ui.statusLabel.setText(f"Error: {e}")

    def _setupCoordSelector(self) -> None:
        if not self._result_resolver:
            return

        if hasattr(self.ui, "coordSelector"):
            if not self._result_resolver.has_multiple_coords:
                self.ui.coordSelector.setVisible(False)
                return

            self.ui.coordSelector.setVisible(True)
            self.ui.coordSelector.clear()
            for coord in self._result_resolver.available_coords:
                labels = []
                if coord.get("x"):
                    labels.append(coord["x"])
                if coord.get("y"):
                    labels.extend(coord["y"])
                if coord.get("z"):
                    labels.append(coord["z"])
                self.ui.coordSelector.addItem(" × ".join(labels))

    def _onCoordChanged(self, index: int) -> None:
        if self._result_resolver:
            self._result_resolver.setCurrentCoord(index)
        if self._current_result:
            self._displayResult(self._current_result)

    def _displayResult(self, result: dict) -> None:
        self._current_result = result

        if not self._result_resolver:
            self.ui.statusLabel.setText("Error: No result resolver")
            return

        resolved = self._result_resolver.resolve(result)
        if not resolved:
            self.ui.statusLabel.setText("Error: Failed to resolve result")
            return

        config = self._controller.getCurrentConfig()
        module_config = config.get("module", {})
        method_config = config.get(self._current_method, {})
        settings = self._context.settings

        plot_config = self._plot_style_service.buildConfig(
            module_config, method_config, settings
        )

        plot_color_scheme = settings.plot_color_scheme
        if plot_color_scheme == "follow":
            scheme = self._theme_service.scheme
        else:
            scheme = plot_color_scheme
        self._plot_panel.setScheme(scheme)

        plot_type = resolved.get("plot_type", "line_2d")
        x_data = resolved["x_axis"]["data"]
        x_label = resolved["x_axis"]["label"]

        if plot_type == "scatter_3d":
            y_data = resolved["y_axis"][0]["data"] if resolved["y_axis"] else []
            z_data = resolved["z_axis"]["data"] if resolved["z_axis"] else []
            y_label = resolved["y_axis"][0]["label"] if resolved["y_axis"] else ""
            z_label = resolved["z_axis"]["label"] if resolved["z_axis"] else ""
            if x_data and y_data and z_data:
                self._plot_panel.scatter_3d(
                    plot_config, x_data, y_data, z_data, x_label, y_label, z_label
                )
                self.ui.resultLabel.setText(f"Scatter 3D: {len(x_data)} points")
            else:
                self.ui.statusLabel.setText("Error: Empty result data")
                return

        elif plot_type == "contour":
            mesh_data = resolved.get("mesh_data", {})
            x_mesh = mesh_data.get("x_i", [])
            y_mesh = mesh_data.get("x_j", [])
            z_mesh = mesh_data.get("Z_ABC", [])
            y_label = resolved["y_axis"][0]["label"] if resolved["y_axis"] else "x_j"
            if x_mesh and y_mesh and z_mesh:
                self._plot_panel.contourf(
                    plot_config, x_mesh, y_mesh, z_mesh, x_label, y_label
                )
                self.ui.resultLabel.setText("Contour plot")
            else:
                self.ui.statusLabel.setText("Error: Empty mesh data")
                return

        elif plot_type == "contour_triangular":
            values = resolved.get("values", [])
            if values:
                self._plot_panel.contour_triangular(plot_config, values)
                self.ui.resultLabel.setText("Triangular contour plot")
            else:
                self.ui.statusLabel.setText("Error: Empty values for triangular plot")
                return

        else:
            y_data = resolved["y_axis"][0]["data"] if resolved["y_axis"] else []
            y_label = resolved["y_axis"][0]["label"] if resolved["y_axis"] else ""
            is_collection = method_config.get("outputs", {}).get("is_collection", False)

            if not is_collection:
                if not x_data or not y_data:
                    self.ui.statusLabel.setText("Error: No result returned")
                    return
                x_val = x_data[0]
                y_val = y_data[0]
                self._plot_panel.plotSinglePoint(
                    plot_config, x_val, y_val, x_label, y_label
                )
                self.ui.resultLabel.setText(
                    f"{resolved['y_axis'][0]['key']} = {y_val:.4f} {resolved['y_axis'][0]['unit']}"
                    if resolved["y_axis"]
                    else ""
                )
            else:
                if not x_data or not y_data:
                    self.ui.statusLabel.setText("Error: Empty result data")
                    return
                self._plot_panel.plot(plot_config, x_data, y_data, x_label, y_label)

                y_min = min(y_data)
                idx_min = y_data.index(y_min)
                x_at_min = x_data[idx_min]
                self.ui.resultLabel.setText(
                    f"Min: {y_min:.4f} at {resolved['x_axis']['key']}={x_at_min:.2f}"
                )

        self._updateResultTable(result, resolved)

    def _updateResultTable(
        self,
        result: dict,
        resolved: dict,
    ) -> None:
        values = result.get("values", [])
        dims = resolved.get("dims", [])
        columns = dims.copy()
        data = []
        for v in values:
            row = [v.get(dim, "") for dim in dims]
            data.append(row)
        self._result_model.update(columns, data)

    def _retranslateUi(self) -> None:
        pass
