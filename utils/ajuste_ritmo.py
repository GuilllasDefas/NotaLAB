"""
Funções auxiliares para ajuste de ritmo e tempo na extração de notas.
Utiliza as configurações centralizadas em config.py
"""
import config

def calcular_grade_subdivisao(bpm):
    """
    Calcula a grade de subdivisão recomendada com base no BPM.
    Ver config.py para explicações detalhadas.
    """
    if bpm < 60:
        return 8    # BPM lento: use colcheias
    elif bpm < 100:
        return 16   # BPM médio: use semicolcheias
    else:
        return 32   # BPM rápido: use fusas

def ajustar_sensibilidade_onset(tipo_musica):
    """
    Retorna a sensibilidade de onset recomendada para o estilo musical.
    Ver config.py para valores e explicações detalhadas.
    """
    config_estilo = config.obter_config_para_estilo(tipo_musica)
    return config_estilo['sensibilidade_onset']

def recomendar_config_ritmo(bpm, tipo_musica='vocal'):
    """
    Fornece configurações completas recomendadas para o estilo e BPM.
    Utiliza as configurações em config.py.
    """
    return config.obter_config_para_estilo(tipo_musica, bpm)
