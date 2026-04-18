from PySide6 import QtWidgets

from catalog import INT32_MIN, INT32_MAX, FLOAT_MIN, FLOAT_MAX
from core.composition import CompositionTool, FractionType, CompositionError, massToMole
from core.element_map import symbolToId, idToSymbol


def _buildSpinBoxWithHint(parent, min_val: int, max_val: int, hint: str):
    container = QtWidgets.QWidget(parent)
    layout = QtWidgets.QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)

    spinbox = QtWidgets.QSpinBox(container)
    spinbox.setMinimum(min_val)
    spinbox.setMaximum(max_val)
    layout.addWidget(spinbox)

    hint_label = QtWidgets.QLabel(hint, container)
    hint_label.setStyleSheet("color: gray; font-size: 11px;")
    layout.addWidget(hint_label)

    return container, spinbox


def _buildDoubleSpinBoxWithHint(parent, min_val: float, max_val: float, hint: str):
    container = QtWidgets.QWidget(parent)
    layout = QtWidgets.QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)

    spinbox = QtWidgets.QDoubleSpinBox(container)
    spinbox.setMinimum(min_val)
    spinbox.setMaximum(max_val)
    spinbox.setDecimals(4)
    layout.addWidget(spinbox)

    hint_label = QtWidgets.QLabel(hint, container)
    hint_label.setStyleSheet("color: gray; font-size: 11px;")
    layout.addWidget(hint_label)

    return container, spinbox


def _buildSymbolInput(parent, hint: str):
    widget = QtWidgets.QLineEdit(parent)
    widget.setPlaceholderText(hint)
    return widget


_WIDGET_BUILDERS: dict[str, callable] = {
    "element_id_input": lambda p: _buildSpinBoxWithHint(p, 1, 118, "1-118"),
    "element_symbol_input": lambda p: _buildSymbolInput(p, "e.g. Al, Si"),
    "text_input": lambda p: _buildSymbolInput(p, "enter value"),
    "int_input": lambda p: _buildSpinBoxWithHint(p, INT32_MIN, INT32_MAX, "integer"),
    "float_input": lambda p: _buildDoubleSpinBoxWithHint(
        p, FLOAT_MIN, FLOAT_MAX, "decimal"
    ),
}

_VALUE_EXTRACTORS: dict[str, callable] = {
    "element_id_input": lambda w: w.value(),
    "element_symbol_input": lambda w: symbolToId(w.text().strip()),
    "text_input": lambda w: w.text().strip(),
    "int_input": lambda w: w.value(),
    "float_input": lambda w: w.value(),
}


def getSupportedInputTypes() -> list[str]:
    return list(_WIDGET_BUILDERS.keys())


class InputDialog(QtWidgets.QDialog):
    def __init__(self, config: dict, user_db_service, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Configure Input")
        self.setMinimumWidth(400)
        self._config = config
        self._user_db = user_db_service
        self._composition_tool = CompositionTool()
        self._inputs_layout = None
        self._raw_widgets: dict[str, QtWidgets.QWidget] = {}
        self._raw_types: dict[str, str] = {}
        self._composition_input: QtWidgets.QLineEdit | None = None
        self._fraction_type = FractionType.MOLE
        self._fraction_button_group: QtWidgets.QButtonGroup | None = None
        self._composition_error_label: QtWidgets.QLabel | None = None
        self._atomic_mass_cache: dict[str, float] = {}
        self._setupUi()

    def _setupUi(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)

        input_method = self._config.get("input_method", "raw")

        if input_method == "composition_tool":
            self._setupCompositionTool(layout)
        else:
            self._setupRawInputs(layout)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addStretch()

        if input_method == "composition_tool":
            self._fraction_button_group = QtWidgets.QButtonGroup(self)
            mole_btn = QtWidgets.QRadioButton("Mole", self)
            mass_btn = QtWidgets.QRadioButton("Mass", self)
            mole_btn.setChecked(True)
            self._fraction_button_group.addButton(mole_btn, 0)
            self._fraction_button_group.addButton(mass_btn, 1)
            self._fraction_button_group.buttonClicked.connect(
                self._onFractionTypeChanged
            )
            bottom_layout.addWidget(mole_btn)
            bottom_layout.addWidget(mass_btn)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        bottom_layout.addWidget(button_box)

        layout.addLayout(bottom_layout)

    def _onFractionTypeChanged(self, button: QtWidgets.QAbstractButton) -> None:
        if self._fraction_button_group.id(button) == 0:
            self._fraction_type = FractionType.MOLE
        else:
            self._fraction_type = FractionType.MASS

    def _loadAtomicMassCache(self) -> None:
        if len(self._atomic_mass_cache) > 0:
            return
        elements = self._user_db.element_repo.findAll()
        for elem in elements:
            if elem.atomic_mass is not None:
                symbol = idToSymbol(elem.symbol_id)
                if symbol:
                    self._atomic_mass_cache[symbol] = elem.atomic_mass

    def _setupCompositionTool(self, parent_layout: QtWidgets.QVBoxLayout) -> None:
        comp_config = self._config["composition_tool"]
        map_data = comp_config["map"]
        max_components = comp_config.get("max_components", 2)

        label = QtWidgets.QLabel("Composition input (e.g. Al90Si10)")
        parent_layout.addWidget(label)

        self._composition_input = QtWidgets.QLineEdit()
        self._composition_input.setPlaceholderText("Al90Si10")
        self._composition_input.textChanged.connect(self._onCompositionTextChanged)
        parent_layout.addWidget(self._composition_input)

        self._composition_map = map_data
        self._max_components = max_components

        hint = QtWidgets.QLabel(f"Max components: {max_components}")
        hint.setStyleSheet("color: gray;")
        parent_layout.addWidget(hint)

        self._composition_error_label = QtWidgets.QLabel("", self)
        self._composition_error_label.setStyleSheet("color: red; font-size: 12px;")
        self._composition_error_label.hide()
        parent_layout.addWidget(self._composition_error_label)

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

    def _setupRawInputs(self, parent_layout: QtWidgets.QVBoxLayout) -> None:
        method_map = self._config.get("raw", {}).get("method_map", [])
        symbols = self._config.get("symbol", [])
        descriptions = self._config.get("description", [])
        units = self._config.get("units", [])

        self._inputs_layout = QtWidgets.QGridLayout()
        row = 0

        for i, (param_name, control_type) in enumerate(method_map):
            label_name = symbols[i] if i < len(symbols) else param_name
            hint_text = descriptions[i] if i < len(descriptions) else param_name
            unit = units[i] if i < len(units) else ""

            label_text = label_name
            if unit:
                label_text += f" ({unit})"
            label = QtWidgets.QLabel(label_text)
            self._inputs_layout.addWidget(label, row, 0)

            if control_type == "element_id_input":
                container, spinbox = _buildSpinBoxWithHint(self, 1, 118, hint_text)
                self._inputs_layout.addWidget(container, row, 1)
                self._raw_widgets[param_name] = spinbox
            elif control_type == "int_input":
                container, spinbox = _buildSpinBoxWithHint(
                    self, INT32_MIN, INT32_MAX, hint_text
                )
                self._inputs_layout.addWidget(container, row, 1)
                self._raw_widgets[param_name] = spinbox
            elif control_type == "float_input":
                container, spinbox = _buildDoubleSpinBoxWithHint(
                    self, FLOAT_MIN, FLOAT_MAX, hint_text
                )
                self._inputs_layout.addWidget(container, row, 1)
                self._raw_widgets[param_name] = spinbox
            elif control_type == "element_symbol_input":
                widget = _buildSymbolInput(self, hint_text)
                self._inputs_layout.addWidget(widget, row, 1)
                self._raw_widgets[param_name] = widget
            elif control_type == "text_input":
                widget = _buildSymbolInput(self, hint_text)
                self._inputs_layout.addWidget(widget, row, 1)
                self._raw_widgets[param_name] = widget
            else:
                raise ValueError(f"Unknown input type: {control_type}")

            self._raw_types[param_name] = control_type
            row += 1

        parent_layout.addLayout(self._inputs_layout)

    def getInputs(self) -> dict:
        input_method = self._config.get("input_method", "raw")

        if input_method == "composition_tool" and self._composition_input:
            comp_str = self._composition_input.text().strip()
            if not comp_str:
                return {}
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

            return self._composition_tool.toArgumentMap(
                parsed, self._composition_map, use_atomic_number=True
            )
        else:
            result = {}
            method_map = self._config.get("raw", {}).get("method_map", [])
            for param_name, control_type in method_map:
                widget = self._raw_widgets.get(param_name)
                if widget is None:
                    continue

                extractor = _VALUE_EXTRACTORS.get(control_type)
                if extractor is None:
                    raise ValueError(f"Unknown input type: {control_type}")
                value = extractor(widget)
                if control_type == "element_symbol_input" and value is None:
                    raise ValueError(f"Invalid element symbol: {widget.text().strip()}")
                result[param_name] = value
            return result
