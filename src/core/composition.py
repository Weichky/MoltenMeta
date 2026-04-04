import re
from dataclasses import dataclass

from core.element_map import symbolToId


@dataclass
class ParsedComposition:
    elements: list[str]
    fractions: list[float]


class CompositionTool:
    _PATTERN = re.compile(r"([A-Z][a-z]?)(\d+\.?\d*)")

    def parse(self, composition_str: str) -> ParsedComposition | None:
        matches = self._PATTERN.findall(composition_str)
        if not matches:
            return None

        elements = [m[0] for m in matches]
        fractions = [float(m[1]) for m in matches]

        total = sum(fractions)
        if total == 0:
            return None

        normalized = [f / total for f in fractions]
        return ParsedComposition(elements=elements, fractions=normalized)

    def symbolToNumber(self, symbol: str) -> int | None:
        return symbolToId(symbol)

    def toArgumentMap(
        self,
        parsed: ParsedComposition,
        param_map: list[list],
        use_atomic_number: bool = False,
    ) -> dict:
        result = {}
        for param_name, output_index in param_map:
            if output_index % 2 == 0:
                idx = output_index // 2
                if idx < len(parsed.elements):
                    elem = parsed.elements[idx]
                    if use_atomic_number:
                        result[param_name] = self.symbolToNumber(elem)
                    else:
                        result[param_name] = elem
            else:
                idx = output_index // 2
                if idx < len(parsed.fractions):
                    result[param_name] = parsed.fractions[idx]
        return result
