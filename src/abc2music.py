import subprocess
from midi2audio import FluidSynth

def write_midi_from_abc(abc_file_path:str, midi_file_path:str):
    result = subprocess.run(["abc2midi", abc_file_path, midi_file_path])
    assert result == 0

def write_wav_from_midi(midi_file_path:str, wav_file_path):
    fs = FluidSynth(sound_font="sf2/GeneralUser_GS_1.471/GeneralUser_GS_v1.471.sf2")
    fs.midi_to_audio(midi_file_path, wav_file_path)

if __name__ == "main":
    pass