from qt_material import (
    apply_stylesheet,
    list_themes
)
def applyStyleSheet(app: 'QApplication', themeXML: str, scheme: str) -> None:
    apply_stylesheet(app, theme = themeXML, invert_secondary = scheme == "light")

def getThemeList() -> list[str]:
    return list_themes()