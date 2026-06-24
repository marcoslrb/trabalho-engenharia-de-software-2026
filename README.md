# 🏛️ Sistema de Ouvidoria Pública — v2.0

> Sistema de Ouvidoria Digital desenvolvido como trabalho de Engenharia de Software (2026).
> Stack: **Python (FastAPI) + SQLite + Frontend SPA (Vite + Vanilla JS/CSS)**.

---

## 🛠️ Arquitetura do Sistema

O sistema segue uma arquitetura baseada em **API HTTP (REST) e Cliente SPA Decoplado**:

1. **Backend (Python & FastAPI)**:
   - Gerencia a lógica de negócios, segurança de anonimato e acesso ao banco SQLite.
   - Organizado em camadas bem definidas:
     - `database/`: Conexão SQLite (WAL mode, Foreign Keys) e migrations seguras.
     - `repositories/`: Ponto único de consultas SQL parametrizadas (proteção contra SQL Injection).
     - `services/`: Regras de negócio puras (validação, e-mail stubs, uploads, hashing de senhas).
     - `models/`: Schemas de dados e dataclasses.
     - `utils/`: Validadores (CPF, e-mail) e ajudantes auxiliares.
   - O código Streamlit original do protótipo permanece preservado na pasta `ui/` para fins de referência histórica de Engenharia de Requisitos.
2. **Frontend (Vite & Vanilla JS)**:
   - Uma aplicação de página única (SPA) moderna baseada em Vanilla JS (`src/main.js`) e Vanilla CSS (`src/styles.css`), construída e empacotada com o **Vite**.
   - Comunica-se com o backend FastAPI através de rotas de API `/api/*` sob proxy local configurado em `vite.config.js`.

---

## 🚀 Primeira Execução (Setup Inicial)

Siga estes passos para configurar e inicializar o ambiente de desenvolvimento pela primeira vez.

### 1. Pré-requisitos
* **Python 3.10 ou superior**
* **Poetry** (gerenciador de dependências e ambiente Python)
* **Node.js e npm** (para build e gerenciamento do frontend)

### 2. Instalar Dependências do Backend (Poetry)
Configure o Poetry para criar o ambiente virtual dentro do projeto e instale os pacotes:
```bash
poetry config virtualenvs.in-project true
poetry install
```

### 3. Instalar Dependências do Frontend (npm)
Instale as dependências necessárias para a build do Vite:
```bash
npm install
```

### 4. Criar Banco de Dados e Usuários Administrativos
Execute o script de seed para rodar as migrações automáticas do banco de dados SQLite e criar os usuários iniciais da ouvidoria:
```bash
poetry run python create_admin.py
```
Esse comando gera o arquivo de banco local `ouvidoria.db` e cria duas contas padrão:
* **Administrador**: username `admin` / senha `admin123`
* **Atendente**: username `atendente` / senha `atendente123`

---

## 💻 Modos de Execução

Você pode rodar o projeto de duas formas diferentes, dependendo se deseja realizar alterações de código ou apenas demonstrar o sistema funcional.

### 🌟 Opção A: Execução Integrada (Modo de Produção / Homologação)
Nesse modo, o backend FastAPI atua como servidor unificado, servindo tanto as APIs quanto os arquivos estáticos do frontend em uma única porta.

1. **Gere a Build do Frontend**:
   ```bash
   npm run build
   ```
   *Isso compilará o frontend para a pasta `dist/`.*

2. **Inicie o Servidor**:
   Você pode usar o script automatizado de inicialização rápida:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   Ou rodar diretamente via taskipy/Poetry:
   ```bash
   poetry run task run
   ```
3. **Acesso**:
   Acesse a aplicação unificada no navegador em: **`http://localhost:8501`**

---

### 🧪 Opção B: Modo de Desenvolvimento (Recomendado para Codificação)
Neste modo, o frontend possui *Hot Reloading* (recarregamento instantâneo no navegador ao alterar códigos JS/CSS) e redireciona requisições de API de forma transparente para o backend FastAPI.

1. **Iniciar o Servidor de API (Backend)**:
   ```bash
   poetry run task run
   ```
   *Inicia a API FastAPI na porta `8501`.*

2. **Iniciar o Servidor de Desenvolvimento (Frontend)**:
   Em outra aba do terminal, execute:
   ```bash
   npm run dev
   ```
   *Inicia o servidor de desenvolvimento do Vite.*

3. **Acesso**:
   Abra a URL de desenvolvimento fornecida pelo Vite, normalmente: **`http://localhost:5173`**

---

## 🧪 Executar Testes Automatizados

Os testes automatizados que cobrem validadores, regras de anexos, geração de protocolo e regras de segurança (bcrypt) residem no diretório `tests/`.

Para rodar a suíte inteira via pytest, execute:
```bash
poetry run pytest tests/ -v
```

---

## ⚙️ Variáveis de Ambiente e Configurações

O arquivo `config/settings.py` centraliza todos os parâmetros customizáveis. Para fins de testes, as notificações por e-mail são apenas logadas no console por padrão. Caso queira habilitar envio real (SMTP), defina as variáveis de ambiente equivalentes:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `EMAIL_ENABLED` | `false` | Se `true`, ativa envio real de e-mails via SMTP. |
| `EMAIL_HOST` | `smtp.gmail.com` | Host do servidor de e-mail. |
| `EMAIL_PORT` | `587` | Porta SMTP de envio. |
| `EMAIL_USER` | _(vazio)_ | Usuário do e-mail de autenticação SMTP. |
| `EMAIL_PASSWORD` | _(vazio)_ | Senha de aplicativo do provedor de e-mail. |

---

## 📊 Funcionalidades Implementadas

### Área do Cidadão (Pública)
* ✅ Tela inicial com estatísticas dinâmicas coletadas da base de dados.
* ✅ Formulário de abertura de manifestação (categoria, assunto, descrição).
* ✅ Modo anônimo garantido em nível de banco (dados sensíveis não persistidos).
* ✅ Validação segura de CPF por algoritmo oficial.
* ✅ Upload de múltiplos anexos (máx. 5 arquivos e limite de 10 MB cada), bloqueando extensões executáveis perigosas.
* ✅ Geração de protocolo único (formato `OUT-AAAAMMDDHHMMSS-XXXXXXXX`) e credencial de acesso exclusiva.
* ✅ Consulta pública de andamento de manifestações por protocolo de forma simplificada.
* ✅ Linha do tempo de status para acompanhamento das fases.

### Área Administrativa (Interna)
* ✅ Autenticação por credenciais com senhas criptografadas por **bcrypt (12 rounds)**.
* ✅ Painel administrativo de triagem e visualização de manifestações detalhadas.
* ✅ Moderação e alteração de status/setor e registro de resposta oficial do gestor ao cidadão.
* ✅ Histórico interno de auditoria de alterações.
* ✅ Exportação de dados operacionais nos formatos CSV e XLSX (Planilha Excel).
* ✅ Gestão de usuários internos (perfis: `admin`, `gestor` e `atendente`).

---

## 🔒 Práticas de Segurança Adotadas

* **Garantia de Anonimato**: Manifestações abertas no formato anônimo omitem dados pessoais fisicamente da tabela SQLite.
* **Prevenção de Injection**: Todas as consultas SQL nos repositórios usam exclusivamente parâmetros tipados (`?`).
* **Proteção de Senha**: Senhas no banco de dados utilizam bcrypt com fator de custo adaptativo para blindagem offline.
* **Prevenção de Timing Attacks**: Login administrativo adota tempo constante de resposta para contas inexistentes.
* **Tratamento Seguro de Uploads**: Extensões perigosas como `.exe`, `.bat` e `.js` são bloqueadas diretamente na validação de arquivo do backend.
* **Arquitetura Pronta para MFA**: Métodos prontos e configurados em banco de dados (`totp_secret`) no `services/auth_service.py` para futura implementação de TOTP (QR Code/Authenticator).

---

## 📌 Versão e Autores

* **Versão**: 2.0
* **Data**: 2026
* **Disciplina**: Engenharia de Software