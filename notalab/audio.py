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
    Detecta a tonalidade (tônica e modo) usando análise por perfil tonal.
    
    Args:
        sinal (np.ndarray): Sinal de áudio
        taxa (int): Taxa de amostragem
        
    Returns:
        tuple: (tônica, modo) onde tônica é a nota base e modo é 'maior' ou 'menor'
    '''
    # Cromagrama com janela maior para melhor resolução espectral
    hop_length = 512
    n_fft = 4096
    cromagrama = librosa.feature.chroma_cqt(y=sinal, sr=taxa, hop_length=hop_length)
    
    # Perfis tonais de Krumhansl-Schmuckler para correlação
    perfil_maior = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    perfil_menor = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    
    # Normalizar perfis
    perfil_maior = perfil_maior / np.sum(perfil_maior)
    perfil_menor = perfil_menor / np.sum(perfil_menor)
    
    # Distribuição de notas no cromagrama
    dist_notas = np.mean(cromagrama, axis=1)
    dist_notas = dist_notas / np.sum(dist_notas)
    
    # Calcular correlação para todas as possíveis tonalidades
    correlacoes_maior = np.zeros(12)
    correlacoes_menor = np.zeros(12)
    
    for i in range(12):
        dist_rotacionada = np.roll(dist_notas, -i)
        correlacoes_maior[i] = np.corrcoef(dist_rotacionada, perfil_maior)[0, 1]
        correlacoes_menor[i] = np.corrcoef(dist_rotacionada, perfil_menor)[0, 1]
    
    # Encontrar melhor correspondência
    idx_maior = np.argmax(correlacoes_maior)
    idx_menor = np.argmax(correlacoes_menor)
    corr_maior = correlacoes_maior[idx_maior]
    corr_menor = correlacoes_menor[idx_menor]
    
    # Determinar o tom e modo com maior correlação
    notas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    if corr_maior > corr_menor:
        return (notas[idx_maior], 'maior')
    else:
        return (notas[idx_menor], 'menor')

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

def detectar_acordes(sinal, taxa, bpm=120):
    '''
    Extrai acordes por compasso (1 acorde por compasso).
    '''
    duracao_total = librosa.get_duration(y=sinal, sr=taxa)
    segundos_por_compasso = 4 * 60 / bpm  # 4/4
    acordes = []
    for inicio in np.arange(0, duracao_total, segundos_por_compasso):
        fim = min(inicio + segundos_por_compasso, duracao_total)
        ini_sample = int(inicio * taxa)
        fim_sample = int(fim * taxa)
        trecho = sinal[ini_sample:fim_sample]
        if len(trecho) == 0:
            continue
        crom = librosa.feature.chroma_cqt(y=trecho, sr=taxa).mean(axis=1)
        raiz = int(np.argmax(crom))
        acordes.append(raiz)
    return acordes
