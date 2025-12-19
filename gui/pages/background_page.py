from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QCoreApplication

from gui.pages.workspace import Workspace

class BackgroundPage(object):
    def setupUi(self, workspace: Workspace):
        self.label = QtWidgets.QLabel(workspace)
        self.label.setObjectName("backgroundLabel")
    
    def retranslateUi(self):
        self.label.setText(QCoreApplication.translate("MainWindow", u"Background", None))