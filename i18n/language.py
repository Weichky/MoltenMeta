def getSupportedLanguagesNameMap() -> dict:
    return {
        "en": "English",
        "zh_CN": "简体中文"
    }

def getSupportedTranslationLanguages() -> list:
    return {
        "zh_CN"
    }

def isSupportedLanguage(language: str) -> bool:
    return language in getSupportedLanguagesNameMap()