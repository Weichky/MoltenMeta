from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QMessageBox,
)
from PySide6.QtCore import Signal


class ToopWizardDialog(QDialog):
    resultReady = Signal(dict)

    def __init__(self, module_service, user_db_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Toop 模型配置"))
        self.setMinimumSize(500, 400)
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

        title = QLabel(self.tr("Toop 模型配置"))
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        main_layout.addWidget(title)

        self._stacked = QStackedWidget()
        main_layout.addWidget(self._stacked)

        self._element_page = ElementSelectionPage()
        self._stacked.addWidget(self._element_page)

        self._z_ab_page = DataSourceSelectionPage(
            self.tr("Z_AB 数据源 (A-B 二元系)"), "Z_AB"
        )
        self._z_ac_page = DataSourceSelectionPage(
            self.tr("Z_AC 数据源 (A-C 二元系)"), "Z_AC"
        )
        self._z_bc_page = DataSourceSelectionPage(
            self.tr("Z_BC 数据源 (B-C 二元系)"), "Z_BC"
        )
        self._options_page = CalculationOptionsPage()

        self._stacked.addWidget(self._z_ab_page)
        self._stacked.addWidget(self._z_ac_page)
        self._stacked.addWidget(self._z_bc_page)
        self._stacked.addWidget(self._options_page)

        button_layout = QHBoxLayout()
        self._cancel_btn = QPushButton(self.tr("取消"))
        self._prev_btn = QPushButton(self.tr("上一步"))
        self._next_btn = QPushButton(self.tr("下一步"))
        self._calc_btn = QPushButton(self.tr("计算"))

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

        sources_ab = self._discovery.find_sources("thermodynamic", elem_a, elem_b)
        sources_ac = self._discovery.find_sources("thermodynamic", elem_a, elem_c)
        sources_bc = self._discovery.find_sources("thermodynamic", elem_b, elem_c)

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
                self.tr("警告"),
                self.tr("请为所有数据源选择数据源"),
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

    def calculate(self, inputs: dict) -> dict:
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

        result = toop.calculateScatterWithData(
            elem_a, elem_b, elem_c, n_points, Z_AB_list, Z_AC_list, Z_BC_list
        )

        return result
