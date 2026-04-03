from PySide6 import QtWidgets, QtCore


class UiSimulationPage:
    def setupUi(self, Form):
        Form.setObjectName("Form")

        main_layout = QtWidgets.QHBoxLayout(Form)

        control_widget = QtWidgets.QWidget()
        control_layout = QtWidgets.QVBoxLayout(control_widget)
        control_layout.setContentsMargins(8, 8, 8, 8)

        form_layout = QtWidgets.QFormLayout()

        self.categoryLabel = QtWidgets.QLabel("Category:")
        self.categoryCombo = QtWidgets.QComboBox()
        form_layout.addRow(self.categoryLabel, self.categoryCombo)

        self.moduleLabel = QtWidgets.QLabel("Module:")
        self.moduleCombo = QtWidgets.QComboBox()
        form_layout.addRow(self.moduleLabel, self.moduleCombo)

        self.methodLabel = QtWidgets.QLabel("Method:")
        self.methodCombo = QtWidgets.QComboBox()
        form_layout.addRow(self.methodLabel, self.methodCombo)

        control_layout.addLayout(form_layout)

        self.resultLabel = QtWidgets.QLabel("Result: --")
        self.resultLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(self.resultLabel)

        spacer = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        control_layout.addItem(spacer)

        button_layout = QtWidgets.QHBoxLayout()
        self.configureBtn = QtWidgets.QPushButton("Configure...")
        self.calculateBtn = QtWidgets.QPushButton("Calculate")
        button_layout.addWidget(self.configureBtn)
        button_layout.addWidget(self.calculateBtn)
        control_layout.addLayout(button_layout)

        self.statusLabel = QtWidgets.QLabel("")
        self.statusLabel.setStyleSheet("color: gray;")
        control_layout.addWidget(self.statusLabel)

        self.plotContainer = QtWidgets.QStackedWidget()
        self.plotContainer.setMinimumWidth(500)

        main_layout.addWidget(control_widget, stretch=1)
        main_layout.addWidget(self.plotContainer, stretch=3)

    def retranslateUi(self, Form):
        Form.setWindowTitle("Simulation")
        self.categoryLabel.setText("Category:")
        self.moduleLabel.setText("Module:")
        self.methodLabel.setText("Method:")
        self.configureBtn.setText("Configure...")
        self.calculateBtn.setText("Calculate")
