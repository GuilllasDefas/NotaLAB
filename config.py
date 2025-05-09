"""
Configurações centralizadas para o NotaLAB

Este arquivo contém todos os parâmetros ajustáveis do sistema com explicações
detalhadas sobre cada um, seus efeitos e valores recomendados.

=============== COMO AJUSTAR PARÂMETROS ===============
1. Defina o tipo básico de música primeiro (vocal, pop, jazz, etc.)
2. Ajuste os parâmetros individuais conforme necessário
3. Teste com pequenos trechos antes de processar músicas inteiras
"""

#=== EXTRAÇÃO DE NOTAS E DETECÇÃO DE ONSETS ===

# Sensibilidade na detecção de início das notas (delta no onset_detect)
# → AUMENTAR (0.06-0.08): 
#     • Menos onsets detectados, só os mais evidentes
#     • RECOMENDADO PARA: Músicas com notas longas e sustentadas, vozes operísticas
#     • EXEMPLO: Em uma ária de ópera com notas longas, use 0.07
# → DIMINUIR (0.02-0.03): 
#     • Mais onsets detectados, incluindo ornamentos e ataques suaves
#     • RECOMENDADO PARA: Músicas com muitos detalhes rítmicos, passagens rápidas
#     • EXEMPLO: Para um solo de flauta com trinados e ornamentos, use 0.025
# → VALOR INTERMEDIÁRIO (0.04-0.05):
#     • Equilíbrio entre detalhes e notas principais
#     • RECOMENDADO PARA: Música pop, rock, a maioria das vozes
SENSIBILIDADE_ONSET = 0.035 # Para 99 bpm mais de 0.4 está errando muito
# → OBSERVAÇÃO: Para músicas com BPM muito baixo, considere aumentar o valor

# Duração mínima de uma nota em segundos (para considerar como nota válida)
# → AUMENTAR (0.1-0.2): 
#     • Ignora notas rápidas, captura apenas notas sustentadas
#     • RECOMENDADO PARA: Músicas lentas, baladas, corais
#     • EXEMPLO: Para um coral lento com 60 BPM, use 0.15
# → DIMINUIR (0.03-0.04): 
#     • Captura ornamentos, trinados e articulações rápidas
#     • RECOMENDADO PARA: Passagens rápidas, músicas virtuosas
#     • EXEMPLO: Para um solo de violino com muitas notas rápidas, use 0.03
# → RELAÇÃO COM BPM: Para músicas rápidas (>120 BPM), use valores menores
MIN_DURACAO_NOTA = 0.02

# Limite para agrupar notas iguais consecutivas (em tempos musicais)
# → AUMENTAR (5-8): 
#     • Junta muitas notas iguais em uma só nota longa
#     • RECOMENDADO PARA: Vozes sustentadas, música clássica com legato
#     • EXEMPLO: Para uma melodia com notas longas ligadas, use 6
# → DIMINUIR (1-2): 
#     • Mantém cada nota articulada separadamente
#     • RECOMENDADO PARA: Música percussiva, staccato, ritmos marcados
#     • EXEMPLO: Para um trecho com notas staccato, use 1
# → OBSERVAÇÃO: Valores entre 2-4 são bons para a maioria das canções pop/rock
LIMITE_AGRUPAMENTO = 3

# Ativar ou desativar a quantização (alinhamento à grade rítmica)
# → ATIVAR (True): 
#     • Ritmo preciso e "quadrado", facilita a leitura da partitura
#     • RECOMENDADO PARA: Pop, rock, eletrônica, dance, hip-hop
#     • EXEMPLO: Para uma música dance com batida mecânica, ative
# → DESATIVAR (False): 
#     • Preserva nuances de tempo e rubato, mais expressivo
#     • RECOMENDADO PARA: Música clássica, jazz, performances solo
#     • EXEMPLO: Para uma sonata de piano com rubato, desative

QUANTIZAR = True # True tem acertado mais

# Grade de quantização rítmica (se QUANTIZAR = True)
# → VALORES MAIS BAIXOS (4): 
#     • Semínimas - notas longas, simplifica muito o ritmo
#     • RECOMENDADO PARA: Músicas muito lentas, hinos, corais
#     • EXEMPLO: Para um coral com poucas variações rítmicas, use 4
# → VALORES INTERMEDIÁRIOS (8): 
#     • Colcheias - equilíbrio entre simplicidade e detalhe
#     • RECOMENDADO PARA: Baladas, rock lento, folk
#     • EXEMPLO: Para uma balada em 80 BPM, use 8
# → VALORES ALTOS (16): 
#     • Semicolcheias - bom nível de detalhe rítmico
#     • RECOMENDADO PARA: A maioria das músicas pop, rock médio
#     • EXEMPLO: Para uma música pop em 100-120 BPM, use 16
# → VALORES MUITO ALTOS (32): 
#     • Fusas - preserva detalhes rítmicos complexos
#     • RECOMENDADO PARA: Música muito rápida, técnica, virtuosa
#     • EXEMPLO: Para uma música eletrônica em 140+ BPM, use 32
GRADE_QUANTIZACAO = 16
# → OBSERVAÇÃO: Para BPM muito baixo, considere aumentar o valor

#=== PARÂMETROS AVANÇADOS DE DETECÇÃO DE ONSETS ===

# Janela ANTES do ponto para buscar máximo local (em segundos)
# → AUMENTAR (0.03-0.05): 
#     • Ignora ataques próximos, menos detecções, menos fragmentação
#     • RECOMENDADO PARA: Músicas com menos articulação, mais legato
#     • EXEMPLO: Para uma música com notas ligadas suavemente, use 0.04
# → DIMINUIR (0.01-0.02): 
#     • Separa cada pequeno ataque, mais preciso em passagens rápidas
#     • RECOMENDADO PARA: Música com muitas articulações, staccato
#     • EXEMPLO: Para capturar cada nota de uma passagem rápida de piano, use 0.01
PRE_MAX = 0.03

# Janela DEPOIS do ponto para buscar máximo local (em segundos)
# → AUMENTAR (0.03-0.05): 
#     • Agrupa ataques próximos, trata vibratos como uma nota
#     • RECOMENDADO PARA: Vozes operísticas, instrumentos com muito sustain
#     • EXEMPLO: Para uma voz com vibrato intenso, use 0.04-0.05
# → DIMINUIR (0.01-0.02): 
#     • Separa ataques seguidos, mais preciso em notas curtas
#     • RECOMENDADO PARA: Instrumentos percussivos, guitarra com palm mute
#     • EXEMPLO: Para uma bateria ou percussão, use 0.01
POST_MAX = 0.02

# Janela para calcular média ANTES do ponto (em segundos)
# → AUMENTAR (0.1-0.2): 
#     • Compara com trecho maior, menos sensível a pequenas variações
#     • RECOMENDADO PARA: Músicas com dinâmica variada, vozes expressivas
#     • EXEMPLO: Para uma ária com crescendos e diminuendos, use 0.15
# → DIMINUIR (0.02-0.04): 
#     • Compara com trecho mais curto, detecta mudanças sutis
#     • RECOMENDADO PARA: Música com articulação precisa, instrumentos de ataque
#     • EXEMPLO: Para um instrumento como violão com ataques claros, use 0.03
PRE_AVG = 0.04

# Janela para calcular média DEPOIS do ponto (em segundos)
# → AUMENTAR (0.1-0.2): 
#     • Considera trecho maior após a nota, ignora variações após o ataque
#     • RECOMENDADO PARA: Instrumentos com muito sustain, vozes com vibrato
#     • EXEMPLO: Para um saxofone com vibrato expressivo, use 0.15
# → DIMINUIR (0.02-0.04): 
#     • Reage a mudanças rápidas após o início da nota
#     • RECOMENDADO PARA: Músicas com muitas nuances, articulações precisas
#     • EXEMPLO: Para um violino com marcato, use 0.02
POST_AVG = 0.03

# Tempo mínimo entre onsets consecutivos (em segundos)
# → AUMENTAR (0.03-0.05): 
#     • Evita fragmentação, impõe espaçamento mínimo entre notas
#     • RECOMENDADO PARA: Evitar falsos positivos, simplificar passagens complexas
#     • EXEMPLO: Para uma voz com muito vibrato, use 0.04-0.05
# → DIMINUIR (0.01): 
#     • Permite notas muito próximas, sem impor limite artificial
#     • RECOMENDADO PARA: Músicas virtuosas, passagens muito rápidas
#     • EXEMPLO: Para um trecho com 32 notas por compasso, use 0.01
# → RELAÇÃO COM BPM: Para BPM > 140, use valores menores (≤ 0.01)
WAIT = 0.03

#=== PARÂMETROS DE ANÁLISE ESPECTRAL ===

# Limite de frequência mínima para detecção de notas (em Hz)
# → AUMENTAR (100-130 Hz): 
#     • Ignora frequências muito graves, reduz ruídos de baixa frequência
#     • RECOMENDADO PARA: Vozes femininas, instrumentos agudos
#     • EXEMPLO: Para soprano ou voz feminina, aumente para 130 Hz (C3)
# → DIMINUIR (50-60 Hz): 
#     • Captura notas mais graves, bom para vozes profundas
#     • RECOMENDADO PARA: Vozes masculinas graves, baixo, barítono
#     • EXEMPLO: Para baixo ou voz masculina grave, diminua para 55 Hz (A1)
FMIN = 65.0  # C2 em Hz

# Limite de frequência máxima para detecção de notas (em Hz)
# → AUMENTAR (1500-2000 Hz): 
#     • Captura harmônicos superiores, mais sensível a nuances
#     • RECOMENDADO PARA: Análise espectral detalhada, soprano coloratura
#     • EXEMPLO: Para um soprano agudo com notas até C7, aumente para 2093 Hz
# → DIMINUIR (700-900 Hz): 
#     • Foca na região fundamental da voz, menos sujeito a ruídos
#     • RECOMENDADO PARA: Ambientes ruidosos, gravações de baixa qualidade
#     • EXEMPLO: Para uma gravação com muito ruído de fundo, diminua para 880 Hz (A5)
FMAX = 1047.0  # C6 em Hz

# Threshold de probabilidade para considerar um frame como vocalizado
# → AUMENTAR (0.5-0.7): 
#     • Exige maior certeza, menos notas falsas, mais pausas
#     • RECOMENDADO PARA: Isolamento preciso de voz, ambientes ruidosos
#     • EXEMPLO: Para uma gravação ao vivo com ruído de público, use 0.6
# → DIMINUIR (0.3-0.4): 
#     • Mais liberal, menos pausas, capta respirações e transições
#     • RECOMENDADO PARA: Gravações limpas, vozes suaves ou sussurradas
#     • EXEMPLO: Para uma voz muito suave ou sussurrada, use 0.35
VOICED_THRESHOLD = 0.45

# Tolerância máxima de distância de frequência para aceitar nota na escala (%)
# → AUMENTAR (0.15-0.2): 
#     • Mais tolerante com notas desafinadas, menos rigoroso
#     • RECOMENDADO PARA: Cantores amadores, gravações históricas, jazz
#     • EXEMPLO: Para uma gravação antiga ou amadora, use 0.2 (20% de tolerância)
# → DIMINUIR (0.05-0.1): 
#     • Exige afinação mais precisa, mais rigoroso
#     • RECOMENDADO PARA: Cantores profissionais, música clássica
#     • EXEMPLO: Para um cantor de ópera profissional, use 0.08 (8% de tolerância)
TOLERANCIA_AFINACAO = 0.1

"""
===== GUIA DE CONFIGURAÇÕES POR CASO DE USO =====

* MÚSICA COM MUITOS ORNAMENTOS E TRINADOS:
  - sensibilidade_onset: 0.02-0.03 (mais sensível)
  - min_duracao: 0.03-0.04 (permite notas curtas)
  - limite_agrupamento: 1 (preserva cada nota)
  - quantizar: False (preserva timing original)

* VOZ COM VIBRATO INTENSO:
  - sensibilidade_onset: 0.04-0.05 (moderado)
  - pre_avg/post_avg: 0.1-0.15 (maiores, para ignorar ciclos do vibrato)
  - min_duracao: 0.06-0.08 (ignora fragmentos do vibrato)
  - limite_agrupamento: 3-4 (agrupa moderadamente)

* MÚSICA COM NOTAS STACCATO:
  - sensibilidade_onset: 0.03-0.04 (moderada sensibilidade)
  - wait: 0.01 (permite notas próximas)
  - min_duracao: 0.03-0.04 (permite notas curtas)
  - limite_agrupamento: 1 (preserva cada nota)

* MELODIA LENTA E SUSTENTADA:
  - sensibilidade_onset: 0.05-0.06 (menos sensível)
  - min_duracao: 0.1-0.15 (ignora pequenas variações)
  - limite_agrupamento: 5-6 (agrupa notas longas)
  - grade_quantizacao: 8 (colcheias são suficientes)

* VOZ COM MUITAS NOTAS RÁPIDAS E PASSAGENS:
  - sensibilidade_onset: 0.03 (mais sensível)
  - pre_max/post_max: 0.01 (detecta notas próximas) 
  - min_duracao: 0.03 (permite notas muito curtas)
  - grade_quantizacao: 32 (para capturar ritmos complexos)
"""
#=== CONFIGURAÇÕES POR TIPO DE MÚSICA ===

# Configurações recomendadas para diferentes estilos
CONFIGS_POR_ESTILO = {
    'vocal': {
        'sensibilidade_onset': 0.04,
        'min_duracao': 0.03,
        'limite_agrupamento': 3,
        'quantizar': True,
        'grade_quantizacao': 16
    },
    'a_capella': {
        'sensibilidade_onset': 0.03,
        'min_duracao': 0.05,
        'limite_agrupamento': 2,
        'quantizar': False,
        'grade_quantizacao': 16
    },
    'pop': {
        'sensibilidade_onset': 0.05,
        'min_duracao': 0.04,
        'limite_agrupamento': 2,
        'quantizar': True,
        'grade_quantizacao': 16
    },
    'rock': {
        'sensibilidade_onset': 0.05,
        'min_duracao': 0.05,
        'limite_agrupamento': 2,
        'quantizar': True,
        'grade_quantizacao': 8
    },
    'jazz': {
        'sensibilidade_onset': 0.035,
        'min_duracao': 0.04,
        'limite_agrupamento': 1,
        'quantizar': False,
        'grade_quantizacao': 16
    },
    'classica': {
        'sensibilidade_onset': 0.025,
        'min_duracao': 0.04,
        'limite_agrupamento': 1,
        'quantizar': False,
        'grade_quantizacao': 16
    },
    'folk': {
        'sensibilidade_onset': 0.045,
        'min_duracao': 0.06,
        'limite_agrupamento': 3,
        'quantizar': True,
        'grade_quantizacao': 8
    },
    'lentas': {
        'sensibilidade_onset': 0.05,
        'min_duracao': 0.1,
        'limite_agrupamento': 6,
        'quantizar': True,
        'grade_quantizacao': 8
    },
    'rapidas': {
        'sensibilidade_onset': 0.03,
        'min_duracao': 0.03,
        'limite_agrupamento': 1,
        'quantizar': True,
        'grade_quantizacao': 32
    }
}

def obter_config_para_estilo(estilo, bpm=None):
    """Retorna configurações recomendadas para o estilo musical

    Args:
        estilo (str): Estilo musical ('vocal', 'pop', 'jazz', etc.)
        bpm (int, optional): BPM da música, usado para ajustes

    Returns:
        dict: Dicionário com parâmetros recomendados
    """
    estilo = estilo.lower()
    config = CONFIGS_POR_ESTILO.get(estilo, CONFIGS_POR_ESTILO['vocal']).copy()
    
    # Ajusta grade_quantizacao baseado no BPM se fornecido
    if bpm is not None:
        if bpm < 60:
            config['grade_quantizacao'] = min(config['grade_quantizacao'], 8)
        elif bpm > 120:
            config['grade_quantizacao'] = max(config['grade_quantizacao'], 16)
    
    return config

# Função para análise automática e ajuste de parâmetros
import numpy as np
import librosa

def analisar_e_ajustar_parametros(sinal, taxa, bpm, tonica=None, modo=None):
    """
    Analisa características do áudio e retorna parâmetros otimizados
    
    Args:
        sinal: array do sinal de áudio
        taxa: taxa de amostragem em Hz
        bpm: batidas por minuto (se já calculado)
        tonica: nota tônica (opcional)
        modo: modo musical (opcional)
        
    Returns:
        dict: Dicionário com parâmetros otimizados
    """
    # Inicializa com valores padrão (conservadores)
    params = {
        'sensibilidade_onset': SENSIBILIDADE_ONSET,
        'min_duracao': MIN_DURACAO_NOTA,
        'limite_agrupamento': LIMITE_AGRUPAMENTO,
        'quantizar': QUANTIZAR,
        'grade_quantizacao': GRADE_QUANTIZACAO,
        'pre_max': PRE_MAX,
        'post_max': POST_MAX,
        'pre_avg': PRE_AVG,
        'post_avg': POST_AVG,
        'wait': WAIT,
        'voiced_threshold': VOICED_THRESHOLD,
        'remover_falsos_positivos': False
    }
    
    # 1. Análise de densidade rítmica
    onset_env = librosa.onset.onset_strength(y=sinal, sr=taxa)
    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=taxa)
    if len(onsets) > 0:
        densidade_onset = len(onsets) / (len(sinal) / taxa)
    else:
        densidade_onset = 0.5
    
    # 2. Análise da estrutura harmônica para identificar música coral/polifônica
    chroma = librosa.feature.chroma_cqt(y=sinal, sr=taxa)
    notas_por_frame = np.mean(np.sum(chroma > 0.3, axis=0))
    variacao_harmonica = np.mean(np.std(chroma, axis=1))
    
    # Análise adicional das características vocais
    centroide = np.mean(librosa.feature.spectral_centroid(y=sinal, sr=taxa))
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=sinal))
    
    # 3. Análise de percussividade vs. harmonicidade
    y_harmonic, y_percussive = librosa.effects.hpss(sinal)
    energia_harmonica = np.sum(y_harmonic**2)
    energia_percussiva = np.sum(y_percussive**2)
    razao_percussiva = energia_percussiva / (energia_harmonica + energia_percussiva + 1e-10)
    
    e_coral = False
    tipo_coral = None
    
    if notas_por_frame > 1.8 and variacao_harmonica < 0.3 and razao_percussiva < 0.4:
        e_coral = True
        if zcr > 0.1 and centroide > 3000:
            tipo_coral = "agudo"
        elif zcr < 0.05 and centroide < 2000:
            tipo_coral = "grave"
        else:
            tipo_coral = "misto"
        
        print(f"Características de música coral/polifônica detectadas (tipo: {tipo_coral})")
    
    if e_coral:
        params['quantizar'] = True
        if tipo_coral == "agudo":
            params['sensibilidade_onset'] = 0.032
            params['min_duracao'] = 0.075
            params['limite_agrupamento'] = 4
            params['wait'] = 0.022
            params['grade_quantizacao'] = 8
        elif tipo_coral == "grave":
            params['sensibilidade_onset'] = 0.038
            params['min_duracao'] = 0.1
            params['limite_agrupamento'] = 5
            params['wait'] = 0.028
            params['grade_quantizacao'] = 8
        else:
            params['sensibilidade_onset'] = 0.034
            params['min_duracao'] = 0.085
            params['limite_agrupamento'] = 4
            params['wait'] = 0.024
            params['grade_quantizacao'] = 8
        
        params['pre_max'] = 0.04
        params['post_max'] = 0.035
        params['pre_avg'] = 0.07
        params['post_avg'] = 0.06
        
        if bpm < 80:
            params['sensibilidade_onset'] = min(0.045, params['sensibilidade_onset'] + 0.008)
            params['min_duracao'] = params['min_duracao'] * 1.2
            params['limite_agrupamento'] += 1
            params['grade_quantizacao'] = 4
        elif bpm > 120:
            params['sensibilidade_onset'] = max(0.025, params['sensibilidade_onset'] - 0.005)
            params['min_duracao'] = max(0.05, params['min_duracao'] * 0.9)
            params['wait'] = max(0.015, params['wait'] - 0.005)
            params['grade_quantizacao'] = 16
            
        if densidade_onset > 2.0:
            params['sensibilidade_onset'] = max(0.028, params['sensibilidade_onset'] - 0.004)
            params['limite_agrupamento'] = max(2, params['limite_agrupamento'] - 1)
        elif densidade_onset < 1.0:
            params['sensibilidade_onset'] = min(0.05, params['sensibilidade_onset'] + 0.005)
            params['limite_agrupamento'] += 1
            params['min_duracao'] = params['min_duracao'] * 1.1
    else:
        if bpm < 90:
            params['sensibilidade_onset'] = min(0.05, SENSIBILIDADE_ONSET + 0.01)
            params['min_duracao'] = max(0.06, 60 / (bpm * 8))
            params['grade_quantizacao'] = 8
        elif bpm > 120:
            params['sensibilidade_onset'] = max(0.025, SENSIBILIDADE_ONSET - 0.01)
            params['min_duracao'] = max(0.02, 60 / (bpm * 12))
            params['grade_quantizacao'] = 16
    
    if e_coral:
        if 85 <= bpm <= 105:
            params['grade_quantizacao'] = 8
            if bpm % 4 > 2:
                params['quantizar'] = True
        
        if variacao_harmonica < 0.15:
            params['limite_agrupamento'] = min(8, params['limite_agrupamento'] + 1)
            params['min_duracao'] = params['min_duracao'] * 1.05
            
        if tonica in ['C', 'F', 'G', 'D'] and modo == 'maior':
            params['min_duracao'] = params['min_duracao'] * 1.05
            params['pre_avg'] = min(0.09, params['pre_avg'] + 0.01)
    
    return params

# Função simplificada para filtragem de falsos positivos
def filtrar_falsos_positivos(notas, energia_minima=0.15, duracao_minima=0.05, distancia_minima=0.1):
    """
    Filtra notas que provavelmente são falsos positivos com base no formato de dados disponíveis
    
    Args:
        notas: lista de notas extraídas
        energia_minima: energia mínima para considerar uma nota válida (não utilizada na versão simplificada)
        duracao_minima: duração mínima em segundos (não utilizada na versão simplificada)
        distancia_minima: distância mínima entre notas (em segundos)
        
    Returns:
        list: lista de notas filtradas, no mesmo formato da entrada
    """
    if not notas:
        return []
    
    # Verifica o formato das notas
    primeiro_item = notas[0]
    formato_tupla = isinstance(primeiro_item, tuple)
    
    print(f"Formato de dados detectado: {'Tupla' if formato_tupla else 'Dicionário'}")
    if formato_tupla:
        print(f"Tamanho da tupla: {len(primeiro_item)}")
        print(f"Exemplo do primeiro item: {primeiro_item}")
    
    if formato_tupla and len(primeiro_item) <= 2:
        print("Formato de tupla simples detectado. Aplicando filtragem básica.")
        
        notas_ordenadas = sorted(notas, key=lambda x: x[1] if len(x) > 1 else 0)
        notas_filtradas = []
        
        ultima_nota = None
        ultimo_tempo = 0
        
        for nota in notas_ordenadas:
            if len(nota) < 2:
                continue
                
            pitch = nota[0]
            tempo = nota[1]
            
            if ultima_nota is None or (tempo - ultimo_tempo) >= distancia_minima or pitch == 'rest':
                notas_filtradas.append(nota)
                ultima_nota = pitch
                ultimo_tempo = tempo
            else:
                if pitch == ultima_nota:
                    continue
                else:
                    notas_filtradas.append(nota)
                    ultima_nota = pitch
                    ultimo_tempo = tempo
                    
        print(f"Filtragem básica: {len(notas)} notas originais -> {len(notas_filtradas)} após filtragem")
        return notas_filtradas
    
    print("Formato de dados completo detectado. Aplicando filtragem avançada.")
    
    return notas_filtradas
