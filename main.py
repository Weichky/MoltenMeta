#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLocale, QTranslator, QLibraryInfo
from gui.main_window import MainWindow


def load_translator(app, locale_name="en"):
    """加载翻译文件"""
    translator = QTranslator()
    
    # 构建翻译文件路径
    ts_file = os.path.join(os.path.dirname(__file__), "i18n", locale_name, "settings.qm")
    
    if os.path.exists(ts_file):
        if translator.load(ts_file):
            app.installTranslator(translator)
            print(f"Loaded translation: {ts_file}")
        else:
            print(f"Failed to load translation: {ts_file}")
    else:
        print(f"Translation file not found: {ts_file}")
    
    return translator


def main():
    app = QApplication(sys.argv)
    
    # 默认使用系统语言或设置为中文
    locale = QLocale.system().name()  #  "zh_CN" 或 "en_US" 等
    
    # 加载翻译
    translator = load_translator(app, locale)  # 目前没有配置文件，暂时按照系统语言加载
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()