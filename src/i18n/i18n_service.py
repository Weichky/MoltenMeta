from PySide6.QtCore import QTranslator, QObject, Signal

from core.fio import getLanguagePackagePath

from catalog import isSupportedLanguage

class I18nService(QObject):
    language_changed = Signal()

    def __init__(self, app):
        super().__init__(app)

        self.app = app
        self.translator = None

    def setLanguage(self, language: str):
        if not isSupportedLanguage(language):
            raise ValueError(f"Language {language} not supported")

        if self.translator:
            self.app.removeTranslator(self.translator)

        if language == "en":
            self.translator = None
            self.language_changed.emit()
            return

        self.translator = QTranslator(self.app)
        self.translator.load(getLanguagePackagePath(language))
        self.app.installTranslator(self.translator)

        self.language_changed.emit()
