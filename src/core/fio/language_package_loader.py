from pathlib import Path

from importlib.resources import files

from catalog import getSupportedTranslationLanguages

# BASE_DIR = Path(__file__).resolve().parent.parent.parent
LANGUAGE_PACKAGE_PATH = files("resources.i18n")

# Unfortunately, Qt Translator doesn't support a Path argument,
# so we have to convert it to a string
def getLanguagePackagePath(language: str) -> str | None:
    if language == "en":
        return None
    
    if language not in getSupportedTranslationLanguages():
        raise ValueError(f"Language {language} not supported")
    
    path =  LANGUAGE_PACKAGE_PATH / f"{language}.qm"
    if not path.exists():
        raise FileNotFoundError(f"Language package not found: {path}")
    
    return str(path)
