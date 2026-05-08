from datetime import datetime
from pathlib import Path

from PySide6 import QtWidgets

from core.platform import getRuntimePath


SUPPORTED_FORMATS = ["png", "pdf", "svg", "eps"]

FORMAT_LABELS = {
    "png": "PNG (*.png)",
    "pdf": "PDF (*.pdf)",
    "svg": "SVG (*.svg)",
    "eps": "EPS (*.eps)",
}


def _defaultDirectory() -> Path:
    output_dir = getRuntimePath() / "output" / "pics"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _defaultFilename() -> str:
    return f"moltenmeta_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


class ExportDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Export Plot")
        self.setMinimumWidth(400)
        self._setupUi()

    def _setupUi(self) -> None:
        layout = QtWidgets.QFormLayout(self)

        self.formatCombo = QtWidgets.QComboBox()
        for fmt in SUPPORTED_FORMATS:
            self.formatCombo.addItem(FORMAT_LABELS[fmt], fmt)
        self.formatCombo.setCurrentIndex(0)
        self.formatCombo.currentIndexChanged.connect(self._onFormatChanged)
        layout.addRow("Format:", self.formatCombo)

        self.dpiSpin = QtWidgets.QSpinBox()
        self.dpiSpin.setMinimum(72)
        self.dpiSpin.setMaximum(600)
        self.dpiSpin.setValue(300)
        self.dpiSpin.setSuffix(" dpi")
        layout.addRow("DPI:", self.dpiSpin)

        path_layout = QtWidgets.QHBoxLayout()
        self.pathEdit = QtWidgets.QLineEdit()
        self.pathEdit.setPlaceholderText("Select location...")
        self.pathEdit.setReadOnly(True)
        path_layout.addWidget(self.pathEdit, stretch=1)

        self.browseBtn = QtWidgets.QPushButton("Browse...")
        self.browseBtn.clicked.connect(self._onBrowseClicked)
        path_layout.addWidget(self.browseBtn)
        layout.addRow("Location:", path_layout)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow("", button_box)

    def _onFormatChanged(self) -> None:
        if self.pathEdit.text().strip():
            old_ext = self._currentExtension()
            new_ext = self.formatCombo.currentData()
            if old_ext and new_ext:
                old_path = Path(self.pathEdit.text().strip())
                new_path = old_path.with_suffix(f".{new_ext}")
                self.pathEdit.setText(str(new_path))

    def _currentExtension(self) -> str | None:
        path = self.pathEdit.text().strip()
        if path:
            return Path(path).suffix.lstrip(".")
        return None

    def _onBrowseClicked(self) -> None:
        fmt = self.formatCombo.currentData()
        default_dir = _defaultDirectory()
        default_file = f"{_defaultFilename()}.{fmt}"
        filters = f"{FORMAT_LABELS[fmt]};;All Files (*.*)"
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.tr("Save Plot"),
            str(default_dir / default_file),
            filters,
        )
        if file_path:
            self.pathEdit.setText(file_path)

    def getExportInfo(self) -> tuple[str, str, int]:
        fmt = self.formatCombo.currentData()
        path = self.pathEdit.text().strip()
        dpi = self.dpiSpin.value()
        return path, fmt, dpi

    def accept(self) -> None:
        path, _, _ = self.getExportInfo()
        if not path:
            QtWidgets.QMessageBox.warning(
                self,
                self.tr("No Location"),
                self.tr("Please select a location to save the plot."),
            )
            return
        super().accept()