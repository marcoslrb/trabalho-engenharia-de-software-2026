#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sem Cor

echo -e "${BLUE}=== Sistema de Ouvidoria: Inicialização Automatizada (Poetry) ===${NC}"

# 1. Configurar o Poetry para instalar virtualenvs na raiz (.venv)
echo -e "${BLUE}Configurando ambiente virtual local no Poetry...${NC}"
poetry config virtualenvs.in-project true

# 2. Instalar dependências pelo Poetry
echo -e "${YELLOW}Instalando dependências pelo Poetry...${NC}"
poetry install
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao instalar dependências com o Poetry.${NC}"
    exit 1
fi
echo -e "${GREEN}Dependências instaladas/atualizadas!${NC}"

# 3. Inicializar Banco de Dados (se não existir ouvidoria.db)
if [ ! -f "ouvidoria.db" ]; then
    echo -e "${YELLOW}Banco de dados não encontrado. Criando usuário administrador inicial...${NC}"
    poetry run python create_admin.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}Erro ao inicializar o banco de dados.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Banco de dados inicializado com sucesso!${NC}"
else
    echo -e "${BLUE}Banco de dados existente detectado.${NC}"
fi

# 4. Iniciar o Servidor unificado usando taskipy
echo -e "${GREEN}Iniciando o servidor de Ouvidoria (FastAPI)...${NC}"
poetry run task run
