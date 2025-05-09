import tkinter as tk
import os
from tkinter import filedialog

def selecionar_arquivo():
    """
    Abre uma janela para o usuário selecionar um arquivo de áudio.
    
    Returns:
        str: Caminho do arquivo selecionado ou None se nenhum arquivo for selecionado
    """
    # Inicializa o Tkinter mas oculta a janela principal
    root = tk.Tk()
    root.withdraw()
    
    # Exibe a janela principal e mantém ela no topo
    root.deiconify()
    root.attributes('-topmost', True)  # Mantém a janela sempre no topo
    
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