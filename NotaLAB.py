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


# Extrai acordes simples por batida
# retorna lista de índices de notas (0=C, 1=C#, ..., 11=B)
def detectar_acordes(sinal, taxa):
    _, batidas = librosa.beat.beat_track(y=sinal, sr=taxa)
    amostras = librosa.frames_to_samples(batidas)
    acordes = []
    for i in range(len(amostras)-1):
        trecho = sinal[amostras[i]:amostras[i+1]]
        crom = librosa.feature.chroma_cqt(y=trecho, sr=taxa).mean(axis=1)
        raiz = int(np.argmax(crom))
        acordes.append(raiz)
    return acordes

# Separa vozes (vocal, baixo, bateria, outros)
# caminho: arquivo de origem, 
# saida: pasta para stems

def separar_stems(caminho, saida='stems'):
    sep = Separator('spleeter:4stems')
    sep.separate_to_file(caminho, saida)
    return f"Stems salvos em '{saida}'"

# Gera linhas de harmonia para corais (Soprano, Contralto, Tenor)
# notas_por_voz: dict com chaves 'Soprano','Contralto','Tenor' e valores listas de tuplas (nota, duração)

def montar_harmonia(notas_por_voz):
    partitura = stream.Score()
    for voz, sequencia in notas_por_voz.items():
        parte = stream.Part()
        parte.id = voz
        for grau, dur in sequencia:
            n = note.Note(grau)
            n.quarterLength = dur
            parte.append(n)
        partitura.append(parte)
    return partitura

if __name__ == '__main__':
    # Exemplo de uso:
    audio = 'minha_musica.mp3'
    sinal, taxa = carregar_audio(audio)

    print('Tom:', detectar_tom(sinal, taxa))
    print('BPM:', detectar_bpm(sinal, taxa))

    acordes_idx = detectar_acordes(sinal, taxa)
    print('Acordes (índices):', acordes_idx)

    print(separar_stems(audio))

    # Exemplo de harmonia manual:
    exemplo = {
        'Soprano': [('C4', 1), ('E4', 1)],
        'Contralto':    [('A3', 1), ('B3', 1)],
        'Tenor':   [('F3', 1), ('G3', 1)]
    }
    part = montar_harmonia(exemplo)
    part.show('text')  # mostra no console