from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QObject

class UiSettingsPage(QObject):
    def setupUi(self, settingsPage: QtWidgets.QWidget):
        if not settingsPage.objectName():
            settingsPage.setObjectName("settingsPage")

        self.root_layout = QtWidgets.QHBoxLayout(settingsPage)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # 创建可调整大小的分割器
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("settingsSplitter")
        
        # ===== 左侧导航面板 =====
        self.nav_panel = QtWidgets.QWidget()
        self.nav_panel.setObjectName("settingsNavPanel")
        self.nav_panel.setMinimumWidth(100)  # 设置最小宽度
        self.nav_panel.setMaximumWidth(300)  # 设置最大宽度
        
        self.nav_layout = QtWidgets.QVBoxLayout(self.nav_panel)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域用于侧边栏按钮
        self.nav_scroll = QtWidgets.QScrollArea()
        self.nav_scroll.setWidgetResizable(True)
        self.nav_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.nav_scroll.setObjectName("navScrollArea")
        
        # 创建包含按钮的容器widget
        self.nav_buttons_widget = QtWidgets.QWidget()
        self.nav_buttons_layout = QtWidgets.QVBoxLayout(self.nav_buttons_widget)
        self.nav_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_buttons_layout.setAlignment(QtCore.Qt.AlignTop)  # 顶部对齐
        
        # 添加导航项
        self.general_button = QtWidgets.QPushButton()
        self.general_button.setCheckable(True)
        self.general_button.setChecked(True)
        self.nav_buttons_layout.addWidget(self.general_button)
        
        # 将按钮容器设置为滚动区域的widget
        self.nav_scroll.setWidget(self.nav_buttons_widget)
        
        # 添加滚动区域到导航面板布局
        self.nav_layout.addWidget(self.nav_scroll)
        
        # ===== 中间主要内容区域 =====
        self.content_area = QtWidgets.QStackedWidget()
        self.content_area.setObjectName("settingsContentArea")
        
        # 创建通用设置页面
        self.general_page = self._create_general_page()
        self.content_area.addWidget(self.general_page)
        
        # 添加到分割器
        self.splitter.addWidget(self.nav_panel)
        self.splitter.addWidget(self.content_area)
        
        # 设置初始大小
        self.splitter.setSizes([150, 650])
        
        # 添加分割器到主布局
        self.root_layout.addWidget(self.splitter)
        
    def _create_general_page(self):
        """创建通用设置页面"""
        page = QtWidgets.QWidget()
        page.setObjectName("generalPage")
        layout = QtWidgets.QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 语言设置
        lang_group = QtWidgets.QGroupBox()
        lang_group.setObjectName("languageGroup")
        lang_layout = QtWidgets.QVBoxLayout(lang_group)
        
        self.lang_label = QtWidgets.QLabel()
        lang_layout.addWidget(self.lang_label)
        
        self.lang_combo = QtWidgets.QComboBox()
        self.lang_combo.setObjectName("languageCombo")
        self.lang_combo.addItem(self.tr("English"), "en")
        self.lang_combo.addItem(self.tr("Simplified Chinese"), "zh_CN")
        lang_layout.addWidget(self.lang_combo)
        
        lang_layout.addStretch()
        layout.addWidget(lang_group)
        layout.addStretch()
        
        return page
        
    def _connect_signals(self):
        """连接信号"""
        # 使用互斥按钮组确保只有一个按钮被选中
        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.addButton(self.general_button)
        self.button_group.setExclusive(True)
        
        self.general_button.clicked.connect(lambda: self.content_area.setCurrentIndex(0))
        
    def retranslateUi(self):
        """翻译界面文本"""
        # 导航按钮
        self.general_button.setText(self.tr("General"))
        
        # 通用设置页面
        self.lang_label.setText(self.tr("Language:"))
        
        # 清空并重新添加带翻译的选项
        self.lang_combo.clear()
        self.lang_combo.addItem(self.tr("English"), "en")
        self.lang_combo.addItem(self.tr("Simplified Chinese"), "zh_CN")
        
        # 组框标题
        for i in range(self.content_area.count()):
            widget = self.content_area.widget(i)
            if widget.objectName() == "generalPage":
                group = widget.findChild(QtWidgets.QGroupBox, "languageGroup")
                if group:
                    group.setTitle(self.tr("Language Settings"))