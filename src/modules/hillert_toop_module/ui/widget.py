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

from ...geometric_model_core import (
    StepIndicator,
    ElementSelectionPage,
    DataSourceSelectionPage,
    CalculationOptionsPage,
)


class HillertToopWizardDialog(QDialog):
    resultReady = Signal(dict)

    def __init__(self, module_service, user_db_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Hillert-Toop Model Configuration"))
        self.setMinimumSize(600, 500)
        self._ms = module_service
        self._userDb = user_db_service
        self._sources = {"Z_AB": None, "Z_AC": None, "Z_BC": None}
        self._setupUi()

    def _setupUi(self):
        from ..data_source_discovery import BinaryDataSourceDiscovery

        self._discovery = BinaryDataSourceDiscovery(
            self._ms, self._userDb, self._ms.getDataSourceRegistry()
        )

        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(24)
        mainLayout.setContentsMargins(32, 32, 32, 32)

        title = QLabel(self.tr("Hillert-Toop Model Configuration"))
        title.setObjectName("wizardTitle")
        mainLayout.addWidget(title)

        self._stepIndicator = StepIndicator(
            [
                self.tr("Elements"),
                self.tr("Z_AB"),
                self.tr("Z_AC"),
                self.tr("Z_BC"),
                self.tr("Options"),
            ]
        )
        mainLayout.addWidget(self._stepIndicator)

        self._stacked = QStackedWidget()
        mainLayout.addWidget(self._stacked)

        self._elementPage = ElementSelectionPage()
        self._stacked.addWidget(self._elementPage)

        self._zAbPage = DataSourceSelectionPage(self.tr("Z_AB Data Source"), "Z_AB")
        self._zAcPage = DataSourceSelectionPage(self.tr("Z_AC Data Source"), "Z_AC")
        self._zBcPage = DataSourceSelectionPage(self.tr("Z_BC Data Source"), "Z_BC")
        self._optionsPage = CalculationOptionsPage()

        self._stacked.addWidget(self._zAbPage)
        self._stacked.addWidget(self._zAcPage)
        self._stacked.addWidget(self._zBcPage)
        self._stacked.addWidget(self._optionsPage)

        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(16)

        self._cancelBtn = QPushButton(self.tr("Cancel"))
        self._cancelBtn.setObjectName("secondary")
        self._prevBtn = QPushButton(self.tr("Previous"))
        self._prevBtn.setObjectName("secondary")
        self._nextBtn = QPushButton(self.tr("Next"))
        self._nextBtn.setObjectName("primary")
        self._calcBtn = QPushButton(self.tr("Calculate"))
        self._calcBtn.setObjectName("primary")

        self._prevBtn.setEnabled(False)
        self._calcBtn.setVisible(False)

        buttonLayout.addWidget(self._cancelBtn)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self._prevBtn)
        buttonLayout.addWidget(self._nextBtn)
        buttonLayout.addWidget(self._calcBtn)

        mainLayout.addLayout(buttonLayout)

        self._cancelBtn.clicked.connect(self.reject)
        self._prevBtn.clicked.connect(self._onPrev)
        self._nextBtn.clicked.connect(self._onNext)
        self._calcBtn.clicked.connect(self._onCalculate)

        self._elementPage.selectionChanged.connect(self._onElementsChanged)
        self._zAbPage.selectionChanged.connect(self._onZAbChanged)
        self._zAcPage.selectionChanged.connect(self._onZAcChanged)
        self._zBcPage.selectionChanged.connect(self._onZBcChanged)

        self._currentStep = 0
        self._updateSources()

    def _updateSources(self):
        elemA, elemB, elemC = self._elementPage.getElements()

        sourcesAB = self._discovery.findSources("thermodynamic", elemA, elemB)
        sourcesAC = self._discovery.findSources("thermodynamic", elemA, elemC)
        sourcesBC = self._discovery.findSources("thermodynamic", elemB, elemC)

        self._zAbPage.setSources(sourcesAB)
        self._zAcPage.setSources(sourcesAC)
        self._zBcPage.setSources(sourcesBC)

        if sourcesAB:
            self._sources["Z_AB"] = sourcesAB[0]
        if sourcesAC:
            self._sources["Z_AC"] = sourcesAC[0]
        if sourcesBC:
            self._sources["Z_BC"] = sourcesBC[0]

    def _onElementsChanged(self):
        self._updateSources()

    def _onZAbChanged(self):
        self._sources["Z_AB"] = self._zAbPage.getSelectedSource()

    def _onZAcChanged(self):
        self._sources["Z_AC"] = self._zAcPage.getSelectedSource()

    def _onZBcChanged(self):
        self._sources["Z_BC"] = self._zBcPage.getSelectedSource()

    def _onPrev(self):
        if self._currentStep > 0:
            self._currentStep -= 1
            self._stacked.setCurrentIndex(self._currentStep)
            self._updateButtons()

    def _onNext(self):
        if self._currentStep < 4:
            self._currentStep += 1
            self._stacked.setCurrentIndex(self._currentStep)
            self._updateButtons()

    def _updateButtons(self):
        self._prevBtn.setEnabled(self._currentStep > 0)
        self._nextBtn.setVisible(self._currentStep < 4)
        self._calcBtn.setVisible(self._currentStep == 4)

    def _onCalculate(self):
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
        elemA, elemB, elemC = self._elementPage.getElements()
        return {
            "elem_A": elemA,
            "elem_B": elemB,
            "elem_C": elemC,
            "n_points": self._optionsPage.getNPoints(),
            "contour_points": self._optionsPage.getContourPoints(),
            "sources": self._sources.copy(),
        }

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

    def calculate(self, inputs: dict) -> dict:
        from ..hillert_toop_module import HillertToopCalc

        elemA = inputs["elem_A"]
        elemB = inputs["elem_B"]
        elemC = inputs["elem_C"]
        nPoints = inputs["n_points"]
        sources = inputs["sources"]

        hillert_toop = HillertToopCalc()

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
        zAcSource = sources["Z_AC"]
        zBcSource = sources["Z_BC"]

        zABList = zAbSource.getValues(elemA, elemB, xAList)
        zACList = zAcSource.getValues(elemA, elemC, xAList)

        wBList = [
            xB / (xB + xC) if (xB + xC) > 0 else 0 for xB, xC in zip(xBList, xCList)
        ]
        zBCList = zBcSource.getValues(elemB, elemC, wBList)

        zSymbol, zLatex, zUnit = self._getOutputSymbolLatexUnit(zAbSource)

        result = hillert_toop.calculateScatterWithData(
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
            "hillert_toop_module",
            "calculateScatter",
            result,
            elem_A=elemA,
            elem_B=elemB,
            elem_C=elemC,
            n_points=nPoints,
        )

        return result
