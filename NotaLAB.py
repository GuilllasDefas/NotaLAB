import os
from notalab.audio import carregar_audio, detectar_tom, detectar_bpm, detectar_acordes
from notalab.stems import separar_stems
from notalab.notacao import montar_harmonia
from notalab.harmonia import extrair_notas_vocal, gerar_harmonias_vocais

"""
Script principal do NotaLAB - Ferramenta de análise e geração musical
"""

def main():
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

if __name__ == '__main__':
    main()