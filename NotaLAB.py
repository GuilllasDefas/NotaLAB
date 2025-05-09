import os
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from notalab.audio import carregar_audio, detectar_tom, detectar_bpm, detectar_acordes
from notalab.stems import separar_stems
from notalab.notacao import montar_harmonia
from notalab.harmonia import extrair_notas_vocal, gerar_harmonias_vocais

"""
Script principal do NotaLAB - Ferramenta de análise e geração musical
"""

def selecionar_arquivo():
    """
    Abre uma janela para o usuário selecionar um arquivo de áudio.
    
    Returns:
        str: Caminho do arquivo selecionado ou None se nenhum arquivo for selecionado
    """
    # Inicializa o Tkinter mas oculta a janela principal
    root = tk.Tk()
    root.withdraw()
    
    # Define os tipos de arquivos de áudio suportados
    tipos_arquivo = [
        ('Arquivos de Áudio', '*.mp3 *.wav *.flac *.ogg *.m4a'),
        ('MP3', '*.mp3'),
        ('WAV', '*.wav'),
        ('FLAC', '*.flac'),
        ('OGG', '*.ogg'),
        ('Todos os Arquivos', '*.*')
    ]
    
    # Abre o diálogo de seleção de arquivo
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione um arquivo de áudio",
        filetypes=tipos_arquivo,
        initialdir=os.path.expanduser("~")  # Começa no diretório do usuário
    )
    
    # Destrói a janela do Tkinter após a seleção
    root.destroy()
    
    return caminho_arquivo if caminho_arquivo else None

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

if __name__ == '__main__':
    main()