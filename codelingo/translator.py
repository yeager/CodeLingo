"""Översätter svensk pseudokod till giltig Python.

Använder regex-baserad ersättning som skyddar strängar
och kommentarer från översättning.
"""

import re
from dataclasses import dataclass, field

from codelingo.swedish_keywords import (
    ALL_REVERSE,
    ALL_SWEDISH,
    ERROR_MESSAGES,
)

# Regex för att dela upp en rad i strängar och icke-strängar
# Matchar: "...", '...', """...""", '''...'''
_STRING_PATTERN = re.compile(
    r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
)


@dataclass
class TranslationResult:
    """Resultat från en översättning."""
    python_source: str
    line_map: dict[int, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class Translator:
    """Översätter svensk pseudokod till Python."""

    def __init__(self):
        self._keyword_map = ALL_SWEDISH
        self._reverse_map = ALL_REVERSE
        # Bygg ett sorterat mönster (längre ord först för att undvika delmatchningar)
        sorted_keys = sorted(self._keyword_map.keys(), key=len, reverse=True)
        escaped = [re.escape(k) for k in sorted_keys]
        self._replace_pattern = re.compile(
            r"(?<![a-zA-ZåäöÅÄÖ_\d])(" + "|".join(escaped) + r")(?![a-zA-ZåäöÅÄÖ_\d])"
        )

    def translate(self, swedish_source: str) -> TranslationResult:
        """Översätt svensk källkod till Python."""
        if not swedish_source.strip():
            return TranslationResult(python_source="", line_map={})

        result_lines = []
        line_map = {}

        for line_num, line in enumerate(swedish_source.splitlines(), 1):
            translated = self._translate_line(line)
            result_lines.append(translated)
            line_map[line_num] = line_num

        python_source = "\n".join(result_lines)
        if swedish_source.endswith("\n"):
            python_source += "\n"

        return TranslationResult(
            python_source=python_source,
            line_map=line_map,
        )

    def _translate_line(self, line: str) -> str:
        """Översätt en enskild rad."""
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]

        if not stripped:
            return line

        # Kommentarer lämnas orörda
        if stripped.startswith("#"):
            return line

        translated = self._replace_preserving_strings(stripped)
        return indent + translated

    def _replace_preserving_strings(self, code: str) -> str:
        """Ersätt svenska nyckelord men lämna strängar orörda."""
        # Dela upp i strängar och icke-strängar
        parts = _STRING_PATTERN.split(code)
        result = []

        for i, part in enumerate(parts):
            if i % 2 == 1:
                # Strängdel - lämna orörd
                result.append(part)
            else:
                # Koddel - ersätt nyckelord
                translated = self._replace_pattern.sub(
                    lambda m: self._keyword_map[m.group(0)], part
                )
                result.append(translated)

        return "".join(result)

    def translate_error(self, error_msg: str) -> str:
        """Översätt ett Python-felmeddelande till svenska."""
        result = error_msg

        for eng, swe in ERROR_MESSAGES.items():
            result = result.replace(eng, swe)

        for eng, swe in self._reverse_map.items():
            result = re.sub(rf"\b{re.escape(eng)}\b", swe, result)

        return result

    def get_realtime_preview(self, swedish_source: str) -> str:
        """Returnera Python-översättning för realtidsvisning."""
        result = self.translate(swedish_source)
        return result.python_source
