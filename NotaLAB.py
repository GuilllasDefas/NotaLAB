import librosa
import numpy as np

from spleeter.separator import Separator # vai servir para separar os instrumentos (voz, baixo, bateria e outros)
from music21 import stream, note, chord # para manipular as notas musicais

def carregar_audio(caminho, sr=44100):
    '''
    # Carrega um arquivo de áudio e retorna o sinal e a taxa de amostragem.
    sinal = (np.ndarray): série temporal do áudio (amplitudes).
    taxa = (int): taxa de amostragem do áudio (número de amostras por segundo).
    '''
    sinal, taxa = librosa.load(caminho, sr=sr)
    return sinal, taxa

