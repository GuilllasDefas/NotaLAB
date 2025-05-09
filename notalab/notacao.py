"""
Módulo para geração de partituras e notação musical.
"""
from music21 import stream, note

def montar_harmonia(notas_por_voz):
    '''
    Gera linhas de harmonia para corais (Soprano, Contralto, Tenor).
    
    Args:
        notas_por_voz (dict): Dicionário com chaves para cada voz ('Soprano', 'Contralto', 'Tenor')
                             e valores como listas de tuplas (nota, duração)
        
    Returns:
        music21.stream.Score: Partitura com as partes vocais
    '''
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
