from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QComboBox,
    QGroupBox,
    QMessageBox,
)
from PySide6.QtCore import Signal


class HillertToopContourWizardDialog(QDialog):
    resultReady = Signal(dict)

    def __init__(self, module_service, user_db_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Hillert-Toop Contour Configuration"))
        self.setMinimumSize(500, 400)
        self._ms = module_service
        self._userDb = user_db_service
        self._sources = {"Z_AB": None, "Z_AC": None, "Z_BC": None}
        self._setupUi()

    def _setupUi(self):
        from ..data_source_discovery import BinaryDataSourceDiscovery

        self._discovery = BinaryDataSourceDiscovery(self._ms, self._userDb)

        from .wizard_pages import ElementSelectionPage

        mainLayout = QVBoxLayout(self)

        title = QLabel(self.tr("Hillert-Toop Contour Configuration"))
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        mainLayout.addWidget(title)

        self._elementPage = ElementSelectionPage()
        mainLayout.addWidget(self._elementPage)

        planeGroup = QGroupBox(self.tr("Projection Plane"))
        planeLayout = QVBoxLayout()
        self._planeCombo = QComboBox()
        self._planeCombo.addItems(["x_A-x_B", "x_A-x_C", "x_B-x_C"])
        planeLayout.addWidget(self._planeCombo)
        planeGroup.setLayout(planeLayout)
        mainLayout.addWidget(planeGroup)

        optionsGroup = QGroupBox(self.tr("Calculation Options"))
        optionsLayout = QVBoxLayout()
        self._nPointsLabel = QLabel(self.tr("Grid density (points per edge):"))
        self._nPointsSpin = QSpinBox()
        self._nPointsSpin.setRange(2, 1000)
        self._nPointsSpin.setValue(50)
        optionsLayout.addWidget(self._nPointsLabel)
        optionsLayout.addWidget(self._nPointsSpin)
        optionsGroup.setLayout(optionsLayout)
        mainLayout.addWidget(optionsGroup)

        mainLayout.addStretch()

        buttonLayout = QHBoxLayout()
        self._cancelBtn = QPushButton(self.tr("Cancel"))
        self._calcBtn = QPushButton(self.tr("Calculate"))

        buttonLayout.addWidget(self._cancelBtn)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self._calcBtn)

        mainLayout.addLayout(buttonLayout)

        self._cancelBtn.clicked.connect(self.reject)
        self._calcBtn.clicked.connect(self._onCalculate)

        self._elementPage.selectionChanged.connect(self._onElementsChanged)

        self._updateSources()

    def _updateSources(self):
        elemA, elemB, elemC = self._elementPage.getElements()

        sourcesAB = self._discovery.findSources("thermodynamic", elemA, elemB)
        sourcesAC = self._discovery.findSources("thermodynamic", elemA, elemC)
        sourcesBC = self._discovery.findSources("thermodynamic", elemB, elemC)

        if sourcesAB:
            self._sources["Z_AB"] = sourcesAB[0]
        if sourcesAC:
            self._sources["Z_AC"] = sourcesAC[0]
        if sourcesBC:
            self._sources["Z_BC"] = sourcesBC[0]

    def _onElementsChanged(self):
        self._updateSources()

    def _getOutputSymbolLatexUnit(self, source) -> tuple[str, str, str]:
        if source is None:
            return "", "", ""
        moduleName = source.source_name
        outputSymbol = source.output_symbol
        config = self._ms.getModuleConfig(moduleName)
        if not config:
            return "", "", ""
        moduleCfg = config.get("module", {})
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

    def _onCalculate(self):
        from ..hillert_toop_module import HillertToopCalc

        elemA, elemB, elemC = self._elementPage.getElements()
        nPoints = self._nPointsSpin.value()
        plane = self._planeCombo.currentText()

        hillert_toop = HillertToopCalc()

        xAList, xBList, xCList = hillert_toop._generateGrid(nPoints)

        zAbSource = self._sources["Z_AB"]
        zAcSource = self._sources["Z_AC"]
        zBcSource = self._sources["Z_BC"]

        if not zAbSource or not zAcSource or not zBcSource:
            QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr("Please ensure all data sources are available"),
            )
            return

        zABList = zAbSource.getValues(elemA, elemB, xAList)
        zACList = zAcSource.getValues(elemA, elemC, xAList)

        V_BC_list = [(1.0 + xB - xC) / 2.0 for xB, xC in zip(xBList, xCList)]
        zBCList = zBcSource.getValues(elemB, elemC, V_BC_list)

        zSymbol, zLatex, zUnit = self._getOutputSymbolLatexUnit(zAbSource)

        result = hillert_toop.calculateContourWithData(
            elemA,
            elemB,
            elemC,
            plane,
            nPoints,
            zABList,
            zACList,
            zBCList,
            zLatex,
            zUnit,
            zSymbol,
        )

        self._ms.cacheResult(
            "hillert_toop_module",
            "calculateContour",
            result,
            elem_A=elemA,
            elem_B=elemB,
            elem_C=elemC,
            plane=plane,
            n_points=nPoints,
        )

        self.resultReady.emit(result)
        self.accept()
