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


class MaggianuScatterWizardDialog(QDialog):
    resultReady = Signal(dict)

    def __init__(self, module_service, user_db_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Maggianu 3D Scatter Configuration"))
        self.setMinimumSize(500, 400)
        self._ms = module_service
        self._userDb = user_db_service
        self._sources = {"Z_AB": None, "Z_BC": None, "Z_AC": None}
        self._setupUi()

    def _setupUi(self):
        from ..data_source_discovery import MaggianuDataSourceDiscovery

        self._discovery = MaggianuDataSourceDiscovery(
            self._ms, self._userDb, self._ms.getDataSourceRegistry()
        )

        from .wizard_pages import ElementSelectionPage

        mainLayout = QVBoxLayout(self)

        title = QLabel(self.tr("Maggianu 3D Scatter Configuration"))
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        mainLayout.addWidget(title)

        self._elementPage = ElementSelectionPage()
        mainLayout.addWidget(self._elementPage)

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
        sourcesBC = self._discovery.findSources("thermodynamic", elemB, elemC)
        sourcesAC = self._discovery.findSources("thermodynamic", elemA, elemC)

        if sourcesAB:
            self._sources["Z_AB"] = sourcesAB[0]
        if sourcesBC:
            self._sources["Z_BC"] = sourcesBC[0]
        if sourcesAC:
            self._sources["Z_AC"] = sourcesAC[0]

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

    def _onCalculate(self):
        from ..maggianu_module import MaggianuCalc

        elemA, elemB, elemC = self._elementPage.getElements()
        nPoints = self._nPointsSpin.value()

        maggianu = MaggianuCalc()

        xAList, xBList, xCList = maggianu._generateGrid(nPoints)

        zAbSource = self._sources["Z_AB"]
        zBcSource = self._sources["Z_BC"]
        zAcSource = self._sources["Z_AC"]

        if not zAbSource or not zBcSource or not zAcSource:
            QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr("Please ensure all data sources are available"),
            )
            return

        V_AB_list = [(1.0 + xA - xB) / 2.0 for xA, xB in zip(xAList, xBList)]
        zABList = zAbSource.getValues(elemA, elemB, V_AB_list)

        V_BC_list = [(1.0 + xB - xC) / 2.0 for xB, xC in zip(xBList, xCList)]
        zBCList = zBcSource.getValues(elemB, elemC, V_BC_list)

        V_AC_list = [(1.0 + xA - xC) / 2.0 for xA, xC in zip(xAList, xCList)]
        zACList = zAcSource.getValues(elemA, elemC, V_AC_list)

        zSymbol, zLatex, zUnit = self._getOutputSymbolLatexUnit(zAbSource)

        result = maggianu.calculateScatterWithData(
            elemA,
            elemB,
            elemC,
            nPoints,
            zABList,
            zACList,
            zBCList,
            zLatex,
            zUnit,
            zSymbol,
        )

        self._ms.cacheResult(
            "maggianu_module",
            "calculateScatter",
            result,
            elem_A=elemA,
            elem_B=elemB,
            elem_C=elemC,
            n_points=nPoints,
        )

        self.resultReady.emit(result)
        self.accept()
