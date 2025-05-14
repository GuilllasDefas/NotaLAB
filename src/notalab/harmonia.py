import librosa
import numpy as np
from music21 import pitch

import config.config as config
from notalab.audio import carregar_audio


def quantizar_notas(notas_duracao, bpm, grade=16, ativar=True):
    """
    Quantiza as notas para alinhá-las à grade musical.

    Args:
        notas_duracao (list): Lista de tuplas (nota, duração)
        bpm (int): Andamento em batidas por minuto
        grade (int): Divisão da grade musical (4=semínimas, 8=colcheias, 16=semicolcheias)
        ativar (bool): Se False, retorna as notas inalteradas

    Returns:
        list: Lista de tuplas (nota, duração) com ritmo quantizado
    """
    if not ativar or not notas_duracao:
        return notas_duracao

    # Valor de uma batida em quarter notes
    beat_duration = 1.0

    # Duração de uma unidade da grade (em quarter notes)
    grid_unit = beat_duration / (grade / 4)

    # Processar cada nota
    quantizadas = []
    for nota, duracao in notas_duracao:
        # Quantizar posição: arredondar para o múltiplo mais próximo de grid_unit
        qnt_duracao = round(duracao / grid_unit) * grid_unit

        # Evitar notas com duração zero
        if qnt_duracao < grid_unit:
            qnt_duracao = grid_unit

        quantizadas.append((nota, qnt_duracao))

    return quantizadas


def extrair_notas_vocal(
    caminho_vocal,
    sr=44100,
    bpm=120,
    min_dur=config.MIN_DURACAO_NOTA,
    tom='C',
    modo='maior',
    sensibilidade_onset=config.SENSIBILIDADE_ONSET,
    limite_agrupamento=config.LIMITE_AGRUPAMENTO,
    quantizar=config.QUANTIZAR,
    grade_quantizacao=config.GRADE_QUANTIZACAO,
    pre_max=config.PRE_MAX,
    post_max=config.POST_MAX,
    pre_avg=config.PRE_AVG,
    post_avg=config.POST_AVG,
    wait=config.WAIT,
):
    """
    Extrai notas vocais com ajustes para melhorar a precisão rítmica.
    Todos os parâmetros de configuração estão documentados em config.py
    """
    # Carregar e normalizar áudio
    sinal, taxa = carregar_audio(caminho_vocal, sr)
    sinal = librosa.util.normalize(sinal)

    # Definir escala baseada no tom e modo
    notas_map = [
        'C',
        'C#',
        'D',
        'D#',
        'E',
        'F',
        'F#',
        'G',
        'G#',
        'A',
        'A#',
        'B',
    ]
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
            nota_completa = f'{nota_nome}{oitava}'
            freq_notas[nota_completa] = librosa.note_to_hz(nota_completa)

    # Detectar onsets com parâmetros configuráveis
    onsets = librosa.onset.onset_detect(
        y=sinal,
        sr=taxa,
        units='time',
        backtrack=True,
        pre_max=pre_max,
        post_max=post_max,
        pre_avg=pre_avg,
        post_avg=post_avg,
        delta=sensibilidade_onset,
        wait=wait,
    )

    # Se temos poucos onsets, tentar novamente com parâmetros ainda mais sensíveis
    if len(onsets) < 10:
        onsets = librosa.onset.onset_detect(
            y=sinal,
            sr=taxa,
            units='time',
            backtrack=True,
            pre_max=0.01,  # Reduzido: mais sensível a picos locais
            post_max=0.01,  # Reduzido: mais sensível a picos locais
            pre_avg=0.03,  # Reduzido: janela menor para média = mais sensível
            post_avg=0.03,  # Reduzido: janela menor para média = mais sensível
            delta=0.03,  # Reduzido: aceita diferenças de energia menores
            wait=0.01,  # Mantido: ainda precisamos separar notas distintas
        )

    # Adicionar o início e fim do áudio
    onsets = np.append(np.array([0]), onsets)
    onsets = np.append(onsets, librosa.get_duration(y=sinal, sr=taxa))

    # Processar cada segmento entre onsets
    notas_com_duracao = []

    for i in range(len(onsets) - 1):
        inicio = int(onsets[i] * taxa)
        fim = int(onsets[i + 1] * taxa)

        if fim <= inicio:
            continue

        # Reduzir duração mínima para capturar notas rápidas
        if fim - inicio < taxa * min_dur and i > 0 and i < len(onsets) - 2:
            continue

        # Extrair segmento de áudio
        segmento = sinal[inicio:fim]
        duracao = onsets[i + 1] - onsets[i]
        duracao_quarter = duracao * (bpm / 60)

        # Análise de frequência fundamental com threshold mais baixo
        f0, voiced_flag, voiced_prob = librosa.pyin(
            segmento,
            fmin=librosa.note_to_hz('C2'),  # Limite inferior: C2 (aprox. 65Hz)
            fmax=librosa.note_to_hz(
                'C6'
            ),  # Limite superior: C6 (aprox. 1047Hz)
            sr=taxa,
            fill_na=None,  # Não preenche valores ausentes
        )

        # Threshold mais baixo para detectar mais nuances (0.4 em vez de 0.6)
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
                if menor_distancia < 0.15:
                    notas_com_duracao.append(
                        (nota_mais_proxima, duracao_quarter)
                    )
                else:
                    # Verificar se há energia suficiente para ser uma nota
                    rms = np.sqrt(np.mean(segmento**2))
                    if (
                        rms > 0.01
                    ):  # Se tiver energia mínima, tenta forçar para a escala
                        notas_com_duracao.append(
                            (nota_mais_proxima, duracao_quarter)
                        )
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

    # Usar o valor de limite_agrupamento passado como parâmetro
    limite_agrup_quarter = limite_agrupamento * (60 / bpm)

    for i in range(1, len(notas_com_duracao)):
        nota, dur = notas_com_duracao[i]

        # Agrupar apenas se for a mesma nota E a duração não exceder o limite
        if nota == nota_atual and dur_atual < limite_agrup_quarter:
            dur_atual += dur
        else:
            # Nova nota, registrar a anterior e começar nova
            notas_processadas.append((nota_atual, dur_atual))
            nota_atual, dur_atual = nota, dur

    # Adicionar a última nota
    notas_processadas.append((nota_atual, dur_atual))

    # Quantização opcional das notas para alinhamento rítmico
    if quantizar:
        notas_processadas = quantizar_notas(
            notas_processadas, bpm, grade_quantizacao
        )

    return notas_processadas


def gerar_harmonias_vocais(notas_melodia, tom='C', modo='maior'):
    """
    Gera harmonias em uníssono, mantendo a mesma nota em diferentes oitavas.
    """
    harmonias = {'Soprano': [], 'Contralto': [], 'Tenor': []}

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
            while contralto.midi < 48:
                contralto.octave += 1
            while tenor.midi < 36:
                tenor.octave += 1

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
