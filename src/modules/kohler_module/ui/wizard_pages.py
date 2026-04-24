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
        self._setupUi()

    def _setupUi(self):
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
        self._elemACombo = QComboBox()
        self._elemACombo.addItems(ELEMENT_SYMBOLS)
        self._elemACombo.setCurrentText("Fe")
        grid.addWidget(elem_a_label, 0, 0)
        grid.addWidget(self._elemACombo, 0, 1)

        elem_b_label = QLabel(self.tr("Element B (exchange 1)"))
        self._elemBCombo = QComboBox()
        self._elemBCombo.addItems(ELEMENT_SYMBOLS)
        self._elemBCombo.setCurrentText("Cu")
        grid.addWidget(elem_b_label, 1, 0)
        grid.addWidget(self._elemBCombo, 1, 1)

        elem_c_label = QLabel(self.tr("Element C (exchange 2)"))
        self._elemCCombo = QComboBox()
        self._elemCCombo.addItems(ELEMENT_SYMBOLS)
        self._elemCCombo.setCurrentText("Al")
        grid.addWidget(elem_c_label, 2, 0)
        grid.addWidget(self._elemCCombo, 2, 1)

        layout.addLayout(grid)
        layout.addStretch()

        self._elemACombo.currentIndexChanged.connect(self.selectionChanged)
        self._elemBCombo.currentIndexChanged.connect(self.selectionChanged)
        self._elemCCombo.currentIndexChanged.connect(self.selectionChanged)

    def getElementA(self) -> int:
        return ELEMENT_SYMBOLS.index(self._elemACombo.currentText()) + 1

    def getElementB(self) -> int:
        return ELEMENT_SYMBOLS.index(self._elemBCombo.currentText()) + 1

    def getElementC(self) -> int:
        return ELEMENT_SYMBOLS.index(self._elemCCombo.currentText()) + 1

    def getElements(self) -> tuple[int, int, int]:
        return self.getElementA(), self.getElementB(), self.getElementC()


class DataSourceSelectionPage(QWidget):
    selectionChanged = Signal()

    def __init__(self, title: str, source_key: str, parent=None):
        super().__init__(parent)
        self._title = title
        self._sourceKey = source_key
        self._sources = []
        self._setupUi()

    def _setupUi(self):
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

        self._sourceCombo = QComboBox()
        self._sourceCombo.currentIndexChanged.connect(self.selectionChanged)
        layout.addWidget(self._sourceCombo)

        layout.addStretch()

    def setSources(self, sources: list):
        self._sources = sources or []
        self._sourceCombo.clear()
        if self._sources:
            for source in self._sources:
                self._sourceCombo.addItem(source.display_name, source)
        else:
            self._sourceCombo.addItem(self.tr("No sources available"), None)

    def getSelectedSource(self):
        idx = self._sourceCombo.currentIndex()
        if idx >= 0:
            return self._sourceCombo.itemData(idx)
        return None


class CalculationOptionsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setupUi()

    def _setupUi(self):
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

        layout.addSpacing(12)

        grid = QGridLayout()
        grid.setSpacing(16)

        nPointsLabel = QLabel(self.tr("Grid points per dimension"))
        self._nPointsSpin = QSpinBox()
        self._nPointsSpin.setRange(5, 100)
        self._nPointsSpin.setValue(21)
        grid.addWidget(nPointsLabel, 0, 0)
        grid.addWidget(self._nPointsSpin, 0, 1)

        contour_label = QLabel(self.tr("Contour levels"))
        self._contourSpin = QSpinBox()
        self._contourSpin.setRange(10, 100)
        self._contourSpin.setValue(20)
        grid.addWidget(contour_label, 1, 0)
        grid.addWidget(self._contourSpin, 1, 1)

        layout.addLayout(grid)
        layout.addStretch()

    def getNPoints(self) -> int:
        return self._nPointsSpin.value()

    def getContourPoints(self) -> int:
        return self._contourSpin.value()
