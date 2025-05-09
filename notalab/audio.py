"""
Módulo para manipulação e análise de áudio.
Contém funções para carregamento e análise de características musicais.
"""
import librosa
import numpy as np

def carregar_audio(caminho, sr=44100):
    '''
    Carrega um arquivo de áudio e retorna o sinal e a taxa de amostragem.
    
    Args:
        caminho (str): Caminho para o arquivo de áudio
        sr (int): Taxa de amostragem desejada
        
    Returns:
        tuple: (sinal, taxa) onde:
            sinal (np.ndarray): série temporal do áudio (amplitudes)
            taxa (int): taxa de amostragem do áudio
    '''
    sinal, taxa = librosa.load(caminho, sr=sr)
    return sinal, taxa

def detectar_tom(sinal, taxa):
    '''
    Detecta a nota principal (tom) usando cromagrama.
    
    Args:
        sinal (np.ndarray): Sinal de áudio
        taxa (int): Taxa de amostragem
        
    Returns:
        str: Nota base (ex: 'C', 'D#', 'F#')
    '''
    cromagrama = librosa.feature.chroma_stft(y=sinal, sr=taxa, n_fft=512)  # ou 256
    media = cromagrama.mean(axis=1)
    notas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    tom = notas[int(np.argmax(media))]
    return tom

def detectar_bpm(sinal, taxa):
    '''
    Estima o BPM (batidas por minuto) do áudio.
    
    Args:
        sinal (np.ndarray): Sinal de áudio
        taxa (int): Taxa de amostragem
        
    Returns:
        int: BPM estimado, arredondado para o inteiro mais próximo
    '''
    bpm, _ = librosa.beat.beat_track(y=sinal, sr=taxa)
    return round(float(bpm))

def detectar_acordes(sinal, taxa):
    '''
    Extrai acordes simples por batida.
    
    Args:
        sinal (np.ndarray): Sinal de áudio
        taxa (int): Taxa de amostragem
        
    Returns:
        list: Lista de índices de notas (0=C, 1=C#, ..., 11=B)
    '''
    _, batidas = librosa.beat.beat_track(y=sinal, sr=taxa)
    amostras = librosa.frames_to_samples(batidas)
    acordes = []
    for i in range(len(amostras)-1):
        trecho = sinal[amostras[i]:amostras[i+1]]
        crom = librosa.feature.chroma_cqt(y=trecho, sr=taxa).mean(axis=1)
        raiz = int(np.argmax(crom))
        acordes.append(raiz)
    return acordes
