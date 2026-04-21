from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QGroupBox,
    QMessageBox,
)
from PySide6.QtCore import Signal


class ToopScatterWizardDialog(QDialog):
    resultReady = Signal(dict)

    def __init__(self, module_service, user_db_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Toop 3D Scatter Configuration"))
        self.setMinimumSize(500, 400)
        self._ms = module_service
        self._user_db = user_db_service
        self._sources = {"Z_AB": None, "Z_AC": None, "Z_BC": None}
        self._setup_ui()

    def _setup_ui(self):
        from ..data_source_discovery import ToopDataSourceDiscovery

        self._discovery = ToopDataSourceDiscovery(self._ms, self._user_db)

        from .wizard_pages import ElementSelectionPage

        main_layout = QVBoxLayout(self)

        title = QLabel(self.tr("Toop 3D Scatter Configuration"))
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        main_layout.addWidget(title)

        self._element_page = ElementSelectionPage()
        main_layout.addWidget(self._element_page)

        options_group = QGroupBox(self.tr("Calculation Options"))
        options_layout = QVBoxLayout()
        self._n_points_label = QLabel(self.tr("Grid density (points per edge):"))
        self._n_points_spin = QSpinBox()
        self._n_points_spin.setRange(2, 1000)
        self._n_points_spin.setValue(50)
        options_layout.addWidget(self._n_points_label)
        options_layout.addWidget(self._n_points_spin)
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        main_layout.addStretch()

        button_layout = QHBoxLayout()
        self._cancel_btn = QPushButton(self.tr("Cancel"))
        self._calc_btn = QPushButton(self.tr("Calculate"))

        button_layout.addWidget(self._cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self._calc_btn)

        main_layout.addLayout(button_layout)

        self._cancel_btn.clicked.connect(self.reject)
        self._calc_btn.clicked.connect(self._on_calculate)

        self._element_page.selectionChanged.connect(self._on_elements_changed)

        self._update_sources()

    def _update_sources(self):
        elem_a, elem_b, elem_c = self._element_page.get_elements()

        sources_ab = self._discovery.findSources("thermodynamic", elem_a, elem_b)
        sources_ac = self._discovery.findSources("thermodynamic", elem_a, elem_c)
        sources_bc = self._discovery.findSources("thermodynamic", elem_b, elem_c)

        if sources_ab:
            self._sources["Z_AB"] = sources_ab[0]
        if sources_ac:
            self._sources["Z_AC"] = sources_ac[0]
        if sources_bc:
            self._sources["Z_BC"] = sources_bc[0]

    def _on_elements_changed(self):
        self._update_sources()

    def _getOutputLatexUnit(self, source) -> tuple[str, str]:
        if source is None:
            return "", ""
        module_name = source.source_name
        output_symbol = source.output_symbol
        config = self._ms.getModuleConfig(module_name)
        if not config:
            return "", ""
        module_cfg = config.get("module")
        if module_cfg is None:
            return "", ""
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
                    return latex, unit
        return "", ""

    def _on_calculate(self):
        """Gather inputs and invoke Toop scatter calculation."""
        from ..toop_module import ToopCalc

        elem_a, elem_b, elem_c = self._element_page.get_elements()
        n_points = self._n_points_spin.value()

        toop = ToopCalc()

        x_A_list, x_B_list, x_C_list = toop._generateGrid(n_points)

        Z_AB_source = self._sources["Z_AB"]
        Z_AC_source = self._sources["Z_AC"]
        Z_BC_source = self._sources["Z_BC"]

        if not Z_AB_source or not Z_AC_source or not Z_BC_source:
            QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr("Please ensure all data sources are available"),
            )
            return

        Z_AB_list = Z_AB_source.get_values(elem_a, elem_b, x_A_list)
        Z_AC_list = Z_AC_source.get_values(elem_a, elem_c, x_A_list)

        w_B_list = [
            x_B / (x_B + x_C) if (x_B + x_C) > 0 else 0
            for x_B, x_C in zip(x_B_list, x_C_list)
        ]
        Z_BC_list = Z_BC_source.get_values(elem_b, elem_c, w_B_list)

        z_latex, z_unit = self._getOutputLatexUnit(Z_AB_source)

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
        )

        self.resultReady.emit(result)
        self.accept()
