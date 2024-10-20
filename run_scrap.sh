#!/bin/bash

# Ativar o ambiente virtual
source /home/ubuntu/ControlGov/ControGov/bin/activate

# Navegar para o diretório do projeto
cd /home/ubuntu/ControlGov/

# Executar o script Python usando o Python do ambiente virtual
/home/ubuntu/ControlGov/ControGov/bin/python3 scrap_save_DB.py
