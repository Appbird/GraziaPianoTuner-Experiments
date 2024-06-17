import subprocess
import sys
from pathlib    import Path

def write_midi_from_abc(abc_file_path:str, midi_file_path:str):
    return subprocess.run(["abc2midi", abc_file_path, '-o', midi_file_path])


def write_wav_from_midi(midi_file_path:str, wav_file_path:str, gain:float):
    sound_font_path = "sf2/GeneralUser_GS_1.471/GeneralUser_GS_v1.471.sf2"
    return subprocess.run([
        "fluidsynth",
        # Render MIDI file to raw audio data and store in [file]
        "-F", wav_file_path,
        # Set the master gain [0 < gain < 10, default = 0.2]
        "-g", str(gain),
        sound_font_path,
        midi_file_path,
    ])

def abc2wav(input_abc_path:str):
    def dir_stem_ext(filedir:Path, filestem:str, ext:str):
        return f"{filedir/Path(f'{filestem}.{ext}')}"
    
    filepath = Path(input_abc_path)
    filestem = filepath.stem
    filedir = filepath.parent

    abc_file = str(filepath)
    midi_file = dir_stem_ext(filedir, filestem, "mid")
    wav_file = dir_stem_ext(filedir, filestem, "wav")
    
    conv_result = write_midi_from_abc(abc_file, midi_file)
    if conv_result.returncode != 0 : return False
    
    conv_result = write_wav_from_midi(midi_file, wav_file, 1)
    if conv_result.returncode != 0 : return False

    return True

if __name__ == "__main__":
    assert len(sys.argv) == 2
    abc2wav(input_abc_path=sys.argv[1])
    

