from PySide6.QtCore import QTranslator, QObject, Signal

from core.fio import getLanguagePackagePath

from catalog import isSupportedLanguage

_i18nService: _I18nService | None = None

class _I18nService(QObject):
    languageChanged = Signal()

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
            self.languageChanged.emit()
            return
        
        self.translator = QTranslator(self.app)
        self.translator.load(getLanguagePackagePath(language))
        self.app.installTranslator(self.translator)

        self.languageChanged.emit()

# Normally, these insignificant loading events can be automatically determined，
# whether to create the application.
# However, this module is different;
# its creation depends on the QApplication passed in during the call,
# therefore, a distinction must be made.
# Remember to create service before get it
def getI18nService() -> _I18nService:
    global _i18nService
    if _i18nService:
        return _i18nService
    
    raise RuntimeError("i18n service not created")

# You cannot create service twice
def createI18nService(app) -> _I18nService:
    global _i18nService
    if _i18nService:
        raise RuntimeError("I18n service already created")
    
    _i18nService = _I18nService(app)
    return _i18nService