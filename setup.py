"""
Setup para instalação do pacote NotaLAB
"""

import os
import sys
from cx_Freeze import setup, Executable
from setuptools import find_packages

# Adiciona o diretório src ao path para encontrar os módulos durante o build
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Lê o conteúdo do README.md para usar como descrição longa
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Lê os requisitos do arquivo requirements.txt
try:
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = f.read().splitlines()
except UnicodeDecodeError:
    with open("requirements.txt", "r", encoding="utf-16") as f:
        requirements = f.read().splitlines()

# Configurações específicas para Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Evita mostrar console quando executado

# Diretórios e arquivos a serem incluídos
include_files = [
    ("config", "config"),
    ("README.md", "README.md"),
    ("icon.ico", "icon.ico"),
    ("src", "src"),  # Inclui todo o diretório src
]

# Criar pasta data se não existir
if not os.path.exists("data"):
    os.makedirs("data")
include_files.append(("data", "data"))

# Adicione pretrained_models se existir
if os.path.exists("pretrained_models"):
    include_files.append(("pretrained_models", "pretrained_models"))

# Pacotes que cx_Freeze pode não detectar automaticamente
packages = [
    "librosa", 
    "music21", 
    "spleeter",
    "numpy",
    "scipy",
    "matplotlib",
    "tensorflow",
    "sklearn",
]

# Caminho dos módulos internos
package_data = {"": ["*.py"]}

executables = [
    Executable(
        "main.py",  
        base=base,
        target_name="NotaLAB.exe",
        icon="icon.ico",
        shortcut_name="NotaLAB",
        shortcut_dir="DesktopFolder",
    )
]

setup(
    name="notalab",
    version="0.1.0",
    author="Guilherme Defas",
    author_email="guilhermedifreitas@gmail.com",
    description="Aplicação para análise de áudio e transcrição musical",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GuilllasDefas/Multimidia-Tool/tree/main",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data=package_data,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    options={
        "build_exe": {
            "packages": packages,
            "include_files": include_files,
            "include_msvcr": True,
            "build_exe": "dist/NotaLAB",
            "excludes": ["tkinter.test", "unittest"],
            "zip_include_packages": "*",
            "zip_exclude_packages": "",
            "path": sys.path + ["src"]  # Adiciona explicitamente o diretório src ao path
        },
    },
    executables=executables,
)