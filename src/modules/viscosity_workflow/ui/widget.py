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
    QLineEdit,
    QFileDialog,
    QCheckBox,
)
from PySide6.QtCore import Signal
import csv
from pathlib import Path

from ...geometric_model_core import StepIndicator


class ViscosityWorkflowWizardDialog(QDialog):
    resultReady = Signal(dict)

    def __init__(self, module_service, user_db_service, method_type="fit", parent=None):
        super().__init__(parent)
        self._method_type = method_type
        self.setWindowTitle(self.tr("Viscosity Workflow Configuration"))
        self.setMinimumSize(700, 550)
        self._ms = module_service
        self._userDb = user_db_service
        self._ternary_data = None
        self._arrhenius_params = {
            "Ti": (0.4288, 27.0),
            "Al": (0.1817, 16.642),
            "Ni": (0.4197, 27.3),
        }
        self._setupUi()

    def _setupUi(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(24)
        mainLayout.setContentsMargins(32, 32, 32, 32)

        title = QLabel(self.tr("Viscosity Workflow (Ti-Al-Ni)"))
        title.setObjectName("wizardTitle")
        mainLayout.addWidget(title)

        if self._method_type == "predict":
            steps = [
                self.tr("Composition"),
                self.tr("Temperature"),
                self.tr("Parameters"),
                self.tr("Ternary GP"),
            ]
        elif self._method_type == "predictOnGrid":
            steps = [
                self.tr("Model"),
                self.tr("Ternary GP"),
            ]
        elif self._method_type == "predictBatch":
            steps = [
                self.tr("Composition"),
                self.tr("Temperature"),
                self.tr("Parameters"),
                self.tr("Ternary GP"),
            ]
        else:
            steps = [
                self.tr("Ternary Data"),
                self.tr("Arrhenius"),
                self.tr("GP Settings"),
                self.tr("Model"),
            ]

        self._stepIndicator = StepIndicator(steps)
        mainLayout.addWidget(self._stepIndicator)

        self._stacked = QStackedWidget()
        mainLayout.addWidget(self._stacked)

        self._createTernaryDataPage()
        self._createArrheniusPage()
        self._createGPSettingsPage()
        self._createModelPage()
        self._createCompositionPage()
        self._createTemperaturePage()
        self._createTernaryGPPage()

        if self._method_type == "fit":
            self._stacked.addWidget(self._ternaryDataPage)
            self._stacked.addWidget(self._arrheniusPage)
            self._stacked.addWidget(self._gpSettingsPage)
            self._stacked.addWidget(self._modelPage)
            self._maxSteps = 4
        elif self._method_type == "predict":
            self._stacked.addWidget(self._compositionPage)
            self._stacked.addWidget(self._temperaturePage)
            self._stacked.addWidget(self._modelPage)
            self._stacked.addWidget(self._ternaryGPPage)
            self._maxSteps = 4
        elif self._method_type == "predictBatch":
            self._stacked.addWidget(self._compositionPage)
            self._stacked.addWidget(self._temperaturePage)
            self._stacked.addWidget(self._gpSettingsPage)
            self._stacked.addWidget(self._ternaryGPPage)
            self._maxSteps = 4
        elif self._method_type == "predictOnGrid":
            self._stacked.addWidget(self._modelPage)
            self._stacked.addWidget(self._ternaryGPPage)
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

    def _loadTernaryCsv(self, path: str) -> dict:
        data = {"x_Ti": [], "x_Al": [], "x_Ni": [], "vi": []}
        try:
            with open(path) as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    data["x_Ti"].append(float(row[0]))
                    data["x_Al"].append(float(row[1]))
                    data["x_Ni"].append(float(row[2]))
                    data["vi"].append(float(row[3]))
        except Exception:
            pass
        return data

    def _createTernaryDataPage(self):
        self._ternaryDataPage = QWidget()
        layout = QVBoxLayout(self._ternaryDataPage)
        layout.setContentsMargins(32, 32, 32, 32)

        group = QGroupBox(self.tr("Load Ti-Al-Ni Ternary Viscosity Data"))
        form = QFormLayout()

        self._ternaryBtn = QPushButton(self.tr("Select Ternary CSV..."))
        self._ternaryPath = QLabel("-")
        self._ternaryPath.setWordWrap(True)

        form.addRow("Ternary CSV:", self._ternaryBtn)
        form.addRow("", self._ternaryPath)

        group.setLayout(form)
        layout.addWidget(group)

        self._ternaryBtn.clicked.connect(self._selectTernaryCsv)

        layout.addStretch()

    def _selectTernaryCsv(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Ti-Al-Ni Ternary CSV"),
            "",
            self.tr("CSV Files (*.csv);;All Files (*.*)"),
        )
        if not path:
            return

        data = self._loadTernaryCsv(path)
        if data["x_Ti"]:
            self._ternary_data = data
            self._ternaryPath.setText(
                Path(path).name + f" ({len(data['x_Ti'])} points)"
            )

    def _createArrheniusPage(self):
        self._arrheniusPage = QWidget()
        layout = QVBoxLayout(self._arrheniusPage)
        layout.setContentsMargins(32, 32, 32, 32)

        group = QGroupBox(self.tr("Arrhenius Parameters for Pure Elements"))
        form = QFormLayout()

        self._TiArrheniusEdit = QLineEdit()
        self._TiArrheniusEdit.setText("0.4288, 27.0")

        self._AlArrheniusEdit = QLineEdit()
        self._AlArrheniusEdit.setText("0.1817, 16.642")

        self._NiArrheniusEdit = QLineEdit()
        self._NiArrheniusEdit.setText("0.4197, 27.3")

        form.addRow("Ti (eta_0, E_a):", self._TiArrheniusEdit)
        form.addRow("Al (eta_0, E_a):", self._AlArrheniusEdit)
        form.addRow("Ni (eta_0, E_a):", self._NiArrheniusEdit)

        group.setLayout(form)
        layout.addWidget(group)

        layout.addStretch()

    def _createGPSettingsPage(self):
        self._gpSettingsPage = QWidget()
        layout = QVBoxLayout(self._gpSettingsPage)
        layout.setContentsMargins(32, 32, 32, 32)

        group = QGroupBox(self.tr("Gaussian Process Settings"))
        form = QFormLayout()

        self._alphaSpin = QDoubleSpinBox()
        self._alphaSpin.setRange(0.0001, 10.0)
        self._alphaSpin.setValue(0.01)
        self._alphaSpin.setDecimals(4)
        self._alphaSpin.setObjectName("alphaInput")

        self._kernelCombo = QComboBox()
        self._kernelCombo.addItems(["rbf", "matern"])
        self._kernelCombo.setObjectName("kernelCombo")

        self._nuSpin = QDoubleSpinBox()
        self._nuSpin.setRange(0.5, 3.0)
        self._nuSpin.setValue(1.5)
        self._nuSpin.setDecimals(2)
        self._nuSpin.setObjectName("nuInput")

        form.addRow("Alpha:", self._alphaSpin)
        form.addRow("Kernel:", self._kernelCombo)
        form.addRow("Nu (Matern):", self._nuSpin)

        group.setLayout(form)
        layout.addWidget(group)

        layout.addStretch()

    def _createModelPage(self):
        self._modelPage = QWidget()
        layout = QVBoxLayout(self._modelPage)
        layout.setContentsMargins(32, 32, 32, 32)

        group = QGroupBox(self.tr("Geometric Model"))
        form = QFormLayout()

        self._modelCombo = QComboBox()
        self._modelCombo.addItems(["kohler", "toop", "maggianu", "hillert_toop"])
        self._modelCombo.setObjectName("modelCombo")

        form.addRow("Model:", self._modelCombo)

        group.setLayout(form)
        layout.addWidget(group)

        layout.addStretch()

    def _createTernaryGPPage(self):
        self._ternaryGPPage = QWidget()
        layout = QVBoxLayout(self._ternaryGPPage)
        layout.setContentsMargins(32, 32, 32, 32)

        group = QGroupBox(self.tr("Ternary GP Correction"))
        form = QFormLayout()

        self._includeTernaryGPCheck = QCheckBox()
        self._includeTernaryGPCheck.setChecked(True)
        self._includeTernaryGPCheck.setToolTip(
            self.tr("Include ternary GP correction on top of binary model prediction")
        )

        form.addRow("Include Ternary GP:", self._includeTernaryGPCheck)

        group.setLayout(form)
        layout.addWidget(group)

        layout.addStretch()

    def _createCompositionPage(self):
        self._compositionPage = QWidget()
        layout = QVBoxLayout(self._compositionPage)
        layout.setContentsMargins(32, 32, 32, 32)

        group = QGroupBox(self.tr("Composition"))
        form = QFormLayout()

        if self._method_type == "predictBatch":
            self._xTupleEdit = QLineEdit()
            self._xTupleEdit.setPlaceholderText(
                "[(0.3, 0.3, 0.4), (0.2, 0.5, 0.3), ...]"
            )
            self._xTupleEdit.setText("[(0.3, 0.3, 0.4)]")
        else:
            self._xTiSpin = QDoubleSpinBox()
            self._xTiSpin.setRange(0.0, 1.0)
            self._xTiSpin.setValue(0.3)
            self._xTiSpin.setDecimals(4)

            self._xAlSpin = QDoubleSpinBox()
            self._xAlSpin.setRange(0.0, 1.0)
            self._xAlSpin.setValue(0.3)
            self._xAlSpin.setDecimals(4)

            self._xNiSpin = QDoubleSpinBox()
            self._xNiSpin.setRange(0.0, 1.0)
            self._xNiSpin.setValue(0.4)
            self._xNiSpin.setDecimals(4)

            form.addRow("x_Ti:", self._xTiSpin)
            form.addRow("x_Al:", self._xAlSpin)
            form.addRow("x_Ni:", self._xNiSpin)

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
        self._TSpin.setValue(2033.0)
        self._TSpin.setDecimals(2)
        self._TSpin.setSuffix(" K")

        form.addRow("Temperature:", self._TSpin)

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
        if self._method_type == "fit":
            return self._collectFitParams()
        elif self._method_type == "predict":
            return self._collectPredictParams()
        elif self._method_type == "predictBatch":
            return self._collectPredictBatchParams()
        elif self._method_type == "predictOnGrid":
            return self._collectPredictOnGridParams()
        return {}

    def _collectFitParams(self) -> dict:
        def parse_arrhenius(text):
            parts = text.split(",")
            return (float(parts[0].strip()), float(parts[1].strip()))

        arrhenius_params = {
            "Ti": parse_arrhenius(self._TiArrheniusEdit.text()),
            "Al": parse_arrhenius(self._AlArrheniusEdit.text()),
            "Ni": parse_arrhenius(self._NiArrheniusEdit.text()),
        }

        from ..viscosity_workflow import ViscosityWorkflowParams

        params = ViscosityWorkflowParams(
            alpha=self._alphaSpin.value(),
            kernel_type=self._kernelCombo.currentText(),
            nu=self._nuSpin.value(),
            model_name=self._modelCombo.currentText(),
        )

        return {
            "method_name": "fit",
            "ternary_data": self._ternary_data,
            "arrhenius_params": arrhenius_params,
            "params": params,
        }

    def _collectPredictParams(self) -> dict:
        x_tuple = (
            self._xTiSpin.value(),
            self._xAlSpin.value(),
            self._xNiSpin.value(),
        )
        return {
            "method_name": "predict",
            "x_tuple": list(x_tuple),
            "T": self._TSpin.value(),
            "model_name": self._modelCombo.currentText(),
            "include_ternary_gp": self._includeTernaryGPCheck.isChecked(),
        }

    def _collectPredictBatchParams(self) -> dict:
        import json

        try:
            x_tuples = json.loads(self._xTupleEdit.text())
        except Exception:
            x_tuples = []
        return {
            "method_name": "predictBatch",
            "x_tuples": x_tuples,
            "T": self._TSpin.value(),
            "include_ternary_gp": self._includeTernaryGPCheck.isChecked(),
        }

    def _collectPredictOnGridParams(self) -> dict:
        return {
            "method_name": "predictOnGrid",
            "include_ternary_gp": self._includeTernaryGPCheck.isChecked(),
        }
