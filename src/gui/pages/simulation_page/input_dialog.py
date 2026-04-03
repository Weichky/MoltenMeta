from PySide6 import QtWidgets

from .composition_tool import CompositionTool


class InputDialog(QtWidgets.QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Configure Input")
        self.setMinimumWidth(400)
        self._config = config
        self._composition_tool = CompositionTool()
        self._inputs_layout = None
        self._raw_widgets: dict[str, QtWidgets.QWidget] = {}
        self._composition_input: QtWidgets.QLineEdit | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)

        input_method = self._config.get("input_method", "raw")

        if input_method == "composition_tool":
            self._setup_composition_tool(layout)
        else:
            self._setup_raw_inputs(layout)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _setup_composition_tool(self, parent_layout: QtWidgets.QVBoxLayout) -> None:
        comp_config = self._config["composition_tool"]
        map_data = comp_config["map"]

        label = QtWidgets.QLabel("Mole fraction input (e.g. Al90Si10)")
        parent_layout.addWidget(label)

        self._composition_input = QtWidgets.QLineEdit()
        self._composition_input.setPlaceholderText("Al90Si10")
        parent_layout.addWidget(self._composition_input)

        self._composition_map = map_data

        hint = QtWidgets.QLabel(
            f"Max components: {comp_config.get('max_components', 2)}"
        )
        hint.setStyleSheet("color: gray;")
        parent_layout.addWidget(hint)

    def _setup_raw_inputs(self, parent_layout: QtWidgets.QVBoxLayout) -> None:
        method_map = self._config.get("raw", {}).get("method_map", [])
        descriptions = self._config.get("inputs", {}).get("description", [])
        units = self._config.get("inputs", {}).get("unit", [])

        self._inputs_layout = QtWidgets.QGridLayout()
        row = 0

        for i, (param_name, control_type) in enumerate(method_map):
            desc = descriptions[i] if i < len(descriptions) else param_name
            unit = units[i] if i < len(units) else ""

            label_text = desc
            if unit:
                label_text += f" ({unit})"
            label = QtWidgets.QLabel(label_text)
            self._inputs_layout.addWidget(label, row, 0)

            if control_type == "element_input":
                widget = QtWidgets.QSpinBox()
                widget.setMinimum(1)
                widget.setMaximum(118)
            elif control_type == "int_input":
                widget = QtWidgets.QSpinBox()
                widget.setMinimum(0)
                widget.setMaximum(9999)
            else:
                widget = QtWidgets.QDoubleSpinBox()
                widget.setMinimum(-9999)
                widget.setMaximum(9999)
                widget.setDecimals(4)

            self._inputs_layout.addWidget(widget, row, 1)
            self._raw_widgets[param_name] = widget

            row += 1

        parent_layout.addLayout(self._inputs_layout)

    def get_inputs(self) -> dict:
        input_method = self._config.get("input_method", "raw")

        if input_method == "composition_tool" and self._composition_input:
            comp_str = self._composition_input.text().strip()
            parsed = self._composition_tool.parse(comp_str)
            if parsed:
                return self._composition_tool.to_argument_map(
                    parsed, self._composition_map, use_atomic_number=True
                )
            return {}
        else:
            result = {}
            method_map = self._config.get("raw", {}).get("method_map", [])
            for i, (param_name, control_type) in enumerate(method_map):
                widget = self._raw_widgets.get(param_name)
                if widget is None:
                    continue

                if isinstance(widget, QtWidgets.QLineEdit):
                    text = widget.text().strip()
                    try:
                        if "." in text:
                            result[param_name] = float(text)
                        else:
                            result[param_name] = int(text)
                    except ValueError:
                        result[param_name] = text
                elif isinstance(widget, QtWidgets.QSpinBox):
                    result[param_name] = widget.value()
                elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                    result[param_name] = widget.value()
            return result
