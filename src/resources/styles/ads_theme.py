from importlib.resources import files

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
    qproperty-icon: url({resources_path}/tabs-menu-button.svg);
    qproperty-iconSize: 16px;
}}

#dockAreaCloseButton {{
    qproperty-icon: url({resources_path}/close-button.svg);
    qproperty-iconSize: 16px;
}}

#detachGroupButton {{
    qproperty-icon: url({resources_path}/detach-button.svg);
    qproperty-iconSize: 16px;
}}

#tabCloseButton {{
    margin-top: 2px;
    background: none;
    border: none;
    padding: 0px -2px;
    qproperty-icon: url({resources_path}/close-button.svg);
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
    qproperty-icon: url({resources_path}/vs-pin-button.svg);
    qproperty-iconSize: 16px;
}}

#dockAreaMinimizeButton {{
    qproperty-icon: url({resources_path}/minimize-button.svg);
    qproperty-iconSize: 16px;
}}

#dockAreaFloatButton {{
    qproperty-icon: url({resources_path}/maximize-button.svg);
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


def get_ads_stylesheet() -> str:
    images_dir = files(qtads).joinpath("images")
    return ADS_STYLESHEET_TEMPLATE.format(resources_path=str(images_dir))
