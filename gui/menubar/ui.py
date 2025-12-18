from PySide6.QtWidgets import (
    QMenu,
    QMenuBar,
)
from PySide6.QtCore import QCoreApplication

from PySide6.QtGui import (
    QAction,
)

class UiMenubar(object):

    def setupUi(self, menubar: QMenuBar):
        # 创建菜单
        self.menuFile = QMenu(menubar)
        self.menuFile.setObjectName(u"menuFile")
        
        self.menuEdit = QMenu(menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        
        self.menuView = QMenu(menubar)
        self.menuView.setObjectName(u"menuView")
        
        self.menuSession = QMenu(menubar)
        self.menuSession.setObjectName(u"menuSession")
        
        self.menuWindow = QMenu(menubar)
        self.menuWindow.setObjectName(u"menuWindow")
        
        self.menuData = QMenu(menubar)
        self.menuData.setObjectName(u"menuData")
        
        self.menuDatabase = QMenu(self.menuData)
        self.menuDatabase.setObjectName(u"menuDatabase")
        
        self.menuSimulation = QMenu(menubar)
        self.menuSimulation.setObjectName(u"menuSimulation")
        
        self.menuTools = QMenu(menubar)
        self.menuTools.setObjectName(u"menuTools")
        
        self.menuHelp = QMenu(menubar)
        self.menuHelp.setObjectName(u"menuHelp")

        # 创建动作
        ## File 菜单动作
        self.actionNew = QAction(menubar)
        self.actionNew.setObjectName(u"actionNew")
        
        self.actionOpen = QAction(menubar)
        self.actionOpen.setObjectName(u"actionOpen")
        
        self.actionClose = QAction(menubar)
        self.actionClose.setObjectName(u"actionClose")
        
        self.actionSave = QAction(menubar)
        self.actionSave.setObjectName(u"actionSave")
        
        self.actionSaveAs = QAction(menubar)
        self.actionSaveAs.setObjectName(u"actionSaveAs")
        
        self.actionImportFile = QAction(menubar)
        self.actionImportFile.setObjectName(u"actionImportFile")
        
        self.actionExportFile = QAction(menubar)
        self.actionExportFile.setObjectName(u"actionExportFile")
        
        self.actionPrint = QAction(menubar)
        self.actionPrint.setObjectName(u"actionPrint")
        
        self.actionExit = QAction(menubar)
        self.actionExit.setObjectName(u"actionExit")

        ## Edit 菜单动作
        self.actionUndo = QAction(menubar)
        self.actionUndo.setObjectName(u"actionUndo")
        
        self.actionRedo = QAction(menubar)
        self.actionRedo.setObjectName(u"actionRedo")
        
        self.actionCut = QAction(menubar)
        self.actionCut.setObjectName(u"actionCut")
        
        self.actionCopy = QAction(menubar)
        self.actionCopy.setObjectName(u"actionCopy")
        
        self.actionPaste = QAction(menubar)
        self.actionPaste.setObjectName(u"actionPaste")
        
        self.actionDelete = QAction(menubar)
        self.actionDelete.setObjectName(u"actionDelete")
        
        self.actionRename = QAction(menubar)
        self.actionRename.setObjectName(u"actionRename")
        
        self.actionMoveUp = QAction(menubar)
        self.actionMoveUp.setObjectName(u"actionMoveUp")
        
        self.actionMoveDown = QAction(menubar)
        self.actionMoveDown.setObjectName(u"actionMoveDown")
        
        self.actionShow = QAction(menubar)
        self.actionShow.setObjectName(u"actionShow")
        
        self.actionHide = QAction(menubar)
        self.actionHide.setObjectName(u"actionHide")

        ## View 菜单动作
        self.actionZoomIn = QAction(menubar)
        self.actionZoomIn.setObjectName(u"actionZoomIn")
        
        self.actionZoomOut = QAction(menubar)
        self.actionZoomOut.setObjectName(u"actionZoomOut")
        
        self.actionFilter = QAction(menubar)
        self.actionFilter.setObjectName(u"actionFilter")
        
        self.actionReloadData = QAction(menubar)
        self.actionReloadData.setObjectName(u"actionReloadData")

        ## Database 子菜单动作
        self.actionImportDatabase = QAction(menubar)
        self.actionImportDatabase.setObjectName(u"actionImportDatabase")
        
        self.actionBackupDatabase = QAction(menubar)
        self.actionBackupDatabase.setObjectName(u"actionBackupDatabase")
        
        self.actionRecoveryDatabase = QAction(menubar)
        self.actionRecoveryDatabase.setObjectName(u"actionRecoveryDatabase")

        ## Window 菜单动作
        self.actionFullScreen = QAction(menubar)
        self.actionFullScreen.setObjectName(u"actionFullScreen")

        ## Help 菜单动作
        self.actionManual = QAction(menubar)
        self.actionManual.setObjectName(u"actionManual")
        
        self.actionSettings = QAction(menubar)
        self.actionSettings.setObjectName(u"actionSettings")
        
        self.actionAbout = QAction(menubar)
        self.actionAbout.setObjectName(u"actionAbout")

        # 将菜单添加到菜单栏
        menubar.addAction(self.menuFile.menuAction())
        menubar.addAction(self.menuEdit.menuAction())
        menubar.addAction(self.menuView.menuAction())
        menubar.addAction(self.menuSession.menuAction())
        menubar.addAction(self.menuSimulation.menuAction())
        menubar.addAction(self.menuData.menuAction())
        menubar.addAction(self.menuWindow.menuAction())
        menubar.addAction(self.menuTools.menuAction())
        menubar.addAction(self.menuHelp.menuAction())

        # 将动作添加到对应菜单
        ## File 菜单
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionImportFile)
        self.menuFile.addAction(self.actionExportFile)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionPrint)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)

        ## Edit 菜单
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addAction(self.actionDelete)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionRename)
        self.menuEdit.addAction(self.actionMoveUp)
        self.menuEdit.addAction(self.actionMoveDown)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionShow)
        self.menuEdit.addAction(self.actionHide)

        ## View 菜单
        self.menuView.addAction(self.actionZoomIn)
        self.menuView.addAction(self.actionZoomOut)
        self.menuView.addAction(self.actionFilter)
        self.menuView.addAction(self.actionReloadData)

        ## Window 菜单
        self.menuWindow.addAction(self.actionFullScreen)

        ## Help 菜单
        self.menuHelp.addAction(self.actionManual)
        self.menuHelp.addAction(self.actionSettings)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)

        ## Data 菜单
        self.menuData.addAction(self.actionFilter)
        self.menuData.addAction(self.menuDatabase.menuAction())
        self.menuData.addAction(self.actionReloadData)
        
        ## Database 子菜单
        self.menuDatabase.addAction(self.actionImportDatabase)
        self.menuDatabase.addAction(self.actionBackupDatabase)
        self.menuDatabase.addAction(self.actionRecoveryDatabase)

    def retranslateUi(self, menubar: QMenuBar):
        # 设置菜单标题
        self.menuFile.setTitle(QCoreApplication.translate("menubar", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("menubar", u"Edit", None))
        self.menuView.setTitle(QCoreApplication.translate("menubar", u"View", None))
        self.menuSession.setTitle(QCoreApplication.translate("menubar", u"Session", None))
        self.menuWindow.setTitle(QCoreApplication.translate("menubar", u"Window", None))
        self.menuData.setTitle(QCoreApplication.translate("menubar", u"Data", None))
        self.menuDatabase.setTitle(QCoreApplication.translate("menubar", u"Database", None))
        self.menuSimulation.setTitle(QCoreApplication.translate("menubar", u"Simulation", None))
        self.menuTools.setTitle(QCoreApplication.translate("menubar", u"Tools", None))
        self.menuHelp.setTitle(QCoreApplication.translate("menubar", u"Help", None))

        # 设置动作文本
        ## File 菜单动作
        self.actionNew.setText(QCoreApplication.translate("menubar", u"New", None))
        self.actionOpen.setText(QCoreApplication.translate("menubar", u"Open", None))
        self.actionClose.setText(QCoreApplication.translate("menubar", u"Close", None))
        self.actionSave.setText(QCoreApplication.translate("menubar", u"Save", None))
        self.actionSaveAs.setText(QCoreApplication.translate("menubar", u"Save As", None))
        self.actionImportFile.setText(QCoreApplication.translate("menubar", u"Import", None))
        self.actionExportFile.setText(QCoreApplication.translate("menubar", u"Export", None))
        self.actionPrint.setText(QCoreApplication.translate("menubar", u"Print", None))
        self.actionExit.setText(QCoreApplication.translate("menubar", u"Exit", None))

        ## Edit 菜单动作
        self.actionUndo.setText(QCoreApplication.translate("menubar", u"Undo", None))
        self.actionRedo.setText(QCoreApplication.translate("menubar", u"Redo", None))
        self.actionCut.setText(QCoreApplication.translate("menubar", u"Cut", None))
        self.actionCopy.setText(QCoreApplication.translate("menubar", u"Copy", None))
        self.actionPaste.setText(QCoreApplication.translate("menubar", u"Paste", None))
        self.actionDelete.setText(QCoreApplication.translate("menubar", u"Delete", None))
        self.actionRename.setText(QCoreApplication.translate("menubar", u"Rename", None))
        self.actionMoveUp.setText(QCoreApplication.translate("menubar", u"Move Up", None))
        self.actionMoveDown.setText(QCoreApplication.translate("menubar", u"Move Down", None))
        self.actionShow.setText(QCoreApplication.translate("menubar", u"Show", None))
        self.actionHide.setText(QCoreApplication.translate("menubar", u"Hide", None))

        ## View 菜单动作
        self.actionZoomIn.setText(QCoreApplication.translate("menubar", u"Zoom In", None))
        self.actionZoomOut.setText(QCoreApplication.translate("menubar", u"Zoom Out", None))
        self.actionFilter.setText(QCoreApplication.translate("menubar", u"Filter", None))
        self.actionReloadData.setText(QCoreApplication.translate("menubar", u"Reload", None))

        ## Database 子菜单动作
        self.actionImportDatabase.setText(QCoreApplication.translate("menubar", u"Import", None))
        self.actionBackupDatabase.setText(QCoreApplication.translate("menubar", u"Backup", None))
        self.actionRecoveryDatabase.setText(QCoreApplication.translate("menubar", u"Recovery", None))

        ## Window 菜单动作
        self.actionFullScreen.setText(QCoreApplication.translate("menubar", u"Full Screen", None))

        ## Help 菜单动作
        self.actionManual.setText(QCoreApplication.translate("menubar", u"Manual", None))
        self.actionSettings.setText(QCoreApplication.translate("menubar", u"Settings", None))
        self.actionAbout.setText(QCoreApplication.translate("menubar", u"About", None))