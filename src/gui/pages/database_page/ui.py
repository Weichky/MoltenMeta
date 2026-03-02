from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QObject

class UiDatabasePage(QObject):
    def setupUi(self, databasePage: QtWidgets.QWidget):
        if not databasePage.objectName():
            databasePage.setObjectName("databasePage")

            self.rootLayout = QtWidgets.QVBoxLayout(databasePage)
            