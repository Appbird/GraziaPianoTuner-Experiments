from enum import Enum
from typing import Self

class ProcessState(Enum):
    PENDING = 0
    FAILED_EXTRACT_AUDIO = 1
    FAILED_MODIFY_AUDIO = 2
    FAILED_ABC2MIDI = 3
    FAILED_MIDI2WAV = 4
    OK = 5
    

class ABC2AudioResult:
    def __init__(self, state:ProcessState, reason:str = "") -> None:
        self.state = state
        self.reason = reason
        self.casename = ""
    def give_casename(self, casename:str):
        self.casename = casename

    def write_result(self, result:Self):
        self.state = result.state
        self.reason = result.reason
    
    def encode(self) -> str:
        return f"[{self.casename}] {self.state.name} {self.reason}\n"

    def is_ok(self) -> bool:
        return self.state == ProcessState.OK

def ResultOK() -> ABC2AudioResult:
    return ABC2AudioResult(ProcessState.OK)