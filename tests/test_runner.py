"""Tester för kodköraren."""

import pytest

from codelingo.runner import Runner


@pytest.fixture
def runner():
    return Runner(timeout_seconds=3.0)


class TestRunner:
    """Tester för sandboxad kodkörning."""

    def test_simple_print(self, runner):
        result = runner.execute_sync('print("Hej")')
        assert result.stdout.strip() == "Hej"
        assert result.return_code == 0

    def test_math(self, runner):
        result = runner.execute_sync("print(2 + 3)")
        assert result.stdout.strip() == "5"

    def test_syntax_error(self, runner):
        result = runner.execute_sync("if if if")
        assert result.return_code == 1
        assert result.stderr

    def test_empty_code(self, runner):
        result = runner.execute_sync("")
        assert result.return_code == 0

    def test_variables(self, runner):
        result = runner.execute_sync('x = 42\nprint(x)')
        assert "42" in result.stdout

    def test_loop(self, runner):
        result = runner.execute_sync(
            "for i in range(3):\n    print(i)"
        )
        assert "0" in result.stdout
        assert "1" in result.stdout
        assert "2" in result.stdout

    def test_function(self, runner):
        code = "def dubbla(x):\n    return x * 2\nprint(dubbla(5))"
        result = runner.execute_sync(code)
        assert "10" in result.stdout

    def test_execution_time_tracked(self, runner):
        result = runner.execute_sync('print("test")')
        assert result.execution_time_ms >= 0

    def test_multiline_output(self, runner):
        result = runner.execute_sync(
            'print("rad1")\nprint("rad2")\nprint("rad3")'
        )
        lines = result.stdout.strip().splitlines()
        assert len(lines) == 3

    def test_string_operations(self, runner):
        result = runner.execute_sync(
            'text = "hej världen"\nprint(len(text))'
        )
        assert result.return_code == 0


class TestRunnerSecurity:
    """Tester för säkerhetsbegränsningar."""

    def test_no_file_access(self, runner):
        result = runner.execute_sync('open("/etc/passwd")')
        assert result.return_code == 1

    def test_no_os_module(self, runner):
        result = runner.execute_sync("import os")
        assert result.return_code == 1

    def test_no_subprocess(self, runner):
        result = runner.execute_sync("import subprocess")
        assert result.return_code == 1

    def test_runtime_error(self, runner):
        result = runner.execute_sync("1/0")
        assert result.return_code == 1
        assert result.stderr
