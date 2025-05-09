"""
Módulo para funções relacionadas a harmonia e extração de notas.
"""
import numpy as np
import librosa
from music21 import pitch
from notalab.audio import carregar_audio

def extrair_notas_vocal(caminho_vocal, sr=44100):
    '''
    Extrai as notas melódicas do arquivo vocal com suas durações.
    
    Args:
        caminho_vocal (str): Caminho para o arquivo de áudio vocal
        sr (int): Taxa de amostragem
        
    Returns:
        list: Lista de tuplas (nota, duração)
    '''
    # Carrega o arquivo de áudio vocal
    sinal, taxa = carregar_audio(caminho_vocal, sr)
    
    # Detecta os onsets (inícios de notas)
    onsets = librosa.onset.onset_detect(y=sinal, sr=taxa, units='time')
    
    # Adiciona o final do áudio como último "onset" para calcular duração da última nota
    onsets = np.append(onsets, librosa.get_duration(y=sinal, sr=taxa))
    
    notas_com_duracao = []
    notas_map = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Para cada intervalo entre onsets, extrai a nota predominante
    for i in range(len(onsets)-1):
        inicio = int(onsets[i] * taxa)
        fim = int(onsets[i+1] * taxa)
        
        if fim <= inicio:
            continue
            
        trecho = sinal[inicio:fim]
        if len(trecho) == 0:
            continue
        
        # Extrai a frequência fundamental (f0) e converte para nota
        f0, voiced_flag, _ = librosa.pyin(trecho, fmin=librosa.note_to_hz('C2'), 
                                         fmax=librosa.note_to_hz('C6'), sr=taxa)
        
        # Remove NaNs e pega a média das frequências onde há voz
        f0_valid = f0[voiced_flag]
        if len(f0_valid) > 0:
            freq_media = np.mean(f0_valid)
            nota_midi = librosa.hz_to_midi(freq_media)
            
            # Converte a nota MIDI para nome de nota e oitava
            nota_idx = int(round(nota_midi)) % 12
            oitava = int(nota_midi // 12) - 1  # Ajuste para formato music21
            nome_nota = f"{notas_map[nota_idx]}{oitava}"
            
            # Duração em quartos de nota (assumindo BPM 120 como base)
            duracao = onsets[i+1] - onsets[i]
            duracao_quarter = duracao * (120/60)
            
            notas_com_duracao.append((nome_nota, duracao_quarter))
    
    return notas_com_duracao

def gerar_harmonias_vocais(notas_melodia):
    '''
    Recebe uma lista de tuplas (nota, duração) da melodia principal
    
    Args:
        notas_melodia (list): Lista de tuplas (nota, duração) da melodia principal
        
    Returns:
        dict: Dicionário com as vozes (Soprano, Contralto, Tenor) e suas notas
    '''
    harmonias = {
        'Soprano': [],
        'Contralto': [],
        'Tenor': []
    }
    
    for nota_str, duracao in notas_melodia:
        # Converter a string de nota para um objeto pitch
        nota_principal = pitch.Pitch(nota_str)
        
        # Soprano canta a melodia original
        harmonias['Soprano'].append((nota_str, duracao))
        
        # Contralto canta uma terça ou quarta abaixo
        nota_contralto = pitch.Pitch(nota_principal.nameWithOctave)
        nota_contralto.transpose(-4, inPlace=True)  # Terça maior abaixo
        harmonias['Contralto'].append((nota_contralto.nameWithOctave, duracao))
        
        # Tenor canta uma sexta ou oitava abaixo
        nota_tenor = pitch.Pitch(nota_principal.nameWithOctave)
        nota_tenor.transpose(-7, inPlace=True)  # Quinta justa abaixo
        harmonias['Tenor'].append((nota_tenor.nameWithOctave, duracao))
    
    return harmonias
