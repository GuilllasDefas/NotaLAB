import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'   # Ignora avisos do TensorFlow

import warnings
from pathlib import Path

from music21 import midi

import config.config as config
from src.notalab.audio import (carregar_audio, detectar_acordes, detectar_bpm,
                           detectar_tom)
from src.notalab.harmonia import extrair_notas_vocal, gerar_harmonias_vocais
from src.notalab.notacao import montar_acordes, montar_harmonia
from src.notalab.stems import separar_stems
from src.utils.set import selecionar_arquivo

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


    if notas_melodia:
        print(f'Extraídas {len(notas_melodia)} notas da melodia vocal')
        harmonias = gerar_harmonias_vocais(
            notas_melodia, tom=tonica, modo=modo
        )
        partitura = montar_harmonia(harmonias)

        # Obtém o caminho para a raiz do projeto (2 níveis acima de src/cli)
        projeto_root = Path(__file__).parent.parent.parent
        
        # Cria o diretório data na raiz do projeto
        data_dir = projeto_root / 'data'
        data_dir.mkdir(exist_ok=True)
        
        # Caminho completo para o arquivo MIDI na pasta data
        caminho_midi = data_dir / 'harmonias_vocais.mid'
        
        # Exportar para arquivo MIDI
        mf = midi.translate.streamToMidiFile(partitura)
        mf.open(str(caminho_midi), 'wb')
        mf.write()
        mf.close()
        
        print(f'Arquivo MIDI salvo em: {caminho_midi}')
    else:
        print('Não foi possível extrair notas do vocal.')


if __name__ == '__main__':
    main()
