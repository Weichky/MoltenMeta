import re
from dataclasses import dataclass
from enum import Enum

from core.element_map import symbolToId


class FractionType(Enum):
    MOLE = "mole"
    MASS = "mass"


@dataclass
class ParsedComposition:
    elements: list[str]
    fractions: list[float]
    fraction_type: FractionType = FractionType.MOLE


class CompositionError(Exception):
    pass


_ELEMENT_PATTERN = re.compile(r"[A-Z][a-z]?")


def massToMole(
    mass_fractions: list[float],
    elements: list[str],
    atomic_masses: dict[str, float],
) -> list[float]:
    if any(f < 0 for f in mass_fractions):
        raise CompositionError("Mass fractions cannot be negative")
    moles = []
    for elem, mass_frac in zip(elements, mass_fractions):
        atomic_mass = atomic_masses.get(elem)
        if atomic_mass is None:
            raise CompositionError(f"Atomic mass for {elem} not found")
        moles.append(mass_frac / atomic_mass)

    total = sum(moles)
    if total == 0:
        raise CompositionError("Total mass is zero")
    return [m / total for m in moles]


class CompositionTool:
    def parseAndValidate(
        self,
        composition_str: str | None,
        fraction_type: FractionType,
        max_components: int = 2,
    ) -> ParsedComposition:
        if composition_str is None:
            raise CompositionError("Composition string cannot be None")
        element_symbols = _ELEMENT_PATTERN.findall(composition_str)
        if not element_symbols:
            raise CompositionError("No valid elements found in input")

        raw_fractions: list[float | None] = [None] * len(element_symbols)
        remaining = composition_str
        elem_idx = 0
        pos = 0

        while pos < len(remaining) and elem_idx < len(element_symbols):
            elem = element_symbols[elem_idx]
            elem_pos = remaining.find(elem, pos)
            if elem_pos == -1:
                break
            after_elem_pos = elem_pos + len(elem)
            if after_elem_pos >= len(remaining):
                pos = after_elem_pos
                elem_idx += 1
                continue
            num_match = re.match(r"(\d+\.?\d*)", remaining[after_elem_pos:])
            if num_match:
                raw_fractions[elem_idx] = float(num_match.group(1))
                pos = after_elem_pos + num_match.end()
            else:
                pos = after_elem_pos
            elem_idx += 1

        elements = element_symbols[:elem_idx]
        found_fractions = [f for f in raw_fractions if f is not None]
        n_missing = len(elements) - len(found_fractions)

        if n_missing == 0:
            fractions = [f for f in raw_fractions if f is not None]
        elif n_missing == 1 and found_fractions:
            total_input = sum(found_fractions)
            if fraction_type == FractionType.MOLE:
                if abs(total_input - 1.0) <= 1e-6:
                    fractions_input = found_fractions[:]
                elif abs(total_input - 100.0) <= 1e-6:
                    fractions_input = [f / 100.0 for f in found_fractions]
                else:
                    fractions_input = [f / 100.0 for f in found_fractions]
                missing = 1.0 - sum(fractions_input)
            else:
                fractions_input = [f / 100.0 for f in found_fractions]
                missing = 1.0 - sum(fractions_input)

            fractions = []
            fi = 0
            for rf in raw_fractions:
                if rf is not None:
                    fractions.append(fractions_input[fi])
                    fi += 1
                else:
                    fractions.append(missing)
        else:
            raise CompositionError(
                f"Invalid composition: found {len(elements)} elements and "
                f"{len(found_fractions)} fractions"
            )

        if fraction_type == FractionType.MOLE:
            expected = 1.0 if max(fractions) <= 1.0 else 100.0
            actual = sum(fractions)
            if abs(actual - expected) > 1e-6:
                raise CompositionError(
                    f"Total fractions must be {expected}, got {actual:.4f}"
                )
        elif n_missing == 0:
            actual = sum(fractions)
            if abs(actual - 100.0) > 1e-6:
                raise CompositionError(
                    f"Total mass fractions must be 100, got {actual:.4f}"
                )

        if fraction_type == FractionType.MOLE:
            normalized = [f / sum(fractions) for f in fractions]
        else:
            normalized = fractions
        return ParsedComposition(
            elements=elements, fractions=normalized, fraction_type=fraction_type
        )

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
