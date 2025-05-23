"""
NotaLAB - Aplicação para análise de áudio e transcrição musical

Este arquivo serve como ponto de entrada principal para a aplicação NotaLAB.
Ele coordena a inicialização dos diferentes módulos e inicia a interface do usuário.
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório do projeto ao PYTHONPATH para importações
projeto_dir = Path(__file__).parent
sys.path.insert(0, str(projeto_dir))

# Importa os módulos principais
from src.cli.app import main
from config.config import obter_config_para_estilo


if __name__ == "__main__":
    main()