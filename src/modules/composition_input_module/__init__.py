from .composition_input import (
    FractionType,
    ParsedComposition,
    CompositionError,
    massToMole,
    CompositionTool,
)

__all__ = [
    "FractionType",
    "ParsedComposition",
    "CompositionError",
    "massToMole",
    "CompositionTool",
    "CompositionInputService",
    "createWizard",
]

from .ui import createWizard


class CompositionInputService:
    pass