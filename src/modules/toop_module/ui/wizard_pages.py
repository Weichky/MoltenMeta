from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QSpinBox,
)
from PySide6.QtCore import Signal


ELEMENT_SYMBOLS = [
    "H",
    "He",
    "Li",
    "Be",
    "B",
    "C",
    "N",
    "O",
    "F",
    "Ne",
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "Ar",
    "K",
    "Ca",
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Ga",
    "Ge",
    "As",
    "Se",
    "Br",
    "Kr",
    "Rb",
    "Sr",
    "Y",
    "Zr",
    "Nb",
    "Mo",
    "Tc",
    "Ru",
    "Rh",
    "Pd",
    "Ag",
    "Cd",
    "In",
    "Sn",
    "Sb",
    "Te",
    "I",
    "Xe",
    "Cs",
    "Ba",
    "La",
    "Ce",
    "Pr",
    "Nd",
    "Pm",
    "Sm",
    "Eu",
    "Gd",
    "Tb",
    "Dy",
    "Ho",
    "Er",
    "Tm",
    "Yb",
    "Lu",
    "Hf",
    "Ta",
    "W",
    "Re",
    "Os",
    "Ir",
    "Pt",
    "Au",
    "Hg",
    "Tl",
    "Pb",
    "Bi",
    "Po",
    "At",
    "Rn",
    "Fr",
    "Ra",
    "Ac",
    "Th",
    "Pa",
    "U",
    "Np",
    "Pu",
    "Am",
    "Cm",
    "Bk",
    "Cf",
    "Es",
    "Fm",
]


class ElementSelectionPage(QWidget):
    selectionChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(32, 32, 32, 32)

        title = QLabel(self.tr("Element Selection"))
        title.setObjectName("wizardTitle")
        layout.addWidget(title)

        description = QLabel(
            self.tr(
                "Select elements for the ternary system. Element A is the solvent, B and C are exchange components."
            )
        )
        description.setObjectName("wizardDescription")
        description.setWordWrap(True)
        layout.addWidget(description)

        grid = QGridLayout()
        grid.setSpacing(16)

        elem_a_label = QLabel(self.tr("Element A (solvent)"))
        self._elem_a_combo = QComboBox()
        self._elem_a_combo.addItems(ELEMENT_SYMBOLS)
        self._elem_a_combo.setCurrentText("Fe")
        grid.addWidget(elem_a_label, 0, 0)
        grid.addWidget(self._elem_a_combo, 0, 1)

        elem_b_label = QLabel(self.tr("Element B (exchange 1)"))
        self._elem_b_combo = QComboBox()
        self._elem_b_combo.addItems(ELEMENT_SYMBOLS)
        self._elem_b_combo.setCurrentText("Cu")
        grid.addWidget(elem_b_label, 1, 0)
        grid.addWidget(self._elem_b_combo, 1, 1)

        elem_c_label = QLabel(self.tr("Element C (exchange 2)"))
        self._elem_c_combo = QComboBox()
        self._elem_c_combo.addItems(ELEMENT_SYMBOLS)
        self._elem_c_combo.setCurrentText("Al")
        grid.addWidget(elem_c_label, 2, 0)
        grid.addWidget(self._elem_c_combo, 2, 1)

        layout.addLayout(grid)
        layout.addStretch()

        self._elem_a_combo.currentIndexChanged.connect(self.selectionChanged)
        self._elem_b_combo.currentIndexChanged.connect(self.selectionChanged)
        self._elem_c_combo.currentIndexChanged.connect(self.selectionChanged)

    def get_element_a(self) -> int:
        return ELEMENT_SYMBOLS.index(self._elem_a_combo.currentText()) + 1

    def get_element_b(self) -> int:
        return ELEMENT_SYMBOLS.index(self._elem_b_combo.currentText()) + 1

    def get_element_c(self) -> int:
        return ELEMENT_SYMBOLS.index(self._elem_c_combo.currentText()) + 1

    def get_elements(self) -> tuple[int, int, int]:
        return self.get_element_a(), self.get_element_b(), self.get_element_c()


class DataSourceSelectionPage(QWidget):
    selectionChanged = Signal()

    def __init__(self, title: str, source_key: str, parent=None):
        super().__init__(parent)
        self._title = title
        self._source_key = source_key
        self._sources = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(32, 32, 32, 32)

        title = QLabel(self._title)
        title.setObjectName("wizardTitle")
        layout.addWidget(title)

        description = QLabel(
            self.tr("Select the thermodynamic data source for this binary system.")
        )
        description.setObjectName("wizardDescription")
        description.setWordWrap(True)
        layout.addWidget(description)

        self._source_combo = QComboBox()
        self._source_combo.currentIndexChanged.connect(self.selectionChanged)
        layout.addWidget(self._source_combo)

        layout.addStretch()

    def set_sources(self, sources: list):
        self._sources = sources or []
        self._source_combo.clear()
        if self._sources:
            for source in self._sources:
                self._source_combo.addItem(source.display_name, source)
        else:
            self._source_combo.addItem(self.tr("No sources available"), None)

    def get_selected_source(self):
        idx = self._source_combo.currentIndex()
        if idx >= 0:
            return self._source_combo.itemData(idx)
        return None


class CalculationOptionsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(32, 32, 32, 32)

        title = QLabel(self.tr("Calculation Options"))
        title.setObjectName("wizardTitle")
        layout.addWidget(title)

        description = QLabel(
            self.tr("Configure the calculation parameters for the ternary system.")
        )
        description.setObjectName("wizardDescription")
        description.setWordWrap(True)
        layout.addWidget(description)

        grid = QGridLayout()
        grid.setSpacing(16)

        n_points_label = QLabel(self.tr("Grid points per dimension"))
        self._n_points_spin = QSpinBox()
        self._n_points_spin.setRange(5, 100)
        self._n_points_spin.setValue(21)
        grid.addWidget(n_points_label, 0, 0)
        grid.addWidget(self._n_points_spin, 0, 1)

        contour_label = QLabel(self.tr("Contour levels"))
        self._contour_spin = QSpinBox()
        self._contour_spin.setRange(10, 100)
        self._contour_spin.setValue(20)
        grid.addWidget(contour_label, 1, 0)
        grid.addWidget(self._contour_spin, 1, 1)

        layout.addLayout(grid)
        layout.addStretch()

    def get_n_points(self) -> int:
        return self._n_points_spin.value()

    def get_contour_points(self) -> int:
        return self._contour_spin.value()
