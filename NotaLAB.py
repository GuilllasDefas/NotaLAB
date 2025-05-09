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

# Detecta a nota principal (tom) usando cromagrama
# sinal: áudio carregado, taxa: taxa de amostragem
# retorna nota base (ex: 'C', 'D#', 'F#')
def detectar_tom(sinal, taxa):
    '''
    1. Cálculo do cromagrama:
    Ela utiliza librosa.feature.chroma_cqt para transformar o áudio em um cromagrama, 
    que é uma representação gráfica da intensidade (energia) de cada uma das 12 notas musicais ao longo do tempo.

    2. Média de energia:
    Em seguida, calcula a média dos valores de energia para cada nota (linha) do cromagrama. 
    Dessa forma, ela obtém um valor que representa a intensidade média de cada nota no áudio.

    3. Seleção da nota principal:
    É criada uma lista com as 12 notas musicais (de C a B, incluindo sustenidos). 
    Pela função np.argmax, é identificado qual nota possui a maior energia média, 
    e essa nota é escolhida como o "tom" principal do áudio.
    '''
    cromagrama = librosa.feature.chroma_cqt(y=sinal, sr=taxa)
    media = cromagrama.mean(axis=1)
    notas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    tom = notas[int(np.argmax(media))]
    return tom

# Estima o BPM (batidas por minuto)
def detectar_bpm(sinal, taxa):
    bpm, _ = librosa.beat.beat_track(y=sinal, sr=taxa)
    return round(bpm)