from pathlib import Path

from core.log import getLogger
from i18n.language import getSupportedTranslationLanguages

logger = getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LANGUAGE_PACKAGE_PATH = BASE_DIR / "i18n"

def getLanguagePackagePath(language: str) -> str | None:
    if language == "en":
        return None
    
    if language not in getSupportedTranslationLanguages():
        raise ValueError(f"Language {language} not supported")
    
    path =  LANGUAGE_PACKAGE_PATH / f"{language}.qm"
    if not path.exists():
        raise FileNotFoundError(f"Language package not found: {path}")
    
    return str(path)
