import librosa
import numpy as np

from spleeter.separator import Separator # vai servir para separar os instrumentos (voz, baixo, bateria e outros)
from music21 import stream, note, chord

