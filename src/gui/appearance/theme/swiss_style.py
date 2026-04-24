from PySide6.QtWidgets import QApplication


DENSITY_SCALE_OPTIONS = {
    "50%": 0.5,
    "75%": 0.75,
    "100%": 1.0,
    "125%": 1.25,
    "150%": 1.5,
}


def _generateScaledStylesheet(
    scale: float, primary_color: str = "#C62828", secondary_color: str = "#1A1A1A"
) -> str:
    base_font = 13
    base_btn_height = 28
    base_input_height = 28

    scaled_font = int(base_font * scale)
    scaled_btn_height = max(24, int(base_btn_height * scale))
    scaled_input_height = max(24, int(base_input_height * scale))
    scaled_padding = int(6 * scale)

    return f"""
/* === General === */
QWidget {{
  background-color: #FFFFFF;
  color: #1A1A1A;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: {scaled_font}px;
}}

/* === Hero Section (HomePage) === */
QLabel#heroTitle {{
  font-size: {int(56 * scale)}px;
  font-weight: 700;
  color: #1A1A1A;
  line-height: 1.0;
  background: transparent;
  letter-spacing: -1px;
}}

QLabel#heroSubtitle {{
  font-size: {int(15 * scale)}px;
  font-weight: 400;
  color: #616161;
  line-height: 1.4;
  background: transparent;
  letter-spacing: 0.2px;
}}

QLabel#sectionLabel {{
  font-size: {int(10 * scale)}px;
  font-weight: 600;
  color: #9E9E9E;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  background: transparent;
}}

QLabel#description {{
  font-size: {int(12 * scale)}px;
  font-weight: 400;
  color: #9E9E9E;
  line-height: 1.6;
  background: transparent;
}}

/* Section divider line */
QFrame#sectionLine {{
  background-color: #E0E0E0;
  border: none;
}}

QFrame#dividerLine {{
  background-color: #E0E0E0;
  border: none;
}}

/* === Buttons (Compact) === */
QPushButton {{
  background-color: #F5F5F5;
  color: #1A1A1A;
  border: none;
  border-radius: 3px;
  padding: {scaled_padding}px {int(14 * scale)}px;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: {int(12 * scale)}px;
  font-weight: 500;
  min-height: {scaled_btn_height}px;
  min-width: {int(56 * scale)}px;
}}

QPushButton:hover {{
  background-color: #E8E8E8;
}}

QPushButton:pressed {{
  background-color: #DCDCDC;
}}

QPushButton:disabled {{
  color: #9E9E9E;
  background-color: #F5F5F5;
}}

/* Primary Button */
QPushButton[theme="primary"] {{
  background-color: {primary_color};
  color: #FFFFFF;
}}

QPushButton[theme="primary"]:hover {{
  background-color: {primary_color};
  border: 1px solid {primary_color};
  opacity: 0.8;
}}

QPushButton[theme="primary"]:pressed {{
  background-color: {primary_color};
  opacity: 0.6;
}}

/* Secondary Button */
QPushButton[theme="secondary"] {{
  background-color: transparent;
  border: 1px solid {secondary_color};
  color: {secondary_color};
}}

QPushButton[theme="secondary"]:hover {{
  background-color: {secondary_color};
  color: #FFFFFF;
}}

/* Text Button */
QPushButton[theme="text"] {{
  background-color: transparent;
  border: none;
  color: {primary_color};
  text-decoration: underline;
}}

QPushButton[theme="text"]:hover {{
  color: {primary_color};
  opacity: 0.7;
}}

/* Sidebar Background */
QDockWidget {{
  background-color: #E8E8E8;
  border: none;
}}

QDockWidget > QWidget {{
  background-color: #E8E8E8;
}}

/* Sidebar Buttons (Compact) */
QPushButton#sidebarButton {{
  background-color: rgba(250, 250, 250, 200);
  border: none;
  border-radius: 0;
  border-left: 3px solid transparent;
  text-align: left;
  padding-left: {int(14 * scale)}px;
  font-size: {int(12 * scale)}px;
  font-weight: 500;
  min-height: {int(36 * scale)}px;
  color: #616161;
}}

QPushButton#sidebarButton:hover {{
  background-color: rgba(248, 248, 248, 220);
  color: #1A1A1A;
}}

QPushButton#sidebarButton:checked {{
  background-color: {primary_color};
  color: #FFFFFF;
  border-left-color: {primary_color};
}}

/* === Tile Button (2x2 Grid) === */
QPushButton#tileButton {{
  background-color: rgba(250, 250, 250, 120);
  border: 1px solid rgba(224, 224, 224, 180);
  border-radius: 4px;
  padding: {int(24 * scale)}px {int(28 * scale)}px;
  min-width: {int(70 * scale)}px;
  min-height: {int(40 * scale)}px;
  font-size: {int(12 * scale)}px;
  font-weight: normal;
  color: #1A1A1A;
  text-align: center;
}}

QPushButton#tileButton:hover {{
  background-color: rgba(250, 250, 250, 160);
  border-color: {primary_color};
  border-width: 2px;
}}

QPushButton#tileButton:pressed {{
  background-color: #F0F0F0;
}}

/* === Tick Mark / Ruler Decoration === */
QFrame#tickMark {{
  background-color: transparent;
  border: none;
}}

QFrame#tickLine {{
  background-color: #E0E0E0;
  border: none;
}}

QFrame#rulerMark {{
  background-color: transparent;
  border: none;
  border-left: 1px solid #E0E0E0;
}}

QFrame#cornerAccent {{
  background-color: {primary_color};
  border: none;
}}

/* === Input Widgets (Compact) === */
QLineEdit,
QSpinBox,
QDoubleSpinBox {{
  min-height: {scaled_input_height}px;
  border: 1px solid #E0E0E0;
  border-radius: 4px;
  padding: 0 {int(10 * scale)}px;
  font-size: {int(12 * scale)}px;
  background-color: #FFFFFF;
  color: #1A1A1A;
}}

QLineEdit:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {{
  border: 2px solid {primary_color};
  padding: 0 {int(9 * scale)}px;
}}

QLineEdit:disabled,
QSpinBox:disabled,
QDoubleSpinBox:disabled,
QComboBox:disabled {{
  background-color: #F5F5F5;
  color: #9E9E9E;
}}

/* === ComboBox === */
QComboBox {{
  min-height: {scaled_input_height}px;
  border: 1px solid #E0E0E0;
  border-radius: 4px;
  padding: 0 {int(10 * scale)}px;
  font-size: {int(12 * scale)}px;
  background-color: #FFFFFF;
  color: #1A1A1A;
}}

QComboBox:focus {{
  border: 2px solid {primary_color};
  padding: 0 {int(9 * scale)}px;
}}

QComboBox::drop-down {{
  border: none;
  width: {int(24 * scale)}px;
}}

QComboBox::down-arrow {{
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 5px solid #616161;
  top: 1px;
}}

QComboBox QAbstractItemView {{
  background-color: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 4px;
  selection-background-color: {primary_color};
  selection-color: #FFFFFF;
  outline: none;
}}

QComboBox::item:selected {{
  background-color: {primary_color};
  color: #FFFFFF;
}}

QComboBox::item:hover {{
  background-color: rgba(248, 248, 248, 220);
}}

/* === Toggle Button === */
QPushButton#toggleButton {{
  background-color: rgba(250, 250, 250, 200);
  border: none;
  border-radius: 0;
  text-align: center;
  font-size: {int(12 * scale)}px;
  min-height: {int(36 * scale)}px;
  color: #616161;
}}

QPushButton#toggleButton:hover {{
  background-color: rgba(248, 248, 248, 220);
  color: #1A1A1A;
}}

/* === Group Box === */
QGroupBox {{
  border: none;
  margin-top: {int(20 * scale)}px;
}}

QGroupBox::title {{
  font-size: {int(10 * scale)}px;
  font-weight: 600;
  color: #9E9E9E;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: {int(12 * scale)}px;
}}

/* === Card Frame === */
QFrame#card {{
  background-color: #FAFAFA;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  padding: {int(16 * scale)}px;
}}

/* === Tab Widget === */
QTabWidget::pane {{
  border: none;
  background-color: transparent;
}}

QTabBar::tab {{
  font-size: {int(12 * scale)}px;
  font-weight: 500;
  padding: {int(6 * scale)}px {int(14 * scale)}px;
  color: #616161;
  background-color: transparent;
  border: none;
  border-bottom: 2px solid transparent;
}}

QTabBar::tab:selected {{
  color: {primary_color};
  border-bottom: 2px solid {primary_color};
}}

QTabBar::tab:hover:!selected {{
  color: #1A1A1A;
}}

/* === Menu === */
QMenu {{
  background-color: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 4px;
  padding: {int(4 * scale)}px 0;
}}

QMenu::item {{
  padding: {int(6 * scale)}px {int(14 * scale)}px;
  font-size: {int(12 * scale)}px;
}}

QMenu::item:selected {{
  background-color: #F5F5F5;
}}

/* === Tool Tip === */
QToolTip {{
  background-color: #1A1A1A;
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  padding: {int(6 * scale)}px {int(10 * scale)}px;
  font-size: {int(11 * scale)}px;
}}

/* === Tree/Table === */
QTreeWidget,
QTableWidget {{
  background-color: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 4px;
  gridline-color: #F0F0F0;
}}

QTreeWidget::item,
QTableWidget::item {{
  padding: {int(6 * scale)}px;
}}

QTreeWidget::item:selected,
QTableWidget::item:selected {{
  background-color: {primary_color};
  color: #FFFFFF;
}}

/* === List Widget === */
QListWidget {{
  background-color: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 4px;
}}

QListWidget::item {{
  padding: {int(8 * scale)}px {int(12 * scale)}px;
}}

QListWidget::item:selected {{
  background-color: {primary_color};
  color: #FFFFFF;
}}

/* === Scrollbar === */
QScrollBar:vertical {{
  width: {int(6 * scale)}px;
  background: transparent;
}}

QScrollBar::handle:vertical {{
  background: #E0E0E0;
  border-radius: 3px;
  min-height: {int(24 * scale)}px;
}}

QScrollBar::handle:vertical:hover {{
  background: #BDBDBD;
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
  height: 0;
}}

QScrollBar:horizontal {{
  height: {int(6 * scale)}px;
  background: transparent;
}}

QScrollBar::handle:horizontal {{
  background: #E0E0E0;
  border-radius: 3px;
  min-width: {int(24 * scale)}px;
}}

QScrollBar::handle:horizontal:hover {{
  background: #BDBDBD;
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
  width: 0;
}}
"""


class SwissStyle:
    _current_scale = 1.0

    @staticmethod
    def getScaleOptions() -> list[str]:
        return list(DENSITY_SCALE_OPTIONS.keys())

    @staticmethod
    def getScale(scale_name: str) -> float:
        return DENSITY_SCALE_OPTIONS.get(scale_name, 1.0)

    @staticmethod
    def getCurrentScale() -> float:
        return SwissStyle._current_scale

    @staticmethod
    def getStylesheet(
        scale_name: str | None = None,
        primary_color: str = "#C62828",
        secondary_color: str = "#1A1A1A",
    ) -> str:
        if scale_name:
            SwissStyle._current_scale = DENSITY_SCALE_OPTIONS.get(scale_name, 1.0)
        return _generateScaledStylesheet(
            SwissStyle._current_scale, primary_color, secondary_color
        )

    @staticmethod
    def apply(
        app: QApplication,
        scale_name: str | None = None,
        primary_color: str = "#C62828",
        secondary_color: str = "#1A1A1A",
    ) -> None:
        stylesheet = SwissStyle.getStylesheet(
            scale_name, primary_color, secondary_color
        )
        app.setStyleSheet(stylesheet)
