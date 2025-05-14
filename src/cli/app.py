import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'   # Ignora avisos do TensorFlow

import warnings
from pathlib import Path

from music21 import midi

import config.config as config
from notalab.audio import (carregar_audio, detectar_acordes, detectar_bpm,
                           detectar_tom)
from notalab.harmonia import extrair_notas_vocal, gerar_harmonias_vocais
from notalab.notacao import montar_acordes, montar_harmonia
from notalab.stems import separar_stems
from utils.set import selecionar_arquivo

warnings.filterwarnings(
    'ignore', message='n_fft=1024 is too large for input signal'
)
warnings.filterwarnings(
    'ignore', message='n_fft=256 is too large for input signal'
)
"""
Script principal do NotaLAB - Ferramenta de análise e geração musical

Para ajustar parâmetros, edite o arquivo config.py que contém todas as 
configurações centralizadas com explicações detalhadas.
"""


def main():
    print('\n=== NotaLAB - Análise e Geração Musical ===\n')

    # Solicitar ao usuário que selecione o arquivo de áudio
    caminho_audio = selecionar_arquivo()

    # Verifica se o usuário selecionou um arquivo
    if not caminho_audio:
        print('Nenhum arquivo selecionado. Encerrando.')
        return

    print(f'Arquivo selecionado: {caminho_audio}')

    # Carrega o áudio selecionado
    try:
        sinal, taxa = carregar_audio(caminho_audio)
    except Exception as e:
        print(f'Erro ao carregar o arquivo: {e}')
        return

    # Analisa características do áudio
    print('\nAnalisando áudio...')
    tonica, modo = detectar_tom(sinal, taxa)
    print(f'Tonalidade: {tonica} {modo}')
    bpm = detectar_bpm(sinal, taxa)
    print('BPM:', bpm)

    acordes_idx = detectar_acordes(sinal, taxa, bpm=bpm)
    notas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    acordes_nomes = [notas[idx] for idx in acordes_idx]
    print('Acordes detectados:', ', '.join(acordes_nomes))

    # Separar os stems
    print('\nSeparando vozes e instrumentos...')
    print(separar_stems(caminho_audio))

    # Extrai o nome do arquivo sem extensão para usar na pasta de stems
    nome_arquivo = Path(caminho_audio).stem

    # Caminho para o arquivo vocal extraído pelo spleeter
    caminho_vocal = os.path.join('stems', nome_arquivo, 'vocals.wav')

    # Verifica se o arquivo de vocal existe
    if not os.path.exists(caminho_vocal):
        print(f'Arquivo vocal não encontrado em: {caminho_vocal}')
        return

    # Extrair notas do vocal e gerar harmonias automáticas
    print('\nExtraindo notas do vocal e gerando harmonias...')

    # Opção 1: Usar as configurações do config.py
    notas_melodia = extrair_notas_vocal(
        caminho_vocal,
        bpm=bpm,
        tom=tonica,
        modo=modo,
        sensibilidade_onset=config.SENSIBILIDADE_ONSET,
        limite_agrupamento=config.LIMITE_AGRUPAMENTO,
        min_dur=config.MIN_DURACAO_NOTA,
        quantizar=config.QUANTIZAR,
        grade_quantizacao=config.GRADE_QUANTIZACAO,
        # Parâmetros avançados
        pre_max=config.PRE_MAX,
        post_max=config.POST_MAX,
        pre_avg=config.PRE_AVG,
        post_avg=config.POST_AVG,
        wait=config.WAIT,
    )

    # Opção 2: Usar configurações específicas de estilo (descomente para usar)
    # estilo = 'pop'  # Escolha: 'vocal', 'pop', 'jazz', 'classica', 'folk', etc.
    # config_estilo = config.obter_config_para_estilo(estilo, bpm)
    # notas_melodia = extrair_notas_vocal(
    #     caminho_vocal,
    #     bpm=bpm,
    #     tom=tonica,
    #     modo=modo,
    #     sensibilidade_onset=config_estilo['sensibilidade_onset'],
    #     limite_agrupamento=config_estilo['limite_agrupamento'],
    #     min_dur=config_estilo['min_duracao'],
    #     quantizar=config_estilo['quantizar'],
    #     grade_quantizacao=config_estilo['grade_quantizacao']
    # )

    if notas_melodia:
        print(f'Extraídas {len(notas_melodia)} notas da melodia vocal')
        harmonias = gerar_harmonias_vocais(
            notas_melodia, tom=tonica, modo=modo
        )
        partitura = montar_harmonia(harmonias)

        # Não adicione acordes extras aqui!
        # O MIDI agora respeita momentos de notas únicas e acordes

        # Exportar para arquivo MIDI
        mf = midi.translate.streamToMidiFile(partitura)
        mf.open('harmonias_vocais.mid', 'wb')
        mf.write()
        mf.close()
    else:
        print('Não foi possível extrair notas do vocal.')


if __name__ == '__main__':
    main()
