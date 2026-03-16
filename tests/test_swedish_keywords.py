"""Tester för svenska nyckelordsmappningar."""

from codelingo.swedish_keywords import (
    ALL_REVERSE,
    ALL_SWEDISH,
    BUILTINS,
    ERROR_MESSAGES,
    KEYWORDS,
    REVERSE_BUILTINS,
    REVERSE_KEYWORDS,
)


class TestKeywordMappings:
    """Tester för nyckelordsmappningar."""

    def test_keywords_not_empty(self):
        assert len(KEYWORDS) > 0

    def test_builtins_not_empty(self):
        assert len(BUILTINS) > 0

    def test_no_duplicate_swedish_keywords(self):
        all_swedish = list(KEYWORDS.keys()) + list(BUILTINS.keys())
        assert len(all_swedish) == len(set(all_swedish))

    def test_no_duplicate_python_targets(self):
        """Varje Python-nyckelord ska bara ha en svensk mappning."""
        python_keywords = list(KEYWORDS.values())
        assert len(python_keywords) == len(set(python_keywords))

    def test_reverse_keyword_mapping(self):
        for swe, eng in KEYWORDS.items():
            assert REVERSE_KEYWORDS[eng] == swe

    def test_reverse_builtin_mapping(self):
        for swe, eng in BUILTINS.items():
            assert REVERSE_BUILTINS[eng] == swe

    def test_all_swedish_combined(self):
        assert len(ALL_SWEDISH) == len(KEYWORDS) + len(BUILTINS)

    def test_all_reverse_combined(self):
        assert len(ALL_REVERSE) == len(REVERSE_KEYWORDS) + len(REVERSE_BUILTINS)

    def test_essential_keywords_present(self):
        """Kontrollera att viktiga nyckelord finns."""
        essential = ["om", "annars", "medan", "funktion", "returnera"]
        for kw in essential:
            assert kw in KEYWORDS, f"Saknar nyckelord: {kw}"

    def test_essential_builtins_present(self):
        """Kontrollera att viktiga inbyggda funktioner finns."""
        essential = ["skriv", "längd", "omfång", "heltal", "text"]
        for bi in essential:
            assert bi in BUILTINS, f"Saknar builtin: {bi}"

    def test_error_messages_not_empty(self):
        assert len(ERROR_MESSAGES) > 0

    def test_common_errors_translated(self):
        common = ["SyntaxError", "NameError", "TypeError"]
        for err in common:
            assert err in ERROR_MESSAGES

    def test_keywords_map_to_python_keywords(self):
        """Verifiera att mappningarna är korrekta Python-nyckelord."""
        import keyword
        python_kws = set(keyword.kwlist) | {"True", "False", "None"}
        for eng in KEYWORDS.values():
            assert eng in python_kws, f"{eng} är inte ett Python-nyckelord"

    def test_builtins_map_to_python_builtins(self):
        """Verifiera att builtins mappar till riktiga Python-builtins."""
        import builtins
        for eng in BUILTINS.values():
            assert hasattr(builtins, eng), \
                f"{eng} är inte en Python-builtin"
