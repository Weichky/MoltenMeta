from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
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

        title = QLabel(
            self.tr("Select elements (A is solvent, B/C are exchange components)")
        )
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        form_layout = QVBoxLayout()

        self._elem_a_combo = QComboBox()
        self._elem_a_combo.addItems(ELEMENT_SYMBOLS)
        self._elem_a_combo.setCurrentText("Fe")
        elem_a_layout = QHBoxLayout()
        elem_a_layout.addWidget(QLabel(self.tr("Element A (solvent):")))
        elem_a_layout.addWidget(self._elem_a_combo)
        form_layout.addLayout(elem_a_layout)

        self._elem_b_combo = QComboBox()
        self._elem_b_combo.addItems(ELEMENT_SYMBOLS)
        self._elem_b_combo.setCurrentText("Cu")
        elem_b_layout = QHBoxLayout()
        elem_b_layout.addWidget(QLabel(self.tr("Element B (exchange 1):")))
        elem_b_layout.addWidget(self._elem_b_combo)
        form_layout.addLayout(elem_b_layout)

        self._elem_c_combo = QComboBox()
        self._elem_c_combo.addItems(ELEMENT_SYMBOLS)
        self._elem_c_combo.setCurrentText("Al")
        elem_c_layout = QHBoxLayout()
        elem_c_layout.addWidget(QLabel(self.tr("Element C (exchange 2):")))
        elem_c_layout.addWidget(self._elem_c_combo)
        form_layout.addLayout(elem_c_layout)

        layout.addLayout(form_layout)
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
