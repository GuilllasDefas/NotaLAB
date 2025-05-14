"""
Módulo para separação de stems (partes instrumentais) de um arquivo de áudio.
"""
from spleeter.separator import Separator


def separar_stems(caminho, saida='stems'):
    """
    Separa um arquivo de áudio em stems (vocal, baixo, bateria, outros).

    Args:
        caminho (str): Caminho para o arquivo de áudio
        saida (str): Pasta para salvar os stems extraídos

    Returns:
        str: Mensagem de confirmação
    """
    sep = Separator('spleeter:4stems')
    sep.separate_to_file(caminho, saida)
    return f"Stems salvos em '{saida}'"
