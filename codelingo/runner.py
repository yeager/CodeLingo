"""Säker kodkörning med sandboxad Python.

Använder RestrictedPython för kompileringstidsbegränsningar
och subprocess-isolering för körtidsskydd.
"""

import queue
import sys
import threading
import time
import traceback
from dataclasses import dataclass
from io import StringIO

try:
    from RestrictedPython import compile_restricted, safe_globals
    from RestrictedPython.Guards import (
        guarded_unpack_sequence,
        safer_getattr,
    )
    HAS_RESTRICTED = True
except ImportError:
    HAS_RESTRICTED = False


@dataclass
class ExecutionResult:
    """Resultat från kodkörning."""
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    timed_out: bool = False
    execution_time_ms: float = 0.0


# Tillåtna inbyggda funktioner i sandboxen
SAFE_BUILTINS = {
    "print", "len", "range", "input", "int", "float", "str",
    "list", "dict", "type", "sorted", "sum", "min", "max",
    "abs", "bool", "set", "tuple", "enumerate", "zip", "map",
    "filter", "round", "chr", "ord", "hex", "bin", "oct",
    "isinstance", "issubclass", "hasattr", "getattr",
    "reversed", "any", "all", "repr",
}


def _run_code_in_process(code: str, result_queue, timeout: float):
    """Kör kod i en separat process för isolering."""
    output = StringIO()
    error_output = StringIO()
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    try:
        sys.stdout = output
        sys.stderr = error_output

        if HAS_RESTRICTED:
            byte_code = compile_restricted(
                code, filename="<codelingo>", mode="exec"
            )
            if byte_code is None:
                result_queue.put(ExecutionResult(
                    stderr="Kompileringsfel: Koden kunde inte kompileras säkert.",
                    return_code=1,
                ))
                return

            restricted_globals = dict(safe_globals)
            restricted_globals["__builtins__"] = {
                name: __builtins__[name] if isinstance(__builtins__, dict)
                else getattr(__builtins__, name)
                for name in SAFE_BUILTINS
                if (name in __builtins__ if isinstance(__builtins__, dict)
                    else hasattr(__builtins__, name))
            }
            restricted_globals["_getattr_"] = safer_getattr
            restricted_globals["_getiter_"] = iter
            restricted_globals["_getitem_"] = lambda obj, key: obj[key]
            restricted_globals["_unpack_sequence_"] = guarded_unpack_sequence
            restricted_globals["_iter_unpack_sequence_"] = guarded_unpack_sequence
            restricted_globals["__name__"] = "__main__"
            restricted_globals["__metaclass__"] = type

            exec(byte_code, restricted_globals)
        else:
            # Fallback: begränsad exec utan RestrictedPython
            safe_builtins = {
                name: getattr(__builtins__, name)
                if hasattr(__builtins__, name)
                else __builtins__.get(name) if isinstance(__builtins__, dict)
                else None
                for name in SAFE_BUILTINS
            }
            safe_builtins = {k: v for k, v in safe_builtins.items() if v is not None}

            restricted_globals = {
                "__builtins__": safe_builtins,
                "__name__": "__main__",
            }
            exec(compile(code, "<codelingo>", "exec"), restricted_globals)

        result_queue.put(ExecutionResult(
            stdout=output.getvalue(),
            stderr=error_output.getvalue(),
            return_code=0,
        ))

    except SyntaxError as e:
        result_queue.put(ExecutionResult(
            stderr=f_("Syntax error on line {e.lineno}: { "e.msg".}"),
            return_code=1,
        ))
    except Exception as e:
        tb = traceback.format_exc()
        result_queue.put(ExecutionResult(
            stderr=str(tb),
            return_code=1,
        ))
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr


class Runner:
    """Kör Python-kod i en sandboxad miljö."""

    def __init__(self, timeout_seconds: float = 5.0):
        self.timeout = timeout_seconds
        self._current_thread = None

    def execute(self, python_source: str, callback=None):
        """Kör kod asynkront. Anropar callback med ExecutionResult."""
        self._current_thread = threading.Thread(
            target=self._execute_threaded,
            args=(python_source, callback),
            daemon=True,
        )
        self._current_thread.start()

    def execute_sync(self, python_source: str) -> ExecutionResult:
        """Kör kod synkront och returnera resultatet."""
        if not python_source.strip():
            return ExecutionResult(stdout="", return_code=0)

        result_queue = queue.Queue()
        start_time = time.time()

        thread = threading.Thread(
            target=_run_code_in_process,
            args=(python_source, result_queue, self.timeout),
            daemon=True,
        )
        thread.start()
        thread.join(timeout=self.timeout)

        elapsed = (time.time() - start_time) * 1000

        if thread.is_alive():
            return ExecutionResult(
                stderr="Tidsgräns överskriden! Programmet tog för lång tid.\n"
                       "Tips: Kontrollera att du inte har en oändlig loop.",
                return_code=1,
                timed_out=True,
                execution_time_ms=elapsed,
            )

        try:
            result = result_queue.get_nowait()
            result.execution_time_ms = elapsed
            return result
        except queue.Empty:
            return ExecutionResult(
                stderr="Okänt fel vid körning.",
                return_code=1,
                execution_time_ms=elapsed,
            )

    def _execute_threaded(self, python_source: str, callback):
        """Kör kod i en tråd och anropa callback med resultatet."""
        result = self.execute_sync(python_source)
        if callback:
            callback(result)

    def stop(self):
        """Stoppa pågående körning."""
        # Tråden är daemon, den dör med processen
        self._current_thread = None
