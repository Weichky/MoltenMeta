from importlib.resources import files
from pathlib import Path

from resources import qtads


ADS_STYLESHEET_TEMPLATE = """
ads--CDockWidgetTab QLabel {{
    color: palette(Text) !important;
}}

ads--CDockWidgetTab[activeTab="true"] QLabel,
ads--CDockWidgetTab[focused="true"] QLabel {{
    color: palette(HighlightedText) !important;
}}

ads--CDockWidgetTab #dockWidgetTabLabel {{
    color: palette(Text) !important;
}}

ads--CDockWidgetTab[activeTab="true"] #dockWidgetTabLabel,
ads--CDockWidgetTab[focused="true"] #dockWidgetTabLabel {{
    color: palette(HighlightedText) !important;
}}

#tabsMenuButton {{
    qproperty-icon: url({resources_url}/tabs-menu-button.svg);
    qproperty-iconSize: 16px;
}}

#dockAreaCloseButton {{
    qproperty-icon: url({resources_url}/close-button.svg);
    qproperty-iconSize: 16px;
}}

#detachGroupButton {{
    qproperty-icon: url({resources_url}/detach-button.svg);
    qproperty-iconSize: 16px;
}}

#tabCloseButton {{
    margin-top: 2px;
    background: none;
    border: none;
    padding: 0px -2px;
    qproperty-icon: url({resources_url}/close-button.svg);
    qproperty-iconSize: 16px;
}}

#tabCloseButton:hover {{
    border: 1px solid rgba(0, 0, 0, 32);
    background: rgba(0, 0, 0, 16);
}}

#tabCloseButton:pressed {{
    background: rgba(0, 0, 0, 32);
}}

#autoHideTitleLabel {{
    padding-left: 4px;
    color: palette(WindowText);
}}

#dockAreaAutoHideButton {{
    qproperty-icon: url({resources_url}/vs-pin-button.svg);
    qproperty-iconSize: 16px;
}}

#dockAreaMinimizeButton {{
    qproperty-icon: url({resources_url}/minimize-button.svg);
    qproperty-iconSize: 16px;
}}

#dockAreaFloatButton {{
    qproperty-icon: url({resources_url}/maximize-button.svg);
    qproperty-iconSize: 16px;
}}

ads--CAutoHideTab {{
    qproperty-iconSize: 16px;
    background: none;
    border: none;
    padding-left: 2px;
    padding-right: 0px;
    text-align: center;
    min-height: 20px;
    padding-bottom: 2px;
}}

ads--CAutoHideSideBar {{
    background: palette(Window);
    border: none;
}}

ads--CResizeHandle {{
    background: palette(Window);
}}
"""


def getAdsStylesheet() -> str:
    images_dir = Path(files(qtads).joinpath("images"))
    resources_url = images_dir.as_posix()
    return ADS_STYLESHEET_TEMPLATE.format(resources_url=resources_url)
