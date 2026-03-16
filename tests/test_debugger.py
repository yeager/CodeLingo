"""Tester för debuggern."""

import pytest

from codelingo.debugger import DebugState, SimpleDebugger


@pytest.fixture
def debugger():
    return SimpleDebugger()


class TestDebugger:
    """Tester för den visuella debuggern."""

    def test_prepare(self, debugger):
        info = debugger.prepare('print("hej")')
        assert info.state == DebugState.PAUSED
        assert len(info.frames) == 1

    def test_step_simple(self, debugger):
        debugger.prepare('print("hej")')
        frame = debugger.step()
        assert frame is not None
        assert "hej" in frame.output

    def test_step_with_variables(self, debugger):
        debugger.prepare("x = 42\ny = 10")
        frame = debugger.step()
        assert frame is not None
        variables = frame.variables
        assert "x" in variables
        assert "42" in variables["x"]

    def test_debug_finishes(self, debugger):
        debugger.prepare('print("test")')
        debugger.step()
        assert debugger.is_finished()

    def test_debug_error(self, debugger):
        debugger.prepare("1/0")
        frame = debugger.step()
        assert debugger.debug_info.state == DebugState.ERROR

    def test_stop(self, debugger):
        debugger.prepare("x = 1")
        debugger.stop()
        assert debugger.debug_info.state == DebugState.IDLE

    def test_get_variables_empty(self, debugger):
        assert debugger.get_variables() == {}

    def test_empty_code(self, debugger):
        info = debugger.prepare("")
        assert info.state == DebugState.PAUSED

    def test_multiple_prints(self, debugger):
        debugger.prepare('print("a")\nprint("b")')
        frame = debugger.step()
        assert "a" in frame.output
        assert "b" in frame.output
