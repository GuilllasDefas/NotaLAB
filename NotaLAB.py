import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Ignora avisos do TensorFlow
from pathlib import Path
from notalab.audio import carregar_audio, detectar_tom, detectar_bpm, detectar_acordes
from notalab.stems import separar_stems
from notalab.notacao import montar_harmonia
from notalab.harmonia import extrair_notas_vocal, gerar_harmonias_vocais
from utils.set import selecionar_arquivo

"""
Script principal do NotaLAB - Ferramenta de análise e geração musical
"""

def main():
    print("=== NotaLAB - Análise e Geração Musical ===")
    
    # Solicitar ao usuário que selecione o arquivo de áudio
    caminho_audio = selecionar_arquivo()
    
    # Verifica se o usuário selecionou um arquivo
    if not caminho_audio:
        print("Nenhum arquivo selecionado. Encerrando.")
        return
    
    print(f"Arquivo selecionado: {caminho_audio}")
    
    # Carrega o áudio selecionado
    try:
        sinal, taxa = carregar_audio(caminho_audio)
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")
        return
    
    # Analisa características do áudio
    print('\nAnalisando áudio...')
    print('Tom:', detectar_tom(sinal, taxa))
    print('BPM:', detectar_bpm(sinal, taxa))

    acordes_idx = detectar_acordes(sinal, taxa)
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
        print(f"Arquivo vocal não encontrado em: {caminho_vocal}")
        return
    
    # Extrair notas do vocal e gerar harmonias automáticas
    print("\nExtraindo notas do vocal e gerando harmonias...")
    notas_melodia = extrair_notas_vocal(caminho_vocal)
    
    if notas_melodia:
        print(f"Extraídas {len(notas_melodia)} notas da melodia vocal")
        harmonias = gerar_harmonias_vocais(notas_melodia)
        
        # Gerar partitura com as harmonias
        partitura = montar_harmonia(harmonias)
        partitura.show('text')  # mostra no console
        partitura.write('midi', 'harmonias_vocais.pdf')
    else:
        print("Não foi possível extrair notas do vocal.")

if __name__ == '__main__':
    main()