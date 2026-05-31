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
    QDoubleSpinBox,
    QSpinBox,
    QLineEdit,
)
from PySide6.QtCore import Signal

from ...geometric_model_core import StepIndicator


class SurfaceWorkflowWizardDialog(QDialog):
    resultReady = Signal(dict)

    def __init__(self, module_service, user_db_service, method_type="fit", parent=None):
        super().__init__(parent)
        self._method_type = method_type
        self.setWindowTitle(self.tr("Surface Tension Workflow (Butler)"))
        self.setMinimumSize(700, 550)
        self._ms = module_service
        self._userDb = user_db_service
        self._sources = {}
        self._setupUi()

    def _setupUi(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(24)
        mainLayout.setContentsMargins(32, 32, 32, 32)

        title = QLabel(self.tr("Surface Tension Workflow (Butler Model)"))
        title.setObjectName("wizardTitle")
        mainLayout.addWidget(title)

        if self._method_type == "fit":
            steps = [
                self.tr("Elements"),
                self.tr("RK Coefficients"),
            ]
        elif self._method_type == "predict":
            steps = [
                self.tr("Temperature"),
                self.tr("Composition"),
            ]
        elif self._method_type == "sample":
            steps = [
                self.tr("Temperature"),
                self.tr("Composition"),
                self.tr("Monte Carlo"),
            ]
        elif self._method_type == "predictCurve":
            steps = [
                self.tr("Temperature"),
                self.tr("Curve Settings"),
            ]

        self._stepIndicator = StepIndicator(steps)
        mainLayout.addWidget(self._stepIndicator)

        self._stacked = QStackedWidget()
        mainLayout.addWidget(self._stacked)

        self._createElementsPage()
        self._createRKPage()
        self._createTemperaturePage()
        self._createCompositionPage()
        self._createMonteCarloPage()
        self._createCurveSettingsPage()

        if self._method_type == "fit":
            self._stacked.addWidget(self._elementsPage)
            self._stacked.addWidget(self._rkPage)
            self._maxSteps = 2
        elif self._method_type == "predict":
            self._stacked.addWidget(self._temperaturePage)
            self._stacked.addWidget(self._compositionPage)
            self._maxSteps = 2
        elif self._method_type == "sample":
            self._stacked.addWidget(self._temperaturePage)
            self._stacked.addWidget(self._compositionPage)
            self._stacked.addWidget(self._monteCarloPage)
            self._maxSteps = 3
        elif self._method_type == "predictCurve":
            self._stacked.addWidget(self._temperaturePage)
            self._stacked.addWidget(self._curveSettingsPage)
            self._maxSteps = 2

        buttonLayout = QHBoxLayout()
        self._cancelBtn = QPushButton(self.tr("Cancel"))
        self._prevBtn = QPushButton(self.tr("Previous"))
        self._prevBtn.setObjectName("secondary")
        self._nextBtn = QPushButton(self.tr("Next"))
        self._nextBtn.setObjectName("primary")
        self._runBtn = QPushButton(self.tr("Run"))
        self._runBtn.setObjectName("primary")

        self._prevBtn.setEnabled(False)

        buttonLayout.addWidget(self._cancelBtn)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self._prevBtn)
        buttonLayout.addWidget(self._nextBtn)
        buttonLayout.addWidget(self._runBtn)

        mainLayout.addLayout(buttonLayout)

        self._cancelBtn.clicked.connect(self.reject)
        self._prevBtn.clicked.connect(self._onPrev)
        self._nextBtn.clicked.connect(self._onNext)
        self._runBtn.clicked.connect(self._onRun)

        self._currentStep = 0
        self._updateNavigation()

    def _createElementsPage(self):
        self._elementsPage = QWidget()
        layout = QVBoxLayout(self._elementsPage)
        layout.setContentsMargins(32, 32, 32, 32)

        group = QGroupBox(self.tr("Select Elements"))
        form = QFormLayout()

        self._elemACombo = QComboBox()
        self._elemACombo.addItems(["Al", "Mg", "Si", "Ti", "Ni", "Cu", "Zn"])
        self._elemACombo.setCurrentText("Al")

        self._elemBCombo = QComboBox()
        self._elemBCombo.addItems(["Mg", "Al", "Si", "Ti", "Ni", "Cu", "Zn"])
        self._elemBCombo.setCurrentText("Mg")

        form.addRow("Element A:", self._elemACombo)
        form.addRow("Element B:", self._elemBCombo)

        group.setLayout(form)
        layout.addWidget(group)

        layout.addStretch()

    def _createRKPage(self):
        self._rkPage = QWidget()
        layout = QVBoxLayout(self._rkPage)
        layout.setContentsMargins(32, 32, 32, 32)

        group = QGroupBox(self.tr("Redlich-Kister Coefficients"))
        form = QFormLayout()

        self._LCoeffsEdit = QLineEdit()
        self._LCoeffsEdit.setPlaceholderText("100.0, 0.0, 200.0, 0.0, 50.0, 0.0")
        self._LCoeffsEdit.setText("100.0, 0.0, 200.0, 0.0, 50.0, 0.0")

        self._orderSpin = QSpinBox()
        self._orderSpin.setRange(1, 3)
        self._orderSpin.setValue(2)

        form.addRow("L Coefficients:", self._LCoeffsEdit)
        form.addRow("Order:", self._orderSpin)

        group.setLayout(form)
        layout.addWidget(group)

        layout.addStretch()

    def _createTemperaturePage(self):
        self._temperaturePage = QWidget()
        layout = QVBoxLayout(self._temperaturePage)
        layout.setContentsMargins(32, 32, 32, 32)

        group = QGroupBox(self.tr("Temperature"))
        form = QFormLayout()

        self._TSpin = QDoubleSpinBox()
        self._TSpin.setRange(300.0, 4000.0)
        self._TSpin.setValue(1000.0)
        self._TSpin.setDecimals(2)
        self._TSpin.setSuffix(" K")

        form.addRow("Temperature:", self._TSpin)

        group.setLayout(form)
        layout.addWidget(group)

        layout.addStretch()

    def _createCompositionPage(self):
        self._compositionPage = QWidget()
        layout = QVBoxLayout(self._compositionPage)
        layout.setContentsMargins(32, 32, 32, 32)

        group = QGroupBox(self.tr("Bulk Composition"))
        form = QFormLayout()

        self._xBulkASpin = QDoubleSpinBox()
        self._xBulkASpin.setRange(0.0, 1.0)
        self._xBulkASpin.setValue(0.3)
        self._xBulkASpin.setDecimals(4)

        form.addRow("x_bulk_A:", self._xBulkASpin)

        group.setLayout(form)
        layout.addWidget(group)

        layout.addStretch()

    def _createMonteCarloPage(self):
        self._monteCarloPage = QWidget()
        layout = QVBoxLayout(self._monteCarloPage)
        layout.setContentsMargins(32, 32, 32, 32)

        group = QGroupBox(self.tr("Monte Carlo Settings"))
        form = QFormLayout()

        self._nSamplesSpin = QSpinBox()
        self._nSamplesSpin.setRange(100, 10000)
        self._nSamplesSpin.setValue(1000)

        form.addRow("Number of Samples:", self._nSamplesSpin)

        group.setLayout(form)
        layout.addWidget(group)

        layout.addStretch()

    def _createCurveSettingsPage(self):
        self._curveSettingsPage = QWidget()
        layout = QVBoxLayout(self._curveSettingsPage)
        layout.setContentsMargins(32, 32, 32, 32)

        group = QGroupBox(self.tr("Isothermal Curve Settings"))
        form = QFormLayout()

        self._nPointsSpin = QSpinBox()
        self._nPointsSpin.setRange(5, 101)
        self._nPointsSpin.setValue(21)

        form.addRow("Number of points:", self._nPointsSpin)

        group.setLayout(form)
        layout.addWidget(group)

        layout.addStretch()

    def _updateNavigation(self):
        self._prevBtn.setEnabled(self._currentStep > 0)
        self._nextBtn.setVisible(self._currentStep < self._maxSteps - 1)
        self._runBtn.setVisible(self._currentStep == self._maxSteps - 1)

    def _onPrev(self):
        if self._currentStep > 0:
            self._currentStep -= 1
            self._stacked.setCurrentIndex(self._currentStep)
            self._updateNavigation()

    def _onNext(self):
        if self._currentStep < self._maxSteps - 1:
            self._currentStep += 1
            self._stacked.setCurrentIndex(self._currentStep)
            self._updateNavigation()

    def _onRun(self):
        params = self._collectParams()
        self.resultReady.emit(params)
        self.accept()

    def _collectParams(self) -> dict:
        def parse_l_coeffs(text):
            return [float(x.strip()) for x in text.split(",")]

        if self._method_type == "fit":
            from ...element_map.element_map import elemSymbolToId

            return {
                "method_name": "fit",
                "elem_A": elemSymbolToId(self._elemACombo.currentText()),
                "elem_B": elemSymbolToId(self._elemBCombo.currentText()),
                "L_coeffs": parse_l_coeffs(self._LCoeffsEdit.text()),
                "order": self._orderSpin.value(),
            }
        elif self._method_type == "predict":
            return {
                "method_name": "predict",
                "T": self._TSpin.value(),
                "x_bulk_A": self._xBulkASpin.value(),
            }
        elif self._method_type == "sample":
            return {
                "method_name": "sample",
                "T": self._TSpin.value(),
                "x_bulk_A": self._xBulkASpin.value(),
                "n_samples": self._nSamplesSpin.value(),
            }
        elif self._method_type == "predictCurve":
            return {
                "method_name": "predictCurve",
                "T": self._TSpin.value(),
                "n_points": self._nPointsSpin.value(),
            }
        return {}
