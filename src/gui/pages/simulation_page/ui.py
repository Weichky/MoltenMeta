from PySide6 import QtWidgets, QtCore


class UiSimulationPage:
    def setupUi(self, Form):
        Form.setObjectName("Form")

        main_layout = QtWidgets.QHBoxLayout(Form)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

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

        self.resultLabel = QtWidgets.QLabel("Result: --")
        self.resultLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.resultLabel.setMaximumHeight(30)

        self.resultTable = QtWidgets.QTableView()
        self.resultTable.setAlternatingRowColors(True)
        self.resultTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.resultTable.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        self.configureBtn = QtWidgets.QPushButton("Configure...")
        self.calculateBtn = QtWidgets.QPushButton("Calculate")

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.configureBtn)
        button_layout.addWidget(self.calculateBtn)

        self.statusLabel = QtWidgets.QLabel("")
        self.statusLabel.setStyleSheet("color: gray;")

        control_frame = QtWidgets.QFrame()
        control_frame.setFrameShape(QtWidgets.QFrame.Shape.Box)
        control_layout = QtWidgets.QVBoxLayout(control_frame)
        control_layout.setContentsMargins(8, 8, 8, 8)
        control_layout.setSpacing(4)
        control_layout.addLayout(form_layout)
        control_layout.addWidget(self.resultLabel)
        control_layout.addWidget(self.resultTable, stretch=1)
        control_layout.addLayout(button_layout)
        control_layout.addWidget(self.statusLabel)

        self.plotContainer = QtWidgets.QStackedWidget()

        plot_frame = QtWidgets.QFrame()
        plot_frame.setFrameShape(QtWidgets.QFrame.Shape.Box)
        plot_layout = QtWidgets.QVBoxLayout(plot_frame)
        plot_layout.setContentsMargins(2, 2, 2, 2)
        plot_layout.addWidget(self.plotContainer)

        main_layout.addWidget(control_frame, stretch=1)
        main_layout.addWidget(plot_frame, stretch=3)

    def retranslateUi(self, Form):
        Form.setWindowTitle("Simulation")
        self.categoryLabel.setText("Category:")
        self.moduleLabel.setText("Module:")
        self.methodLabel.setText("Method:")
        self.configureBtn.setText("Configure...")
        self.calculateBtn.setText("Calculate")
