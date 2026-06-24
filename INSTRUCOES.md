# ⚠️ ATENÇÃO: Instruções Legadas (Versão 1.0)
> **Este arquivo descreve o MVP original baseado em Streamlit (v1.0).**  
> Para a versão atual (v2.0 - FastAPI + Vite SPA), siga as orientações no [README.md](file:///home/marcoslrb/trabalho-engenharia-de-software-2026/README.md).

---

# 📋 Sistema de Ouvidoria - MVP

MVP funcional de um Sistema de Ouvidoria desenvolvido com Python, Streamlit e SQLite.

## 📋 Características

### Funcionalidades Implementadas

- ✅ **Formulário de Manifestação (Cidadão)**
  - Campo de texto para descrição da manifestação
  - Opção de anonimato
  - Campos opcionais para identificação (nome e email)
  - Geração automática de protocolo único

- ✅ **Dashboard de Gestão (Gestor/Analista)**
  - Listagem de todas as manifestações registradas
  - Estatísticas gerais (total, anônimas, identificadas)
  - Filtro por tipo de manifestação (anônimas/identificadas)
  - Visualização detalhada de cada manifestação

- ✅ **Banco de Dados SQLite**
  - Tabela centralizada de manifestações
  - Armazenamento de protocolo, texto, anonimato e data de registro
  - Persistência de dados entre execuções

## 🔧 Requisitos

- Python 3.8 ou superior
- Streamlit
- pandas (opcional, incluído automaticamente)

## 📦 Instalação

### 1. Instalar dependências

```bash
pip install streamlit pandas
```

### 2. Executar a aplicação

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador padrão em `http://localhost:8501`

## 🎯 Como Usar

### Perfil: Cidadão

1. Selecione "Cidadão" na sidebar
2. Preencha o formulário com sua manifestação
3. Escolha se deseja permanecer anônimo
4. Se não anônimo, opcionalmente forneça seu nome e email
5. Clique em "Registrar Manifestação"
6. **Guarde seu número de protocolo** para referência futura

### Perfil: Gestor/Analista

1. Selecione "Gestor/Analista" na sidebar
2. Visualize estatísticas gerais das manifestações
3. Use filtros para visualizar apenas anônimas ou identificadas
4. Clique em qualquer manifestação para ver detalhes completos

## 💾 Banco de Dados

O arquivo `ouvidoria.db` é criado automaticamente na primeira execução e armazena:

- **Protocolo**: Número único gerado automaticamente (OUT-AAAAMMDDHHMMSS-XXXXXXXX)
- **Texto da Manifestação**: Descrição completa
- **Flag de Anonimato**: Booleano indicando se é anônimo
- **Data de Registro**: Timestamp da submissão
- **Nome e Email (opcional)**: Dados do cidadão se não anônimo

## 🗂️ Estrutura de Arquivos

```
trabalho-engenharia-de-software-2026/
├── app.py                 # Aplicação principal (executável)
├── ouvidoria.db          # Banco de dados SQLite (criado automaticamente)
├── INSTRUCOES.md         # Este arquivo
└── README.md
```

## 🚀 Funcionalidades Adicionais

- **Geração de Protocolo Único**: Cada manifestação recebe um protocolo único e imutável
- **Interface Responsiva**: Design adaptável para diferentes tamanhos de tela
- **Filtros Inteligentes**: Gerencie manifestações por tipo
- **Estatísticas em Tempo Real**: Métricas atualizadas automaticamente
- **Validação de Formulário**: Garante que a manifestação não fique vazia

## 📱 Interface do Usuário

- Layout limpo e intuitivo
- Cores visuais para melhor compreensão (azul para protocolo, verde para sucesso)
- Animações de feedback (confete ao registrar)
- Cards expansíveis para visualização de detalhes

## ⚙️ Configuração Técnica

- **Framework Frontend**: Streamlit
- **Banco de Dados**: SQLite3 (já incluso no Python)
- **Geração de IDs**: UUID + Timestamp
- **Persistência**: Arquivo local `ouvidoria.db`

## 🔐 Segurança

- Proteção de anonimato: Manifestações anônimas não armazenam dados pessoais
- Protocolo único como identificador imutável
- Dados armazenados localmente (não há transmissão externa)

## 📞 Suporte

Para dúvidas sobre o sistema, consulte os campos de ajuda disponíveis na interface clicando no ícone "?" próximo aos campos.

---

**Versão**: 1.0  
**Data**: 2026  
**Status**: MVP Funcional
