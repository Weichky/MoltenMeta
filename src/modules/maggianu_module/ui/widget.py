from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
)
from PySide6.QtCore import Signal

from ...geometric_model_core import (
    StepIndicator,
    ElementSelectionPage,
    DataSourceSelectionPage,
    CalculationOptionsPage,
)


class MaggianuWizardDialog(QDialog):
    resultReady = Signal(dict)

    def __init__(self, module_service, user_db_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Maggianu Model Configuration"))
        self.setMinimumSize(600, 500)
        self._ms = module_service
        self._userDb = user_db_service
        self._sources = {"Z_AB": None, "Z_BC": None, "Z_AC": None}
        self._setupUi()

    def _setupUi(self):
        from ..data_source_discovery import MaggianuDataSourceDiscovery

        self._discovery = MaggianuDataSourceDiscovery(self._ms, self._userDb)

        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(24)
        mainLayout.setContentsMargins(32, 32, 32, 32)

        title = QLabel(self.tr("Maggianu Model Configuration"))
        title.setObjectName("wizardTitle")
        mainLayout.addWidget(title)

        self._stepIndicator = StepIndicator(
            [
                self.tr("Elements"),
                self.tr("Z_AB"),
                self.tr("Z_BC"),
                self.tr("Z_AC"),
                self.tr("Options"),
            ]
        )
        mainLayout.addWidget(self._stepIndicator)

        self._stacked = QStackedWidget()
        mainLayout.addWidget(self._stacked)

        self._elementPage = ElementSelectionPage()
        self._stacked.addWidget(self._elementPage)

        self._zAbPage = DataSourceSelectionPage(self.tr("Z_AB Data Source"), "Z_AB")
        self._zBcPage = DataSourceSelectionPage(self.tr("Z_BC Data Source"), "Z_BC")
        self._zAcPage = DataSourceSelectionPage(self.tr("Z_AC Data Source"), "Z_AC")
        self._optionsPage = CalculationOptionsPage()

        self._stacked.addWidget(self._zAbPage)
        self._stacked.addWidget(self._zBcPage)
        self._stacked.addWidget(self._zAcPage)
        self._stacked.addWidget(self._optionsPage)

        buttonLayout = QHBoxLayout()
        self._backBtn = QPushButton(self.tr("Back"))
        self._nextBtn = QPushButton(self.tr("Next"))
        self._cancelBtn = QPushButton(self.tr("Cancel"))

        buttonLayout.addWidget(self._backBtn)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self._cancelBtn)
        buttonLayout.addWidget(self._nextBtn)

        mainLayout.addLayout(buttonLayout)

        self._backBtn.clicked.connect(self._onBack)
        self._nextBtn.clicked.connect(self._onNext)
        self._cancelBtn.clicked.connect(self.reject)

        self._elementPage.selectionChanged.connect(self._onElementsChanged)
        self._updateNavigation()

    def _updateNavigation(self):
        current = self._stacked.currentIndex()
        self._backBtn.setEnabled(current > 0)

        if current == self._stacked.count() - 1:
            self._nextBtn.setText(self.tr("Calculate"))
        else:
            self._nextBtn.setText(self.tr("Next"))

    def _onBack(self):
        current = self._stacked.currentIndex()
        if current > 0:
            self._stacked.setCurrentIndex(current - 1)
            self._updateNavigation()

    def _onNext(self):
        current = self._stacked.currentIndex()
        if current < self._stacked.count() - 1:
            self._stacked.setCurrentIndex(current + 1)
            self._updateNavigation()
        else:
            self._calculate()

    def _onElementsChanged(self):
        self._updateSources()
        self._updatePageSources()

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

    def _updatePageSources(self):
        self._zAbPage.setSources(
            [self._sources["Z_AB"]] if self._sources["Z_AB"] else []
        )
        self._zBcPage.setSources(
            [self._sources["Z_BC"]] if self._sources["Z_BC"] else []
        )
        self._zAcPage.setSources(
            [self._sources["Z_AC"]] if self._sources["Z_AC"] else []
        )

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

    def calculate(self, inputs: dict) -> dict:
        from ..maggianu_module import MaggianuCalc

        elemA = inputs["elem_A"]
        elemB = inputs["elem_B"]
        elemC = inputs["elem_C"]
        nPoints = inputs["n_points"]
        sources = inputs["sources"]

        maggianu = MaggianuCalc()

        xAList = []
        xBList = []
        xCList = []
        for i in range(nPoints):
            for j in range(nPoints - i):
                xA = i / (nPoints - 1) if nPoints > 1 else 0
                xB = j / (nPoints - 1) if nPoints > 1 else 0
                xC = 1 - xA - xB
                xAList.append(xA)
                xBList.append(xB)
                xCList.append(xC)

        zAbSource = sources["Z_AB"]
        zBcSource = sources["Z_BC"]
        zAcSource = sources["Z_AC"]

        V_AB_list = [(1.0 + xA - xB) / 2.0 for xA, xB in zip(xAList, xBList)]
        zABList = zAbSource.get_values(elemA, elemB, V_AB_list)

        V_BC_list = [(1.0 + xB - xC) / 2.0 for xB, xC in zip(xBList, xCList)]
        zBCList = zBcSource.get_values(elemB, elemC, V_BC_list)

        V_AC_list = [(1.0 + xA - xC) / 2.0 for xA, xC in zip(xAList, xCList)]
        zACList = zAcSource.get_values(elemA, elemC, V_AC_list)

        zSymbol, zLatex, zUnit = self._getOutputSymbolLatexUnit(zAbSource)

        result = maggianu.calculateScatterWithData(
            elemA,
            elemB,
            elemC,
            nPoints,
            zABList,
            zBCList,
            zACList,
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

        return result
