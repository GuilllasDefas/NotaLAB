# Arquivo de inicialização do pacote notalab
# Permite importações simplificadas de todos os módulos
from notalab.audio import (carregar_audio, detectar_acordes, detectar_bpm,
                           detectar_tom)
from notalab.harmonia import extrair_notas_vocal, gerar_harmonias_vocais
from notalab.notacao import montar_harmonia
from notalab.stems import separar_stems

__version__ = '0.1.0'
