from enum import Enum

class ProcessState(Enum):
    PENDING = 0
    FAILED_EXTRACT_AUDIO = 1
    FAILED_MODIFY_AUDIO = 2
    FAILED_ABC2MIDI = 3
    FAILED_MIDI2WAV = 4
    OK = 5
    

class Result:
    
    
    def __init__(self, state:ProcessState, reason:str = "") -> None:
        self.state = state
        self.reason = reason
    def is_ok(self) -> bool:
        return self.state == ProcessState.OK

def ResultOK() -> Result:
    return Result(ProcessState.OK)