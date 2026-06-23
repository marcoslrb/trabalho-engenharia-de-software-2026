# Sistema de Ouvidoria — v2.0

> Sistema de Ouvidoria Digital desenvolvido como trabalho de Engenharia de Software (2026).
> Tecnologia: **Python + Streamlit + SQLite**.

---

## 🚀 Início Rápido

### 1. Pré-requisitos
- Python 3.10 ou superior
- pip

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Criar o usuário administrador inicial

```bash
python create_admin.py
```

Isso cria:
- **admin** / `admin123` (perfil: Administrador)
- **atendente** / `atendente123` (perfil: Atendente)

> ⚠️ **Altere as senhas padrão imediatamente após o primeiro login!**

### 4. Executar o sistema

```bash
streamlit run app.py
```

Acesse: `http://localhost:8501`

---

## 📁 Estrutura do Projeto

```
trabalho-engenharia-de-software-2026/
│
├── app.py                  # Ponto de entrada (streamlit run app.py)
├── create_admin.py         # Script de seed do admin inicial
├── requirements.txt        # Dependências Python
├── ouvidoria.db            # Banco SQLite (criado automaticamente)
├── uploads/                # Arquivos anexos (criado automaticamente)
│
├── config/
│   └── settings.py         # Todas as configurações do sistema
│
├── database/
│   ├── connection.py       # Conexão SQLite (WAL mode, foreign keys)
│   └── migrations.py       # Migrações incrementais seguras
│
├── models/
│   └── schemas.py          # Dataclasses das entidades
│
├── repositories/
│   ├── manifestacao_repo.py
│   ├── usuario_repo.py
│   ├── historico_repo.py
│   └── anexo_repo.py
│
├── services/
│   ├── auth_service.py     # bcrypt, sessão, TOTP (arquitetura)
│   ├── manifestacao_service.py
│   ├── email_service.py    # Camada desacoplada (stub/SMTP)
│   ├── anexo_service.py    # Upload e validação
│   └── protocolo_service.py
│
├── utils/
│   ├── validators.py       # CPF, e-mail, texto
│   └── helpers.py          # Formatação e utilitários
│
├── ui/
│   ├── cidadao/
│   │   ├── home.py         # Tela inicial
│   │   ├── abertura.py     # Formulário de manifestação
│   │   └── consulta.py     # Consulta por protocolo
│   └── admin/
│       ├── login.py        # Autenticação
│       ├── dashboard.py    # Painel + métricas
│       ├── detalhe.py      # Atendimento e histórico
│       ├── relatorios.py   # Exportação CSV/XLSX
│       └── admin_usuarios.py  # Gestão de usuários
│
├── tests/
│   ├── test_validators.py
│   ├── test_protocolo.py
│   ├── test_manifestacao.py
│   ├── test_auth.py
│   └── test_anexos.py
│
├── docs/
│   ├── arquitetura.md
│   ├── rastreabilidade.md
│   └── pendencias.md
│
└── src/                    # Protótipo JS original (preservado)
    ├── main.js
    └── styles.css
```

---

## 🔐 Perfis de Usuário

| Perfil | Acesso |
|--------|--------|
| `admin` | Tudo + gestão de usuários |
| `gestor` | Dashboard, detalhes, relatórios |
| `atendente` | Dashboard e atendimento |

---

## ⚙️ Configurações via Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `EMAIL_ENABLED` | `false` | Ativa envio real de e-mail |
| `EMAIL_HOST` | `smtp.gmail.com` | Servidor SMTP |
| `EMAIL_PORT` | `587` | Porta SMTP |
| `EMAIL_USER` | _(vazio)_ | Usuário SMTP |
| `EMAIL_PASSWORD` | _(vazio)_ | Senha SMTP |

Com `EMAIL_ENABLED=false` (padrão), e-mails são apenas logados no console.

---

## 🧪 Executar Testes

```bash
pip install pytest
pytest tests/ -v
```

---

## 📊 Funcionalidades

### Área do Cidadão
- ✅ Tela inicial com estatísticas públicas
- ✅ Formulário de abertura (categoria, assunto, descrição)
- ✅ Modo anônimo (sem dados pessoais)
- ✅ Identificação com CPF obrigatório + e-mail + nome
- ✅ Upload de até 5 anexos (máx. 10 MB cada)
- ✅ Geração de protocolo único (OUT-AAAAMMDDHHMMSS-XXXXXXXX)
- ✅ Consulta por protocolo sem barreiras extras
- ✅ Linha do tempo de status

### Área Administrativa
- ✅ Login seguro (bcrypt)
- ✅ Controle de sessão com timeout
- ✅ Dashboard com métricas e filtros
- ✅ Atendimento e mudança de status
- ✅ Encerramento com parecer obrigatório
- ✅ Trilha de auditoria
- ✅ Relatórios exportáveis (CSV e XLSX)
- ✅ Gestão de usuários internos (perfil admin)

---

## 🔒 Segurança

- Senhas armazenadas com **bcrypt** (12 rounds)
- Queries 100% **parametrizadas** (sem SQL injection)
- **Anonimato garantido** em nível de banco (dados pessoais nunca inseridos em anônimas)
- Sessão com **timeout automático** (60 minutos)
- Extensões perigosas **bloqueadas no upload** (.exe, .bat, .js, etc.)
- CPF **mascarado** na interface administrativa
- Arquitetura preparada para **MFA/TOTP** (campo `totp_secret` no banco)

---

## 📌 Versão e Autores

- **Versão**: 2.0
- **Data**: 2026
- **Disciplina**: Engenharia de Software