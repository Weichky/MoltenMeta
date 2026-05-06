from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QButtonGroup,
    QRadioButton,
)
from PySide6.QtCore import Signal

from ...composition_input_module.composition_input import CompositionTool, FractionType, CompositionError, massToMole


class CompositionWizardDialog(QDialog):
    resultReady = Signal(dict)

    def __init__(
        self,
        module_service,
        module_id: str | None = None,
        method_name: str | None = None,
        max_components: int = 2,
        map_data: list[list] | None = None,
        default_output: str = "atomic_number",
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Composition Input"))
        self.setMinimumWidth(400)
        self._ms = module_service
        self._module_id = module_id
        self._method_name = method_name
        self._max_components = max_components
        self._map_data = map_data or []
        self._default_output = default_output
        self._composition_tool = CompositionTool()
        self._fraction_type = FractionType.MOLE
        self._atomic_mass_cache: dict[str, float] = {}
        self._setupUi()

    def _setupUi(self) -> None:
        layout = QVBoxLayout(self)

        label = QLabel("Composition input (e.g. Al90Si10)")
        layout.addWidget(label)

        self._composition_input = QLineEdit()
        self._composition_input.setPlaceholderText("Al90Si10")
        self._composition_input.textChanged.connect(self._onCompositionTextChanged)
        layout.addWidget(self._composition_input)

        hint = QLabel(f"Max components: {self._max_components}")
        hint.setStyleSheet("color: gray;")
        layout.addWidget(hint)

        self._composition_error_label = QLabel("", self)
        self._composition_error_label.setStyleSheet("color: red; font-size: 12px;")
        self._composition_error_label.hide()
        layout.addWidget(self._composition_error_label)

        layout.addStretch()

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self._fraction_button_group = QButtonGroup(self)
        mole_btn = QRadioButton("Mole", self)
        mass_btn = QRadioButton("Mass", self)
        mole_btn.setChecked(True)
        self._fraction_button_group.addButton(mole_btn, 0)
        self._fraction_button_group.addButton(mass_btn, 1)
        self._fraction_button_group.buttonClicked.connect(self._onFractionTypeChanged)
        bottom_layout.addWidget(mole_btn)
        bottom_layout.addWidget(mass_btn)

        button_box = QPushButton("OK", self)
        cancel_btn = QPushButton("Cancel", self)
        button_box.clicked.connect(self._onOkClicked)
        cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(button_box)
        bottom_layout.addWidget(cancel_btn)

        layout.addLayout(bottom_layout)

    def _onFractionTypeChanged(self, button) -> None:
        if self._fraction_button_group.id(button) == 0:
            self._fraction_type = FractionType.MOLE
        else:
            self._fraction_type = FractionType.MASS

    def _loadAtomicMassCache(self) -> None:
        if len(self._atomic_mass_cache) > 0:
            return
        from modules.element_properties_module import ElementPropertiesCalc
        calc = ElementPropertiesCalc()
        self._atomic_mass_cache = calc.getAllAtomicMasses()

    def _onCompositionTextChanged(self, text: str) -> None:
        if not self._composition_error_label:
            return
        if not text.strip():
            self._composition_error_label.hide()
            return
        try:
            self._composition_tool.parseAndValidate(
                text, self._fraction_type, self._max_components
            )
            self._composition_error_label.hide()
        except CompositionError as e:
            self._composition_error_label.setText(str(e))
            self._composition_error_label.show()

    def _onOkClicked(self) -> None:
        comp_str = self._composition_input.text().strip()
        if not comp_str:
            return

        try:
            parsed = self._composition_tool.parseAndValidate(
                comp_str, self._fraction_type, self._max_components
            )

            if self._fraction_type == FractionType.MASS:
                self._loadAtomicMassCache()
                fractions = massToMole(
                    parsed.fractions, parsed.elements, self._atomic_mass_cache
                )
                parsed = parsed.__class__(
                    elements=parsed.elements,
                    fractions=fractions,
                    fraction_type=FractionType.MOLE,
                )

            use_atomic_number = self._default_output == "atomic_number"
            kwargs = self._composition_tool.toArgumentMap(
                parsed, self._map_data, use_atomic_number=use_atomic_number
            )

            if self._module_id and self._method_name:
                result = self._ms.callMethod(self._module_id, self._method_name, **kwargs)
                self._ms.cacheResult(self._module_id, self._method_name, result, **kwargs)
            else:
                result = kwargs

            self.resultReady.emit(result)
            self.accept()
        except CompositionError as e:
            self._composition_error_label.setText(str(e))
            self._composition_error_label.show()


__all__ = ["CompositionWizardDialog", "createWizard"]


def createWizard(method_name: str, module_service, user_db_service, config: dict | None = None):
    if config is None:
        config = {}

    module_id = config.get("module_id")
    method_name = config.get("method_name")
    max_components = config.get("max_components", 2)
    map_data = config.get("map", [])
    default_output = config.get("default_output", "atomic_number")

    return CompositionWizardDialog(
        module_service,
        module_id=module_id,
        method_name=method_name,
        max_components=max_components,
        map_data=map_data,
        default_output=default_output,
    )