"""
Setup para instalação do pacote NotaLAB
"""

from setuptools import setup, find_packages

# Lê o conteúdo do README.md para usar como descrição longa
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Lê os requisitos do arquivo requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

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
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "notalab=notalab.cli.app:main",
        ],
    },
)