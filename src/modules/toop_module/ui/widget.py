from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QMessageBox,
    QWidget,
)
from PySide6.QtCore import Signal


class StepIndicator(QWidget):
    def __init__(self, steps: list[str], parent=None):
        super().__init__(parent)
        self._steps = steps
        self._current = 0
        self._circles = []
        self._lines = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        for i, step in enumerate(self._steps):
            circle = QLabel()
            circle.setFixedSize(12, 12)
            circle.setObjectName("stepCircle")
            self._circles.append(circle)
            layout.addWidget(circle)

            if i < len(self._steps) - 1:
                line = QLabel()
                line.setFixedHeight(2)
                line.setObjectName("stepLine")
                self._lines.append(line)
                layout.addWidget(line)

        layout.addStretch()

    def setCurrentStep(self, step: int):
        self._current = step

    def _updateStyles(self):
        pass


class ToopWizardDialog(QDialog):
    resultReady = Signal(dict)

    def __init__(self, module_service, user_db_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Toop Model Configuration"))
        self.setMinimumSize(600, 500)
        self._ms = module_service
        self._user_db = user_db_service
        self._sources = {"Z_AB": None, "Z_AC": None, "Z_BC": None}
        self._setup_ui()

    def _setup_ui(self):
        from ..data_source_discovery import ToopDataSourceDiscovery

        self._discovery = ToopDataSourceDiscovery(self._ms, self._user_db)

        from .wizard_pages import (
            ElementSelectionPage,
            DataSourceSelectionPage,
            CalculationOptionsPage,
        )

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(32, 32, 32, 32)

        title = QLabel(self.tr("Toop Model Configuration"))
        title.setObjectName("wizardTitle")
        main_layout.addWidget(title)

        self._step_indicator = StepIndicator(
            [
                self.tr("Elements"),
                self.tr("Z_AB"),
                self.tr("Z_AC"),
                self.tr("Z_BC"),
                self.tr("Options"),
            ]
        )
        main_layout.addWidget(self._step_indicator)

        self._stacked = QStackedWidget()
        main_layout.addWidget(self._stacked)

        self._element_page = ElementSelectionPage()
        self._stacked.addWidget(self._element_page)

        self._z_ab_page = DataSourceSelectionPage(self.tr("Z_AB Data Source"), "Z_AB")
        self._z_ac_page = DataSourceSelectionPage(self.tr("Z_AC Data Source"), "Z_AC")
        self._z_bc_page = DataSourceSelectionPage(self.tr("Z_BC Data Source"), "Z_BC")
        self._options_page = CalculationOptionsPage()

        self._stacked.addWidget(self._z_ab_page)
        self._stacked.addWidget(self._z_ac_page)
        self._stacked.addWidget(self._z_bc_page)
        self._stacked.addWidget(self._options_page)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)

        self._cancel_btn = QPushButton(self.tr("Cancel"))
        self._cancel_btn.setObjectName("secondary")
        self._prev_btn = QPushButton(self.tr("Previous"))
        self._prev_btn.setObjectName("secondary")
        self._next_btn = QPushButton(self.tr("Next"))
        self._next_btn.setObjectName("primary")
        self._calc_btn = QPushButton(self.tr("Calculate"))
        self._calc_btn.setObjectName("primary")

        self._prev_btn.setEnabled(False)
        self._calc_btn.setVisible(False)

        button_layout.addWidget(self._cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self._prev_btn)
        button_layout.addWidget(self._next_btn)
        button_layout.addWidget(self._calc_btn)

        main_layout.addLayout(button_layout)

        self._cancel_btn.clicked.connect(self.reject)
        self._prev_btn.clicked.connect(self._on_prev)
        self._next_btn.clicked.connect(self._on_next)
        self._calc_btn.clicked.connect(self._on_calculate)

        self._element_page.selectionChanged.connect(self._on_elements_changed)
        self._z_ab_page.selectionChanged.connect(self._on_z_ab_changed)
        self._z_ac_page.selectionChanged.connect(self._on_z_ac_changed)
        self._z_bc_page.selectionChanged.connect(self._on_z_bc_changed)

        self._current_step = 0
        self._update_sources()

    def _update_sources(self):
        elem_a, elem_b, elem_c = self._element_page.get_elements()

        sources_ab = self._discovery.findSources("thermodynamic", elem_a, elem_b)
        sources_ac = self._discovery.findSources("thermodynamic", elem_a, elem_c)
        sources_bc = self._discovery.findSources("thermodynamic", elem_b, elem_c)

        self._z_ab_page.set_sources(sources_ab)
        self._z_ac_page.set_sources(sources_ac)
        self._z_bc_page.set_sources(sources_bc)

        if sources_ab:
            self._sources["Z_AB"] = sources_ab[0]
        if sources_ac:
            self._sources["Z_AC"] = sources_ac[0]
        if sources_bc:
            self._sources["Z_BC"] = sources_bc[0]

    def _on_elements_changed(self):
        self._update_sources()

    def _on_z_ab_changed(self):
        self._sources["Z_AB"] = self._z_ab_page.get_selected_source()

    def _on_z_ac_changed(self):
        self._sources["Z_AC"] = self._z_ac_page.get_selected_source()

    def _on_z_bc_changed(self):
        self._sources["Z_BC"] = self._z_bc_page.get_selected_source()

    def _on_prev(self):
        if self._current_step > 0:
            self._current_step -= 1
            self._stacked.setCurrentIndex(self._current_step)
            self._update_buttons()

    def _on_next(self):
        if self._current_step < 4:
            self._current_step += 1
            self._stacked.setCurrentIndex(self._current_step)
            self._update_buttons()

    def _update_buttons(self):
        self._prev_btn.setEnabled(self._current_step > 0)
        self._next_btn.setVisible(self._current_step < 4)
        self._calc_btn.setVisible(self._current_step == 4)

    def _on_calculate(self):
        if (
            not self._sources["Z_AB"]
            or not self._sources["Z_AC"]
            or not self._sources["Z_BC"]
        ):
            QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr("Please select data sources for all inputs"),
            )
            return

        result = self.calculate(self.getInputs())
        self.resultReady.emit(result)
        self.accept()

    def getInputs(self) -> dict:
        elem_a, elem_b, elem_c = self._element_page.get_elements()
        return {
            "elem_A": elem_a,
            "elem_B": elem_b,
            "elem_C": elem_c,
            "n_points": self._options_page.get_n_points(),
            "contour_points": self._options_page.get_contour_points(),
            "sources": self._sources.copy(),
        }

    def _getOutputSymbolLatexUnit(self, source) -> tuple[str, str, str]:
        """Query symbol, latex and unit for a DataSource by resolving its output symbol against module config."""
        if source is None:
            return "", "", ""
        module_name = source.source_name
        output_symbol = source.output_symbol
        config = self._ms.getModuleConfig(module_name)
        if not config:
            return "", "", ""
        module_cfg = config.get("module", {})
        all_methods = module_cfg.get("all_methods", [])
        for method_name in all_methods:
            method_config = config.get(method_name, {})
            outputs = method_config.get("outputs", {})
            symbols = outputs.get("symbol", [])
            latex_list = outputs.get("latex", [])
            units = outputs.get("unit", [])
            for i, sym in enumerate(symbols):
                if sym == output_symbol:
                    latex = latex_list.get(sym, "")
                    unit = units.get(sym, "")
                    return output_symbol, latex, unit
        return "", "", ""

    def calculate(self, inputs: dict) -> dict:
        """Execute Toop calculation using provided binary data sources."""
        from ..toop_module import ToopCalc

        elem_a = inputs["elem_A"]
        elem_b = inputs["elem_B"]
        elem_c = inputs["elem_C"]
        n_points = inputs["n_points"]
        sources = inputs["sources"]

        toop = ToopCalc()

        x_A_list = []
        x_B_list = []
        x_C_list = []
        for i in range(n_points):
            for j in range(n_points - i):
                x_A = i / (n_points - 1) if n_points > 1 else 0
                x_B = j / (n_points - 1) if n_points > 1 else 0
                x_C = 1 - x_A - x_B
                x_A_list.append(x_A)
                x_B_list.append(x_B)
                x_C_list.append(x_C)

        Z_AB_source = sources["Z_AB"]
        Z_AC_source = sources["Z_AC"]
        Z_BC_source = sources["Z_BC"]

        Z_AB_list = Z_AB_source.get_values(elem_a, elem_b, x_A_list)
        Z_AC_list = Z_AC_source.get_values(elem_a, elem_c, x_A_list)

        w_B_list = [
            x_B / (x_B + x_C) if (x_B + x_C) > 0 else 0
            for x_B, x_C in zip(x_B_list, x_C_list)
        ]
        Z_BC_list = Z_BC_source.get_values(elem_b, elem_c, w_B_list)

        z_symbol, z_latex, z_unit = self._getOutputSymbolLatexUnit(Z_AB_source)

        result = toop.calculateScatterWithData(
            elem_a,
            elem_b,
            elem_c,
            n_points,
            Z_AB_list,
            Z_AC_list,
            Z_BC_list,
            z_latex,
            z_unit,
            z_symbol,
        )

        self._ms.cacheResult(
            "toop_module",
            "calculateScatter",
            result,
            elem_A=elem_a,
            elem_B=elem_b,
            elem_C=elem_c,
            n_points=n_points,
        )

        return result
