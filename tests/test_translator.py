"""Tester för översättaren."""

import pytest

from codelingo.translator import Translator


@pytest.fixture
def translator():
    return Translator()


class TestTranslator:
    """Tester för svensk→Python-översättning."""

    def test_simple_print(self, translator):
        result = translator.translate('skriv("Hej")')
        assert 'print("Hej")' in result.python_source

    def test_if_else(self, translator):
        code = 'om sant:\n    skriv("ja")\nannars:\n    skriv("nej")'
        result = translator.translate(code)
        assert "if True:" in result.python_source
        assert "else:" in result.python_source

    def test_while_loop(self, translator):
        code = "medan sant:\n    avbryt"
        result = translator.translate(code)
        assert "while True:" in result.python_source
        assert "break" in result.python_source

    def test_function_def(self, translator):
        code = "funktion hej():\n    skriv(42)"
        result = translator.translate(code)
        assert "def hej():" in result.python_source
        assert "print(42)" in result.python_source

    def test_string_not_translated(self, translator):
        code = 'skriv("om du vill")'
        result = translator.translate(code)
        # "om" inside string should NOT become "if"
        assert '"om du vill"' in result.python_source or "'om du vill'" in result.python_source

    def test_for_loop(self, translator):
        code = "för i i omfång(5):\n    skriv(i)"
        result = translator.translate(code)
        assert "for" in result.python_source
        assert "range(5)" in result.python_source

    def test_boolean_values(self, translator):
        code = "x = sant\ny = falskt\nz = ingen"
        result = translator.translate(code)
        assert "True" in result.python_source
        assert "False" in result.python_source
        assert "None" in result.python_source

    def test_logical_operators(self, translator):
        code = "om sant och falskt eller inte sant:\n    godkänn"
        result = translator.translate(code)
        assert "and" in result.python_source
        assert "or" in result.python_source
        assert "not" in result.python_source
        assert "pass" in result.python_source

    def test_return_statement(self, translator):
        code = "funktion dubbla(x):\n    returnera x * 2"
        result = translator.translate(code)
        assert "def dubbla(x):" in result.python_source
        assert "return x * 2" in result.python_source

    def test_empty_input(self, translator):
        result = translator.translate("")
        assert result.python_source == ""

    def test_comments_preserved(self, translator):
        code = "# Detta är en kommentar om livet"
        result = translator.translate(code)
        assert "# Detta är en kommentar om livet" in result.python_source

    def test_line_map(self, translator):
        code = "x = 1\ny = 2\nskriv(x + y)"
        result = translator.translate(code)
        assert 1 in result.line_map
        assert 2 in result.line_map
        assert 3 in result.line_map

    def test_indentation_preserved(self, translator):
        code = "om sant:\n    skriv(1)\n    om falskt:\n        skriv(2)"
        result = translator.translate(code)
        lines = result.python_source.splitlines()
        assert lines[1].startswith("    ")
        assert lines[3].startswith("        ")

    def test_eller_om(self, translator):
        code = "om x > 0:\n    skriv(1)\neller_om x < 0:\n    skriv(-1)"
        result = translator.translate(code)
        assert "elif" in result.python_source

    def test_class_definition(self, translator):
        code = "klass Hund:\n    godkänn"
        result = translator.translate(code)
        assert "class Hund:" in result.python_source
        assert "pass" in result.python_source

    def test_try_except(self, translator):
        code = "försök:\n    skriv(1)\nutom:\n    skriv(0)"
        result = translator.translate(code)
        assert "try:" in result.python_source
        assert "except:" in result.python_source


class TestErrorTranslation:
    """Tester för felmeddelande-översättning."""

    def test_name_error(self, translator):
        error = "NameError: name 'x' is not defined"
        result = translator.translate_error(error)
        assert "Namnfel" in result

    def test_syntax_error(self, translator):
        error = "SyntaxError: invalid syntax"
        result = translator.translate_error(error)
        assert "Syntaxfel" in result

    def test_zero_division(self, translator):
        error = "ZeroDivisionError: division by zero"
        result = translator.translate_error(error)
        assert "Divisionfel" in result

    def test_indentation_error(self, translator):
        error = "IndentationError: unexpected indent"
        result = translator.translate_error(error)
        assert "Indenteringsfel" in result
