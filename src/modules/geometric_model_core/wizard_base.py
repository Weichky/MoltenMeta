"""
Abstract base classes for geometric model wizards.

Provides common wizard infrastructure for all geometric models (Kohler, Toop, Maggianu, Hillert-Toop).
Concrete implementations should inherit from GeometricModelWizardMixin and implement abstract methods.
"""

from abc import ABC, abstractmethod
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QComboBox,
    QGridLayout,
)
from PySide6.QtCore import Signal

from modules.element_map.element_map import ELEMENT_ID_TO_SYMBOL, elemSymbolToId

ELEMENT_SYMBOLS = list(ELEMENT_ID_TO_SYMBOL.values())


class StepIndicator(QWidget):
    """Simple step indicator for wizard dialogs."""

    def __init__(self, steps: list[str], parent=None):
        super().__init__(parent)
        self._steps = steps
        self._current = 0
        self._setupUi()

    def _setupUi(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        for i, step in enumerate(self._steps):
            circle = QLabel()
            circle.setFixedSize(12, 12)
            circle.setObjectName("stepCircle")
            layout.addWidget(circle)
            if i < len(self._steps) - 1:
                line = QLabel()
                line.setFixedHeight(2)
                line.setObjectName("stepLine")
                layout.addWidget(line)
        layout.addStretch()

    def setCurrentStep(self, step: int):
        self._current = step


class ElementSelectionPage(QWidget):
    """Widget for selecting three elements A, B, C."""

    selectionChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setupUi()

    def _setupUi(self):
        layout = QGridLayout(self)

        self._elemACombo = QComboBox()
        self._elemBCombo = QComboBox()
        self._elemCCombo = QComboBox()

        self._elemACombo.addItems(ELEMENT_SYMBOLS)
        self._elemACombo.setCurrentText("Fe")
        self._elemBCombo.addItems(ELEMENT_SYMBOLS)
        self._elemBCombo.setCurrentText("Cu")
        self._elemCCombo.addItems(ELEMENT_SYMBOLS)
        self._elemCCombo.setCurrentText("Al")

        layout.addWidget(QLabel(self.tr("Element A (solvent):")), 0, 0)
        layout.addWidget(self._elemACombo, 0, 1)
        layout.addWidget(QLabel(self.tr("Element B:")), 1, 0)
        layout.addWidget(self._elemBCombo, 1, 1)
        layout.addWidget(QLabel(self.tr("Element C:")), 2, 0)
        layout.addWidget(self._elemCCombo, 2, 1)

        self._elemACombo.currentIndexChanged.connect(
            lambda: self.selectionChanged.emit()
        )
        self._elemBCombo.currentIndexChanged.connect(
            lambda: self.selectionChanged.emit()
        )
        self._elemCCombo.currentIndexChanged.connect(
            lambda: self.selectionChanged.emit()
        )

    def getElements(self) -> tuple[int, int, int]:

        a = elemSymbolToId(self._elemACombo.currentText())
        b = elemSymbolToId(self._elemBCombo.currentText())
        c = elemSymbolToId(self._elemCCombo.currentText())
        return a, b, c


class GeometricModelWizardMixin(ABC):
    """Mixin class providing common wizard functionality for geometric models.

    Subclasses must implement:
    - getModelName() -> str
    - getModulePackage() -> str
    - createCalculator() -> object
    - getNormalizationType() -> str  # "w" for Kohler, "x" for Toop, "v" for Maggianu/HillertToop
    """

    resultReady = Signal(dict)

    @abstractmethod
    def getModelName(self) -> str:
        """Return display name of the model."""
        pass

    @abstractmethod
    def getModulePackage(self) -> str:
        """Return package name for cacheResult."""
        pass

    @abstractmethod
    def createCalculator(self):
        """Create and return the calculator instance."""
        pass

    @abstractmethod
    def getNormalizationType(self) -> str:
        """Return normalization type: 'w' (fraction), 'x' (direct), or 'v' (normalized)."""
        pass

    def _getNormalizationList(
        self, x_B_list: list, x_C_list: list, normalization_type: str
    ) -> list:
        """Generate normalization list based on type."""
        if normalization_type == "w":
            return [
                x_B / (x_B + x_C) if (x_B + x_C) > 0 else 0
                for x_B, x_C in zip(x_B_list, x_C_list)
            ]
        elif normalization_type == "v":
            return [(1.0 + x_B - x_C) / 2.0 for x_B, x_C in zip(x_B_list, x_C_list)]
        else:
            return x_B_list

    def _getOutputSymbolLatexUnit(self, source, module_service) -> tuple[str, str, str]:
        """Get output symbol, latex and unit from a data source."""
        if source is None:
            return "", "", ""
        moduleName = source.source_name
        if not moduleName:
            return "", "", ""
        outputSymbol = source.output_symbol
        config = module_service.getModuleConfig(moduleName)
        if not config:
            return "", "", ""
        moduleCfg = config.get("module")
        if moduleCfg is None:
            return "", "", ""
        allMethods = moduleCfg.get("all_methods", [])
        for methodName in allMethods:
            methodConfig = config.get(methodName, {})
            outputs = methodConfig.get("outputs", {})
            symbols = outputs.get("symbol", [])
            latexList = outputs.get("latex", [])
            units = outputs.get("unit", [])
            for i, sym in enumerate(symbols):
                if sym == outputSymbol:
                    latex = latexList.get(sym, "")
                    unit = units.get(sym, "")
                    return outputSymbol, latex, unit
        return "", "", ""


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

        contourLabel = QLabel(self.tr("Contour levels"))
        self._contourSpin = QSpinBox()
        self._contourSpin.setRange(10, 100)
        self._contourSpin.setValue(20)
        grid.addWidget(contourLabel, 1, 0)
        grid.addWidget(self._contourSpin, 1, 1)

        layout.addLayout(grid)
        layout.addStretch()

    def getNPoints(self) -> int:
        return self._nPointsSpin.value()

    def getContourPoints(self) -> int:
        return self._contourSpin.value()
