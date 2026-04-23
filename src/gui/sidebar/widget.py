from pathlib import Path

from PySide6.QtWidgets import QDockWidget
from PySide6.QtCore import QEvent, QObject
from PySide6.QtGui import QIcon
from importlib.resources import files

from i18n import I18nService

from .ui import UiSidebar

ICONS_PATH = files("resources.images.svg")


class ResizeEventFilter(QObject):
    def __init__(self, sidebar):
        super().__init__()
        self.sidebar = sidebar

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.sidebar._adjustSidebarSize()
        return False


class SidebarWidget(QDockWidget):
    def __init__(self, parent, i18n_service: I18nService):
        super().__init__(parent)
        self.i18n_service = i18n_service
        self._is_collapsed = False
        self.ui = UiSidebar()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)

        self._setupIcons()
        self._setupToggleButton()

        # Install event filter to listen for parent window size changes
        self.resize_event_filter = ResizeEventFilter(self)
        parent.installEventFilter(self.resize_event_filter)

        # Initial size adjustment
        self._adjustSidebarSize()

        self.retranslateUi()

        # i18n
        self.i18n_service.language_changed.connect(self.retranslateUi)

    def _setupIcons(self):
        icons_path = Path(ICONS_PATH)
        self.ui.homeButton.setIcon(QIcon(str(icons_path / "home.svg")))
        self.ui.simulationButton.setIcon(QIcon(str(icons_path / "experiment.svg")))
        self.ui.settingsButton.setIcon(QIcon(str(icons_path / "config.svg")))
        self.ui.dataButton.setIcon(QIcon(str(icons_path / "database_code.svg")))
        self._updateToggleIcon()

    def _setupToggleButton(self):
        self.ui.toggleButton.toggled.connect(self._onToggle)

    def _onToggle(self, checked: bool):
        self._is_collapsed = checked
        self._updateToggleIcon()
        self._updateButtonStyles()
        self._adjustSidebarSize()
        tooltip = self.tr("Expand sidebar") if checked else self.tr("Collapse sidebar")
        self.ui.toggleButton.setToolTip(tooltip)

    def _updateToggleIcon(self):
        icons_path = Path(ICONS_PATH)
        icon_name = "expand_left.svg" if self._is_collapsed else "expand_right.svg"
        self.ui.toggleButton.setIcon(QIcon(str(icons_path / icon_name)))

    def _updateButtonStyles(self):
        if self._is_collapsed:
            buttons = [
                self.ui.homeButton,
                self.ui.simulationButton,
                self.ui.settingsButton,
                self.ui.dataButton,
            ]
            for btn in buttons:
                btn.setText("")
        else:
            self.ui.retranslateUi(self)

    def _adjustSidebarSize(self):
        self.ui.adjustSidebarSize(self, self._is_collapsed)

    def setActivePage(self, page_key: str) -> None:
        button_map = {
            "home": self.ui.homeButton,
            "simulation": self.ui.simulationButton,
            "data": self.ui.dataButton,
            "settings": self.ui.settingsButton,
        }
        button = button_map.get(page_key)
        if button:
            button.setChecked(True)

    def retranslateUi(self):
        self.ui.retranslateUi(self)
        self.ui.toggleButton.setToolTip(self.tr("Collapse sidebar"))
