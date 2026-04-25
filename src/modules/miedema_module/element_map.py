"""
Element mapping for Miedema module.

Re-exports from the shared element_map module.
See element_map.element_map for the canonical implementation.
"""

from ..element_map.element_map import (
    ELEMENT_ID_TO_SYMBOL,
    ELEMENT_SYMBOL_TO_ID,
    elemIdToSymbol,
    elemSymbolToId,
)

__all__ = [
    "ELEMENT_ID_TO_SYMBOL",
    "ELEMENT_SYMBOL_TO_ID",
    "elemIdToSymbol",
    "elemSymbolToId",
]
