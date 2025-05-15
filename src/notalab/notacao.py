"""
Módulo para geração de partituras e notação musical.
"""
from music21 import chord, note, stream


def montar_harmonia(notas_por_voz):
    """
    Monta a partitura, respeitando pausas e evitando notas inválidas.
    """
    partitura = stream.Score()
    vozes = list(notas_por_voz.keys())
    sequencias = [notas_por_voz[v] for v in vozes]
    parte = stream.Part()
    parte.id = 'Coral'
    for eventos in zip(*sequencias):
        notas = [n for n, _ in eventos]
        duracoes = [d for _, d in eventos]
        dur = duracoes[0]
        notas_unicas = set(notas)
        if all(n is None or n.lower() == 'rest' for n in notas):
            nobj = note.Rest()
            nobj.quarterLength = dur
            parte.append(nobj)
        elif len(notas_unicas) == 1:
            n = list(notas_unicas)[0]
            try:
                nobj = note.Note(n)
            except Exception:
                nobj = note.Rest()
            nobj.quarterLength = dur
            parte.append(nobj)
        else:
            notas_validas = [
                n for n in notas if n is not None and n.lower() != 'rest'
            ]
            try:
                c = chord.Chord(notas_validas)
                c.quarterLength = dur
                parte.append(c)
            except Exception:
                nobj = note.Rest()
                nobj.quarterLength = dur
                parte.append(nobj)
    partitura.append(parte)
    return partitura


def montar_acordes(acordes_idx, notas, duracao=2):
    """
    Gera uma partitura com os acordes detectados, sincronizados por segmento maior.

    Args:
        acordes_idx (list): Lista de índices dos acordes detectados
        notas (list): Lista de nomes das notas (ex: ['C', 'C#', ...])
        duracao (int): Duração padrão para cada acorde ou pausa

    Returns:
        music21.stream.Part: Partitura com os acordes
    """
    acordes_part = stream.Part()
    acordes_part.id = 'Acordes'

    for idx in acordes_idx:
        if idx is None or idx < 0 or idx >= len(notas):
            acorde = note.Rest()
        else:
            acorde = chord.Chord([notas[idx]])
        acorde.quarterLength = duracao
        acordes_part.append(acorde)

    return acordes_part
