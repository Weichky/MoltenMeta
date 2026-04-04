from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt


from .ui import UiSimulationPage
from .controller import SimulationController
from .plot_panel import PlotPanel


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
        self._controller = SimulationController(context)

        self._current_category: str = ""
        self._current_module: str = ""
        self._current_method: str = ""

        self.ui = UiSimulationPage()
        self.ui.setupUi(self)

        self._plot_panel = PlotPanel()
        self.ui.plotContainer.addWidget(self._plot_panel)

        self._result_model = ResultTableModel()
        self.ui.resultTable.setModel(self._result_model)
        self.ui.resultTable.horizontalHeader().setStretchLastSection(True)

        self._connectSignals()
        self._populateCategories()

    def _connectSignals(self) -> None:
        self.ui.categoryCombo.currentIndexChanged.connect(self._onCategoryChanged)
        self.ui.moduleCombo.currentIndexChanged.connect(self._onModuleChanged)
        self.ui.methodCombo.currentIndexChanged.connect(self._onMethodChanged)
        self.ui.configureBtn.clicked.connect(self._onConfigureClicked)
        self.ui.calculateBtn.clicked.connect(self._onCalculateClicked)
        self._i18n.language_changed.connect(self._retranslateUi)

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

    def _onConfigureClicked(self) -> None:
        if not self._current_module or not self._current_method:
            return
        accepted, inputs = self._controller.showInputDialog(self._current_method, self)
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

    def _displayResult(self, result: dict) -> None:
        config = self._controller.getCurrentConfig()
        method_config = config.get(self._current_method, {})
        plot_config = method_config.get("plot", {})
        latex = result.get("latex", {})
        unit = result.get("unit", {})
        values = result.get("values", [])

        x_key = plot_config.get("x", "x_A")
        y_keys = plot_config.get("y", ["Delta_H_mix"])
        title = plot_config.get("title", "")

        x_label = latex.get(x_key, x_key)
        if unit.get(x_key):
            x_label += f" ({unit[x_key]})"

        y_label = latex.get(y_keys[0], y_keys[0])
        if unit.get(y_keys[0]):
            y_label += f" ({unit[y_keys[0]]})"

        is_collection = method_config.get("outputs", {}).get("is_collection", False)

        if not is_collection:
            x_val = values[0].get(x_key, 0)
            y_val = values[0].get(y_keys[0], 0)
            self._plot_panel.plotSinglePoint(x_val, y_val, x_label, y_label, title)
            self.ui.resultLabel.setText(
                f"{y_keys[0]} = {y_val:.4f} {unit.get(y_keys[0], '')}"
            )
        else:
            x_data = [v.get(x_key, 0) for v in values]
            y_data = [v.get(y_keys[0], 0) for v in values]
            self._plot_panel.plot(x_data, y_data, x_label, y_label, title)

            y_min = min(y_data)
            idx_min = y_data.index(y_min)
            x_at_min = x_data[idx_min]
            self.ui.resultLabel.setText(f"Min: {y_min:.4f} at {x_key}={x_at_min:.2f}")

        self._updateResultTable(values, x_key, y_keys)

    def _updateResultTable(
        self,
        values: list[dict],
        x_key: str,
        y_keys: list[str],
    ) -> None:
        columns = [x_key]
        columns.extend(y_keys)
        data = []
        for v in values:
            row = [v.get(x_key, "")]
            for y_key in y_keys:
                row.append(v.get(y_key, ""))
            data.append(row)
        self._result_model.update(columns, data)

    def _retranslateUi(self) -> None:
        pass
