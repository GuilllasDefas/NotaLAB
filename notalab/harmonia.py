"""
Módulo para funções relacionadas a harmonia e extração de notas.

DICAS PARA AJUSTAR RITMO, TEMPO E DURAÇÃO DAS NOTAS:

- min_dur (float): Duração mínima em segundos para considerar uma nota.
    * AUMENTAR: ignora notas rápidas, só pega notas longas/sustentadas, ritmo mais "limpo".
    * DIMINUIR: captura mais notas rápidas, trinados, ornamentos, ritmo mais detalhado.

- pre_max, post_max, pre_avg, post_avg (onset_detect): Janelas para detectar início das notas.
    * VALORES MAIORES: menos notas detectadas, só ataques fortes.
    * VALORES MENORES: mais notas detectadas, sensível a pequenas variações.

- delta (onset_detect): Sensibilidade à diferença de energia para detectar início de nota.
    * MAIOR: só pega notas com ataque forte, ritmo simplificado.
    * MENOR: pega até ataques suaves, ritmo mais fragmentado.

- wait (onset_detect): Tempo mínimo entre notas detectadas.
    * MAIOR: evita notas muito próximas, ritmo mais "quadrado".
    * MENOR: permite notas rápidas em sequência, ritmo mais detalhado.

- Agrupamento de notas iguais (limite_agrupamento):
    * MAIOR: notas longas, menos detalhes rítmicos.
    * MENOR: notas curtas, mais detalhes rítmicos.

- bpm: Batidas por minuto.
    * Se o BPM detectado estiver errado, todas as durações ficarão desproporcionais.
    * quarterLength = duração_em_segundos * (BPM/60)
"""
import numpy as np
import librosa
from music21 import pitch
from notalab.audio import carregar_audio

def extrair_notas_vocal(caminho_vocal, sr=44100, bpm=120, min_dur=0.05, tom='C', modo='maior'):
    '''
    Extrai notas vocais aderindo à escala do tom detectado, mas preservando os nuances da melodia.
    Veja o comentário do módulo para dicas de ajuste de ritmo e duração.
    
    Args:
        caminho_vocal (str): Caminho para o arquivo de áudio vocal
        sr (int): Taxa de amostragem em Hz.
                  → MAIOR: captará sons mais agudos, mas usa mais memória
                  → MENOR: processamento mais rápido, perde detalhes agudos
        bpm (int): Batidas por minuto da música.
                  → MAIOR: notas terão durações menores no MIDI
                  → MENOR: notas terão durações maiores no MIDI
        min_dur (float): Duração mínima em segundos para uma nota ser considerada.
                  → MAIOR: ignora notas rápidas, reduz ruídos, menos notas no total
                  → MENOR: captura ornamentos e notas rápidas, mais notas no total
        tom (str): Nota tônica da música (ex: 'C', 'D#')
        modo (str): Modo da escala ('maior' ou 'menor')
    
    Returns:
        list: Lista de tuplas (nota, duração) com as notas detectadas
    '''
    # Carregar e normalizar áudio
    sinal, taxa = carregar_audio(caminho_vocal, sr)
    sinal = librosa.util.normalize(sinal)
    
    # Definir escala baseada no tom e modo
    notas_map = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    tom_idx = notas_map.index(tom)
    
    # Selecionar escala apropriada
    if modo == 'maior':
        escala = [(tom_idx + i) % 12 for i in [0, 2, 4, 5, 7, 9, 11]]
    else:  # modo menor
        escala = [(tom_idx + i) % 12 for i in [0, 2, 3, 5, 7, 8, 10]]
    
    # Criar mapa de frequências para cada nota da escala
    freq_notas = {}
    for i in escala:
        nota_nome = notas_map[i]
        for oitava in range(2, 6):  # Oitavas C2-B5
            nota_completa = f"{nota_nome}{oitava}"
            freq_notas[nota_completa] = librosa.note_to_hz(nota_completa)
    
    # Detectar onsets com parâmetros mais sensíveis para capturar mais nuances
    # PARÂMETROS DE DETECÇÃO DO INÍCIO DAS NOTAS:
    # pre_max/post_max: Janelas de tempo para encontrar inícios de notas
    #   → MAIOR: Ignora inícios de notas próximos, resultando em menos notas
    #   → MENOR: Detecta mais inícios, resultando em mais notas separadas
    #
    # pre_avg/post_avg: Janelas para calcular a média de energia
    #   → MAIOR: Ignora pequenas variações, menos sensível a vibratos/tremulos
    #   → MENOR: Captura pequenas mudanças de volume, mais sensível a nuances
    #
    # delta: Diferença de energia necessária para considerar o início de uma nota
    #   → MAIOR: Só detecta notas com ataques fortes/evidentes
    #   → MENOR: Detecta notas com ataques suaves, mas pode pegar ruídos
    #
    # wait: Tempo mínimo entre notas consecutivas
    #   → MAIOR: Evita notas muito próximas, menos notas no total
    #   → MENOR: Permite notas muito rápidas em sequência, mais notas no total
    onsets = librosa.onset.onset_detect(
        y=sinal,
        sr=taxa,
        units='time',
        backtrack=True,        # Ajusta onset para o início real do transiente
        pre_max=0.02,          # 20ms antes
        post_max=0.02,         # 20ms depois
        pre_avg=0.04,          # 50ms de janela para média antes
        post_avg=0.03,         # 50ms de janela para média depois
        delta=0.04,            # 4% de diferença de energia
        wait=0.01              # 10ms de espera mínima entre onsets
    )
    
    # Se temos poucos onsets, tentar novamente com parâmetros ainda mais sensíveis
    # Parâmetros mais agressivos para capturar nuances mais sutis
    if len(onsets) < 10:
        onsets = librosa.onset.onset_detect(
            y=sinal,
            sr=taxa,
            units='time',
            backtrack=True,
            pre_max=0.01,      # Reduzido: mais sensível a picos locais
            post_max=0.01,     # Reduzido: mais sensível a picos locais
            pre_avg=0.03,      # Reduzido: janela menor para média = mais sensível
            post_avg=0.03,     # Reduzido: janela menor para média = mais sensível
            delta=0.03,        # Reduzido: aceita diferenças de energia menores
            wait=0.01          # Mantido: ainda precisamos separar notas distintas
        )
    
    # Adicionar o início e fim do áudio
    onsets = np.append(np.array([0]), onsets)
    onsets = np.append(onsets, librosa.get_duration(y=sinal, sr=taxa))
    
    # Processar cada segmento entre onsets
    notas_com_duracao = []
    
    for i in range(len(onsets) - 1):
        inicio = int(onsets[i] * taxa)
        fim = int(onsets[i+1] * taxa)
        
        if fim <= inicio:
            continue
        
        # Reduzir duração mínima para capturar notas rápidas
        if fim - inicio < taxa * min_dur and i > 0 and i < len(onsets) - 2:
            continue
        
        # Extrair segmento de áudio
        segmento = sinal[inicio:fim]
        duracao = onsets[i+1] - onsets[i]
        duracao_quarter = duracao * (bpm/60)
        
        # Análise de frequência fundamental com threshold mais baixo
        # CONFIGURAÇÕES DE DETECÇÃO DE ALTURA/AFINAÇÃO:
        # fmin/fmax: Limites das notas que serão detectadas
        #   → MAIOR FAIXA (C1-C7): Detecta notas muito graves e muito agudas
        #   → MENOR FAIXA (C3-C5): Foca apenas na região central da voz
        #
        # voiced_prob: Confiança mínima para considerar que é uma nota cantada
        #   → MAIOR (>0.5): Só aceita trechos claramente cantados, menos notas
        #   → MENOR (<0.5): Aceita sons menos definidos como notas, mais notas
        f0, voiced_flag, voiced_prob = librosa.pyin(
            segmento,
            fmin=librosa.note_to_hz('C2'),  # Limite inferior: C2 (aprox. 65Hz)
            fmax=librosa.note_to_hz('C6'),  # Limite superior: C6 (aprox. 1047Hz)
            sr=taxa,
            fill_na=None                    # Não preenche valores ausentes
        )
        
        # Threshold mais baixo para detectar mais nuances (0.4 em vez de 0.6)
        # Filtro de probabilidade para frames vocais
        # - Aumentar o threshold (>0.4): menos notas, maior precisão
        # - Diminuir o threshold (<0.4): mais notas, menor precisão
        if f0 is not None and np.any(voiced_flag):
            valid_f0 = f0[voiced_flag & (voiced_prob > 0.4)]
            
            if len(valid_f0) > 0 and not np.all(np.isnan(valid_f0)):
                freq_mediana = np.nanmedian(valid_f0)
                
                # Encontrar a nota mais próxima na escala
                nota_mais_proxima = None
                menor_distancia = float('inf')
                
                for nota, freq in freq_notas.items():
                    distancia = abs(freq - freq_mediana) / freq
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        nota_mais_proxima = nota
                
                # Tolerância para considerar uma nota válida
                # → MAIOR (>0.15): Aceita notas mais "desafinadas", mais flexível
                # → MENOR (<0.15): Exige notas bem afinadas, mais rigoroso, menos notas
                if menor_distancia < 0.15:
                    notas_com_duracao.append((nota_mais_proxima, duracao_quarter))
                else:
                    # Verificar se há energia suficiente para ser uma nota
                    rms = np.sqrt(np.mean(segmento**2))
                    # Energia mínima para considerar um trecho como nota
                    # → MAIOR (>0.01): Ignora sons fracos, só detecta notas cantadas com clareza
                    # → MENOR (<0.01): Capta sons mais suaves, incluindo respirações e ruídos
                    if rms > 0.01:  # Se tiver energia mínima, tenta forçar para a escala
                        notas_com_duracao.append((nota_mais_proxima, duracao_quarter))
                    else:
                        notas_com_duracao.append(('rest', duracao_quarter))
            else:
                notas_com_duracao.append(('rest', duracao_quarter))
        else:
            notas_com_duracao.append(('rest', duracao_quarter))
    
    # Pós-processamento: limitar o agrupamento para preservar nuances
    if not notas_com_duracao:
        return []
    
    notas_processadas = []
    nota_atual, dur_atual = notas_com_duracao[0]
    
    # Limite para juntar notas iguais consecutivas
    # → MAIOR (>4): Junta mais notas iguais, criando notas mais longas
    # → MENOR (<4): Mantém as notas separadas, preservando o ritmo original
    limite_agrupamento = 4 * (60/bpm)  # Máximo de 4 tempos agrupados
    
    for i in range(1, len(notas_com_duracao)):
        nota, dur = notas_com_duracao[i]
        
        # Agrupar apenas se for a mesma nota E a duração não exceder o limite
        if nota == nota_atual and dur_atual < limite_agrupamento:
            dur_atual += dur
        else:
            # Nova nota, registrar a anterior e começar nova
            notas_processadas.append((nota_atual, dur_atual))
            nota_atual, dur_atual = nota, dur
    
    # Adicionar a última nota
    notas_processadas.append((nota_atual, dur_atual))
    
    return notas_processadas

def gerar_harmonias_vocais(notas_melodia, tom='C', modo='maior'):
    '''
    Gera harmonias em uníssono, mantendo a mesma nota em diferentes oitavas.
    '''
    harmonias = {
        'Soprano': [],
        'Contralto': [],
        'Tenor': []
    }
    
    for nota_str, duracao in notas_melodia:
        if nota_str is None or nota_str.lower() == 'rest':
            # Pausas para todas as vozes
            harmonias['Soprano'].append(('rest', duracao))
            harmonias['Contralto'].append(('rest', duracao))
            harmonias['Tenor'].append(('rest', duracao))
            continue
        
        try:
            # Criar objetos pitch para manipulação
            soprano = pitch.Pitch(nota_str)
            
            # Contralto é a mesma nota, mas uma oitava abaixo se necessário
            contralto = pitch.Pitch(nota_str)
            if contralto.midi > 65:  # Se for muito agudo
                contralto.octave -= 1
                
            # Tenor é tipicamente duas oitavas abaixo
            tenor = pitch.Pitch(nota_str)
            tenor.octave -= 1
            if tenor.midi > 60:
                tenor.octave -= 1
                
            # Garantir tessitura vocal adequada
            while contralto.midi < 48: contralto.octave += 1
            while tenor.midi < 36: tenor.octave += 1
            
            # Adicionar às vozes
            harmonias['Soprano'].append((soprano.nameWithOctave, duracao))
            harmonias['Contralto'].append((contralto.nameWithOctave, duracao))
            harmonias['Tenor'].append((tenor.nameWithOctave, duracao))
            
        except Exception:
            # Em caso de erro, usar pausas
            harmonias['Soprano'].append(('rest', duracao))
            harmonias['Contralto'].append(('rest', duracao))
            harmonias['Tenor'].append(('rest', duracao))
    
    return harmonias
