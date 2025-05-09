import librosa
import numpy as np
import os

from spleeter.separator import Separator # vai servir para separar os instrumentos (voz, baixo, bateria e outros)
from music21 import stream, note, chord, pitch # para manipular as notas musicais

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

# Nova função para extrair notas melódicas do vocal com suas durações
def extrair_notas_vocal(caminho_vocal, sr=44100):
    '''
    Extrai as notas melódicas do arquivo vocal com suas durações.
    Retorna uma lista de tuplas (nota, duração)
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

# Gera harmonias automáticas para coral a partir de uma melodia vocal
def gerar_harmonias_vocais(notas_melodia):
    '''
    Recebe uma lista de tuplas (nota, duração) da melodia principal
    Retorna um dicionário com as vozes (Soprano, Contralto, Tenor) e suas notas
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

if __name__ == '__main__':
    # Exemplo de uso:
    audio = 'minha_musica.mp3'
    sinal, taxa = carregar_audio(audio)

    print('Tom:', detectar_tom(sinal, taxa))
    print('BPM:', detectar_bpm(sinal, taxa))

    acordes_idx = detectar_acordes(sinal, taxa)
    print('Acordes (índices):', acordes_idx)

    # Separar os stems primeiro
    print(separar_stems(audio))
    
    # Caminho para o arquivo vocal extraído pelo spleeter
    caminho_vocal = os.path.join('stems', 'minha_musica', 'vocals.wav')
    
    # Extrair notas do vocal e gerar harmonias automáticas
    print("Extraindo notas do vocal e gerando harmonias...")
    notas_melodia = extrair_notas_vocal(caminho_vocal)
    
    if notas_melodia:
        print(f"Extraídas {len(notas_melodia)} notas da melodia vocal")
        harmonias = gerar_harmonias_vocais(notas_melodia)
        
        # Gerar partitura com as harmonias
        partitura = montar_harmonia(harmonias)
        partitura.show('text')  # mostra no console
        
        # Opcional: salvar a partitura como MIDI ou PDF
        # partitura.write('midi', 'harmonias_vocais.mid')
    else:
        print("Não foi possível extrair notas do vocal. Usando exemplo manual:")
        
        # Exemplo de harmonia manual como fallback
        exemplo = {
            'Soprano': [('C4', 1), ('E4', 1)],
            'Contralto': [('A3', 1), ('B3', 1)],
            'Tenor': [('F3', 1), ('G3', 1)]
        }
        partitura = montar_harmonia(exemplo)
        partitura.show('text')  # mostra no console