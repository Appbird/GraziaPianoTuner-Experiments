from pathlib import Path
import sys

from conversion.abc2audio import abc2wav


print(abc2wav(sys.argv[1], "a.midi", "a.wav").reason)