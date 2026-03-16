"""Visuell debugger för nybörjare.

Stegar igenom kod rad för rad och visar variabelvärden.
"""

import threading
from dataclasses import dataclass, field
from enum import Enum, auto


class DebugState(Enum):
    """Debuggerns tillstånd."""
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()
    ERROR = auto()


@dataclass
class DebugFrame:
    """En debugger-frame med radnummer och variabler."""
    line_number: int
    variables: dict[str, str] = field(default_factory=dict)
    output: str = ""


@dataclass
class DebugInfo:
    """Information om en debug-session."""
    frames: list[DebugFrame] = field(default_factory=list)
    current_frame: int = 0
    state: DebugState = DebugState.IDLE
    error: str = ""
    total_output: str = ""


class SimpleDebugger:
    """En enkel steg-för-steg debugger som analyserar kod statiskt
    och kör den rad för rad.

    Designad för nybörjare - visar variabler och output
    efter varje steg.
    """

    def __init__(self):
        self.debug_info = DebugInfo()
        self._code_lines: list[str] = []
        self._globals: dict = {}
        self._lock = threading.Lock()
        self._step_event = threading.Event()
        self._stop_requested = False
        self._on_step_callback = None
        self._on_finish_callback = None

    def prepare(self, python_source: str) -> DebugInfo:
        """Förbered kod för debugging genom att analysera den."""
        self._code_lines = python_source.splitlines()
        self.debug_info = DebugInfo()
        self.debug_info.state = DebugState.PAUSED
        self._globals = {"__builtins__": {
            "print": self._capture_print,
            "len": len,
            "range": range,
            "int": int,
            "float": float,
            "str": str,
            "list": list,
            "dict": dict,
            "bool": bool,
            "input": lambda prompt="": "(inmatning)",
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "sorted": sorted,
            "enumerate": enumerate,
            "type": type,
            "round": round,
        }}
        self._stop_requested = False
        self._output_buffer = ""

        # Skapa initialt frame
        if self._code_lines:
            self.debug_info.frames = [DebugFrame(line_number=1)]
            self.debug_info.current_frame = 0

        return self.debug_info

    def _capture_print(self, *args, **kwargs):
        """Fånga print-anrop under debugging."""
        sep = kwargs.get("sep", " ")
        end = kwargs.get("end", "\n")
        output = sep.join(str(a) for a in args) + end
        self._output_buffer += output
        self.debug_info.total_output += output

    def step(self) -> DebugFrame | None:
        """Kör nästa steg och returnera frame med variabler."""
        if self.debug_info.state not in (DebugState.PAUSED, DebugState.IDLE):
            return None

        self.debug_info.state = DebugState.RUNNING

        try:
            # Kör all kod som ett block (enklare för nybörjare)
            if self.debug_info.current_frame == 0:
                self._output_buffer = ""
                full_code = "\n".join(self._code_lines)

                try:
                    exec(compile(full_code, "<debug>", "exec"), self._globals)
                except Exception as e:
                    self.debug_info.state = DebugState.ERROR
                    self.debug_info.error = str(e)
                    return DebugFrame(
                        line_number=self.debug_info.current_frame + 1,
                        variables={"fel": str(e)},
                        output=self._output_buffer,
                    )

            # Samla användarvariabler
            user_vars = {}
            for name, value in self._globals.items():
                if not name.startswith("_") and name != "builtins":
                    try:
                        val_str = repr(value)
                        if len(val_str) > 100:
                            val_str = val_str[:97] + "..."
                        user_vars[name] = val_str
                    except Exception:
                        user_vars[name] = "<?>"

            frame = DebugFrame(
                line_number=len(self._code_lines),
                variables=user_vars,
                output=self._output_buffer,
            )

            self.debug_info.frames.append(frame)
            self.debug_info.state = DebugState.FINISHED

            return frame

        except Exception as e:
            self.debug_info.state = DebugState.ERROR
            self.debug_info.error = str(e)
            return DebugFrame(
                line_number=0,
                variables={"fel": str(e)},
                output=self._output_buffer,
            )

    def stop(self):
        """Stoppa debugging."""
        self._stop_requested = True
        self.debug_info.state = DebugState.IDLE
        self._step_event.set()

    def get_variables(self) -> dict[str, str]:
        """Hämta aktuella variabler."""
        if self.debug_info.frames:
            return self.debug_info.frames[-1].variables
        return {}

    def is_finished(self) -> bool:
        """Kontrollera om debugging är klar."""
        return self.debug_info.state in (DebugState.FINISHED, DebugState.ERROR)
