from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QMessageBox,
)
from PySide6.QtCore import Signal

from ...element_map.element_map import ELEMENT_SYMBOLS, elemSymbolToId
from ...composition_input_module.ui.wizard import CompositionWizardDialog


class MiedemaRangeWizardDialog(QDialog):
    resultReady = Signal(dict)

    def __init__(self, module_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Miedema Range Configuration"))
        self.setMinimumSize(400, 300)
        self._ms = module_service
        self._setupUi()

    def _setupUi(self):
        mainLayout = QVBoxLayout(self)

        title = QLabel(self.tr("Miedema Enthalpy of Mixing (Range)"))
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        mainLayout.addWidget(title)

        elementsGroup = QGroupBox(self.tr("Elements"))
        elementsLayout = QFormLayout()

        self._elemACombo = QComboBox()
        self._elemACombo.addItems(ELEMENT_SYMBOLS)
        self._elemACombo.setCurrentText("Al")

        self._elemBCombo = QComboBox()
        self._elemBCombo.addItems(ELEMENT_SYMBOLS)
        self._elemBCombo.setCurrentText("Si")

        elementsLayout.addRow(self.tr("Element A:"), self._elemACombo)
        elementsLayout.addRow(self.tr("Element B:"), self._elemBCombo)
        elementsGroup.setLayout(elementsLayout)
        mainLayout.addWidget(elementsGroup)

        rangeGroup = QGroupBox(self.tr("Composition Range"))
        rangeLayout = QFormLayout()

        self._xStartSpin = QDoubleSpinBox()
        self._xStartSpin.setRange(0.0, 1.0)
        self._xStartSpin.setDecimals(4)
        self._xStartSpin.setValue(0.0)

        self._xEndSpin = QDoubleSpinBox()
        self._xEndSpin.setRange(0.0, 1.0)
        self._xEndSpin.setDecimals(4)
        self._xEndSpin.setValue(1.0)

        self._nPointsSpin = QDoubleSpinBox()
        self._nPointsSpin.setRange(2, 1000)
        self._nPointsSpin.setDecimals(0)
        self._nPointsSpin.setValue(50)

        rangeLayout.addRow(self.tr("x_A start:"), self._xStartSpin)
        rangeLayout.addRow(self.tr("x_A end:"), self._xEndSpin)
        rangeLayout.addRow(self.tr("Number of points:"), self._nPointsSpin)
        rangeGroup.setLayout(rangeLayout)
        mainLayout.addWidget(rangeGroup)

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

    def _onCalculate(self):
        from importlib import import_module

        elemA = elemSymbolToId(self._elemACombo.currentText())
        elemB = elemSymbolToId(self._elemBCombo.currentText())
        x_start = self._xStartSpin.value()
        x_end = self._xEndSpin.value()
        n_points = int(self._nPointsSpin.value())

        if elemA is None or elemB is None:
            QMessageBox.warning(self, self.tr("Error"), self.tr("Invalid element"))
            return

        if x_start >= x_end:
            QMessageBox.warning(self, self.tr("Error"), self.tr("Start must be < End"))
            return

        try:
            miedema_calc = import_module("modules.miedema_module.miedema_module")
            MiedemaCalc = getattr(miedema_calc, "MiedemaCalc")
            miedema = MiedemaCalc()
            result = miedema.calculateRange(elemA, elemB, x_start, x_end, n_points)

            self._ms.cacheResult(
                "miedema_module",
                "calculateRange",
                result,
                elem_A=elemA,
                elem_B=elemB,
                x_start=x_start,
                x_end=x_end,
                n_points=n_points,
            )

            self.resultReady.emit(result)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), str(e))


__all__ = ["MiedemaRangeWizardDialog", "createWizard"]


def createWizard(method_name: str, module_service, user_db_service):
    if method_name == "calculateSingle":
        return CompositionWizardDialog(
            module_service,
            module_id="miedema_module",
            method_name="calculateSingle",
            max_components=2,
            map_data=[["elem_A", 0], ["elem_B", 2], ["x_A", 1]],
            default_output="atomic_number",
        )
    elif method_name == "calculateRange":
        return MiedemaRangeWizardDialog(module_service)
    return None