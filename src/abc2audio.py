import subprocess
import sys
from pathlib import Path
from Result import Result, ProcessState, ResultOK


def write_midi_from_abc(abc_file_path:str, midi_file_path:str) -> Result:
    sbp = subprocess.Popen(["abc2midi", abc_file_path, '-o', midi_file_path],
        stdout=subprocess.PIPE,
        cwd=Path.cwd()
    )
    out, _ = sbp.communicate()
    stdout_content = out.decode('utf-8')
    if any([line.startswith("Error") for line in stdout_content.splitlines()]): return Result(ProcessState.FAILED_ABC2MIDI, stdout_content)
    if any([line.startswith("Warning") for line in stdout_content.splitlines()]): return Result(ProcessState.OK, stdout_content)
    return ResultOK()


def write_wav_from_midi(midi_file_path:str, wav_file_path:str, gain:float) -> Result:
    sound_font_path = str(Path.cwd()/"sf2/GeneralUser_GS_1.471/GeneralUser_GS_v1.471.sf2")
    sbp = subprocess.Popen([
            "fluidsynth",
            # Render MIDI file to raw audio data and store in [file]
            "-F", wav_file_path,
            # Set the master gain [0 < gain < 10, default = 0.2]
            "-g", str(gain),
            # Do not print welcome message or other informational output
            "-q",
            sound_font_path,
            midi_file_path,
        ],
        stderr=subprocess.PIPE,
        cwd=Path.cwd()
    )
    _, err = sbp.communicate()
    return ResultOK() if sbp.returncode == 0 else Result(ProcessState.FAILED_MIDI2WAV, err.decode('utf-8'))


def abc2wav(input_abc_path:str, midi_file:str, wav_file:str) -> Result:
    result1 = write_midi_from_abc(input_abc_path, midi_file)
    if not result1.is_ok() : return result1
    
    result2 = write_wav_from_midi(midi_file, wav_file, 1)
    if not result2.is_ok() : return result2

    return result2 if len(result1.reason) == 0 else Result(ProcessState.OK, result1.reason + result2.reason)

if __name__ == "__main__":
    print(abc2wav(sys.argv[1], "a.midi", "a.wav").reason)