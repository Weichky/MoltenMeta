from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QWidget,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QMessageBox,
)
from PySide6.QtCore import Signal

from ...geometric_model_core import (
    StepIndicator,
    ElementSelectionPage,
    DataSourceSelectionPage,
    CalculationOptionsPage,
)


class KohlerWizardDialog(QDialog):
    resultReady = Signal(dict)

    def __init__(self, module_service, user_db_service, method_type="scatter", parent=None):
        super().__init__(parent)
        self._method_type = method_type
        self.setWindowTitle(self.tr("Kohler Model Configuration"))
        self.setMinimumSize(600, 500)
        self._ms = module_service
        self._userDb = user_db_service
        self._sources = {"Z_AB": None, "Z_BC": None, "Z_AC": None}
        self._setupUi()

    def _setupUi(self):
        from ..data_source_discovery import KohlerDataSourceDiscovery

        self._discovery = KohlerDataSourceDiscovery(
            self._ms, self._userDb, self._ms.getDataSourceRegistry()
        )

        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(24)
        mainLayout.setContentsMargins(32, 32, 32, 32)

        title = QLabel(self.tr("Kohler Model Configuration"))
        title.setObjectName("wizardTitle")
        mainLayout.addWidget(title)

        if self._method_type == "contour":
            steps = [
                self.tr("Elements"),
                self.tr("Z_AB"),
                self.tr("Z_BC"),
                self.tr("Z_AC"),
                self.tr("Plane"),
                self.tr("Options"),
            ]
        else:
            steps = [
                self.tr("Elements"),
                self.tr("Z_AB"),
                self.tr("Z_BC"),
                self.tr("Z_AC"),
                self.tr("Options"),
            ]

        self._stepIndicator = StepIndicator(steps)
        mainLayout.addWidget(self._stepIndicator)

        self._stacked = QStackedWidget()
        mainLayout.addWidget(self._stacked)

        self._elementPage = ElementSelectionPage()
        self._stacked.addWidget(self._elementPage)

        self._zAbPage = DataSourceSelectionPage(self.tr("Z_AB Data Source"), "Z_AB")
        self._zBcPage = DataSourceSelectionPage(self.tr("Z_BC Data Source"), "Z_BC")
        self._zAcPage = DataSourceSelectionPage(self.tr("Z_AC Data Source"), "Z_AC")

        self._stacked.addWidget(self._zAbPage)
        self._stacked.addWidget(self._zBcPage)
        self._stacked.addWidget(self._zAcPage)

        if self._method_type == "contour":
            self._planePage = QWidget()
            planeLayout = QVBoxLayout(self._planePage)
            planeLayout.setContentsMargins(32, 32, 32, 32)
            planeGroup = QGroupBox(self.tr("Projection Plane"))
            planeForm = QFormLayout()
            self._planeCombo = QComboBox()
            self._planeCombo.addItems(["x_A-x_B", "x_A-x_C", "x_B-x_C"])
            planeForm.addRow(self.tr("Plane:"), self._planeCombo)
            planeGroup.setLayout(planeForm)
            planeLayout.addWidget(planeGroup)
            planeLayout.addStretch()
            self._stacked.addWidget(self._planePage)

        self._optionsPage = CalculationOptionsPage()
        self._stacked.addWidget(self._optionsPage)

        buttonLayout = QHBoxLayout()
        self._cancelBtn = QPushButton(self.tr("Cancel"))
        self._prevBtn = QPushButton(self.tr("Previous"))
        self._prevBtn.setObjectName("secondary")
        self._nextBtn = QPushButton(self.tr("Next"))
        self._nextBtn.setObjectName("primary")
        self._configBtn = QPushButton(self.tr("Configure"))
        self._configBtn.setObjectName("primary")

        self._prevBtn.setEnabled(False)
        self._configBtn.setVisible(False)

        buttonLayout.addWidget(self._cancelBtn)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self._prevBtn)
        buttonLayout.addWidget(self._nextBtn)
        buttonLayout.addWidget(self._configBtn)

        mainLayout.addLayout(buttonLayout)

        self._cancelBtn.clicked.connect(self.reject)
        self._prevBtn.clicked.connect(self._onPrev)
        self._nextBtn.clicked.connect(self._onNext)
        self._configBtn.clicked.connect(self._onConfigure)

        self._elementPage.selectionChanged.connect(self._onElementsChanged)
        self._zAbPage.selectionChanged.connect(self._onZAbChanged)
        self._zBcPage.selectionChanged.connect(self._onZBcChanged)
        self._zAcPage.selectionChanged.connect(self._onZAcChanged)

        self._currentStep = 0
        self._maxSteps = 5 if self._method_type == "contour" else 4
        self._updateSources()
        self._updatePageSources()

    def _updateNavigation(self):
        self._prevBtn.setEnabled(self._currentStep > 0)
        self._nextBtn.setVisible(self._currentStep < self._maxSteps)
        self._configBtn.setVisible(self._currentStep == self._maxSteps)

    def _onPrev(self):
        if self._currentStep > 0:
            self._currentStep -= 1
            self._stacked.setCurrentIndex(self._currentStep)
            self._updateNavigation()

    def _onNext(self):
        if self._currentStep < self._maxSteps:
            self._currentStep += 1
            self._stacked.setCurrentIndex(self._currentStep)
            self._updateNavigation()

    def _onElementsChanged(self):
        self._updateSources()
        self._updatePageSources()

    def _onZAbChanged(self):
        self._sources["Z_AB"] = self._zAbPage.getSelectedSource()

    def _onZBcChanged(self):
        self._sources["Z_BC"] = self._zBcPage.getSelectedSource()

    def _onZAcChanged(self):
        self._sources["Z_AC"] = self._zAcPage.getSelectedSource()

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

    def _onConfigure(self):
        if (
            not self._sources["Z_AB"]
            or not self._sources["Z_BC"]
            or not self._sources["Z_AC"]
        ):
            QMessageBox.warning(
                self,
                self.tr("Warning"),
                self.tr("Please select data sources for all inputs"),
            )
            return

        params = self.getInputs()
        self.resultReady.emit(params)
        self.accept()

    def getInputs(self) -> dict:
        from ..kohler_module import KohlerCalc

        elemA, elemB, elemC = self._elementPage.getElements()
        nPoints = self._optionsPage.getNPoints()
        plane = self._planeCombo.currentText() if self._method_type == "contour" else None

        kohler = KohlerCalc()
        xAList, xBList, xCList = kohler._generateGrid(nPoints)

        zAbSource = self._sources["Z_AB"]
        zBcSource = self._sources["Z_BC"]
        zAcSource = self._sources["Z_AC"]

        wABList = [
            xA / (xA + xB) if (xA + xB) > 0 else 0 for xA, xB in zip(xAList, xBList)
        ]
        zABList = zAbSource.getValues(elemA, elemB, wABList)

        wBCList = [
            xB / (xB + xC) if (xB + xC) > 0 else 0 for xB, xC in zip(xBList, xCList)
        ]
        zBCList = zBcSource.getValues(elemB, elemC, wBCList)

        wACList = [
            xA / (xA + xC) if (xA + xC) > 0 else 0 for xA, xC in zip(xAList, xCList)
        ]
        zACList = zAcSource.getValues(elemA, elemC, wACList)

        zSymbol, zLatex, zUnit = self._getOutputSymbolLatexUnit(zAbSource)

        if self._method_type == "contour":
            return {
                "method_name": "calculateContourWithData",
                "elem_A": elemA,
                "elem_B": elemB,
                "elem_C": elemC,
                "plane": plane,
                "n_points": nPoints,
                "Z_AB_list": zABList,
                "Z_AC_list": zACList,
                "Z_BC_list": zBCList,
                "z_latex": zLatex,
                "z_unit": zUnit,
                "z_symbol": zSymbol,
            }
        else:
            return {
                "method_name": "calculateScatterWithData",
                "elem_A": elemA,
                "elem_B": elemB,
                "elem_C": elemC,
                "n_points": nPoints,
                "Z_AB_list": zABList,
                "Z_AC_list": zACList,
                "Z_BC_list": zBCList,
                "z_latex": zLatex,
                "z_unit": zUnit,
                "z_symbol": zSymbol,
            }
