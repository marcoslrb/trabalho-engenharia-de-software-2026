# Arquitetura do Sistema de Ouvidoria v2.0

## Visão Geral

O sistema segue uma arquitetura baseada em **API HTTP (REST) com backend em camadas** e **Frontend SPA (Single Page Application)** desacoplado:

```
┌─────────────────────────────────────────────┐
│    Vite Frontend SPA (index.html/main.js)   │  ← Apresentação (Vanilla JS / CSS)
└─────────────────────┬───────────────────────┘
                      │ (Requisições HTTP /api/*)
┌─────────────────────▼───────────────────────┐
│                   app.py                     │  ← Ponto de entrada + Roteamento (FastAPI)
└─────────────────────┬───────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │         services/         │  ← Regras de negócio puras (sem acoplamento de UI)
        │  manifestacao  auth       │
        │  email  anexo  protocolo  │
        └─────────────┬─────────────┘
                      │
        ┌─────────────┴─────────────┐
        │       repositories/       │  ← Acesso a dados (queries SQL parametrizadas)
        │  manifestacao  usuario    │
        │  historico     anexo      │
        └─────────────┬─────────────┘
                      │
        ┌─────────────┴─────────────┐
        │        database/          │  ← Conexão e migrações incrementais
        │  connection  migrations   │
        └─────────────┬─────────────┘
                      │
                  ouvidoria.db      ← SQLite (arquivo local em WAL mode)
```

---

## Camadas e Responsabilidades

### `index.html` & `src/` (Frontend SPA)
- **`index.html`**: Ponto de entrada do frontend.
- **`src/main.js`**: Contém todo o fluxo lógico da SPA (roteamento por hash `#/...`, chamadas HTTP para o backend via `fetch`, manipulação direta do DOM, estados locais e as telas da Área do Cidadão e Área Administrativa).
- **`src/styles.css`**: Design system visual com variáveis CSS, layout responsivo e transições suaves.

### `app.py` (API Gateway / Router)
Porta de entrada do backend utilizando **FastAPI**. Define endpoints HTTP, valida payloads com Pydantic, dispara as rotas de negócio (`services`) e serve os arquivos estáticos do frontend empacotados na pasta `dist/` se presentes.

### `config/settings.py`
Único ponto de configuração do sistema. Guarda constantes, caminhos de diretórios, limites de upload, constantes de status e parâmetros de segurança (como rounds do bcrypt).

### `database/`
- **connection.py**: Gerencia conexão SQLite configurando WAL mode, chaves estrangeiras (`foreign_keys=ON`) e retorno em dicionários/linhas mapeadas.
- **migrations.py**: Migrações incrementais e idempotentes executadas na inicialização da API. Nunca destroem dados existentes.

### `models/schemas.py`
Dataclasses Python tipadas para transporte de dados (DTO) estruturados entre camadas do backend.

### `repositories/`
**Único ponto de acesso ao banco de dados.** Todas as queries SQL são 100% parametrizadas. Nunca contém regras de negócio ou de validação complexa.

### `services/`
Contém as regras de negócio puras do domínio do sistema. Orquestra o fluxo de validação → inserção no repositório → disparos de e-mail → registro de trilhas de auditoria. É completamente independente da camada de apresentação (não conhece HTML ou HTTP).

### `utils/`
Funções puras e reutilizáveis (como validação algorítmica de CPF ou validação de e-mails), sem efeitos colaterais.

### `ui/` (Legado Streamlit)
Diretório contendo o protótipo anterior baseado em Streamlit (`abertura.py`, `consulta.py`, `dashboard.py`). Mantido de forma isolada exclusivamente para rastreabilidade de requisitos funcionais originais.

---

## Banco de Dados

### Tabelas

| Tabela | Finalidade |
|--------|-----------|
| `manifestacoes` | Registro principal de manifestações de ouvidoria |
| `historico_status` | Trilha de auditoria cronológica das mudanças de status |
| `anexos` | Metadados dos arquivos enviados em anexo |
| `usuarios_internos` | Credenciais e perfis de atendentes, gestores e admins |
| `categorias` | Categorias padrão de manifestação |
| `auditoria` | Registro de ações operacionais e eventos de segurança |
| `validacoes` | Log de validações de requisitos |

### Estratégia de Migração
As migrações são executadas de forma automática ao iniciar o backend. Utilizam clauses `CREATE TABLE IF NOT EXISTS` e validações dinâmicas para adicionar colunas de forma segura sem perda de registros preexistentes.

---

## Fluxos de Informações principais

### Fluxo de Dados — Registro de Manifestação

```
Cidadão → Preenche formulário no site → Clique em Registrar
  → SPA (src/main.js): Envia POST para /api/manifestacoes
  → app.py (FastAPI): Recebe payload e encaminha para service
  → manifestacao_service.registrar_manifestacao()
     → valida limites e arquivos de anexo
     → protocolo_service.gerar_protocolo()
     → manifestacao_repo.inserir()
        ↓ Caso eh_anonimo=True: nome/email/telefone salvos como NULL (GARANTIA DE BANCO)
     → registra histórico de alteração
  → Retorna resposta JSON contendo o protocolo gerado
```

### Fluxo de Autenticação

```
Atendente → Insere username/senha → Clique em Entrar
  → SPA (src/main.js): Envia POST para /api/auth/login
  → app.py (FastAPI): Recebe credenciais
  → auth_service.tentar_login()
     → usuario_repo.buscar_por_username()
     → bcrypt.checkpw(senha, hash)
     → registra sucesso/falha na auditoria
  → Retorna dados do usuário e perfil de acesso
  → SPA (src/main.js): Salva sessão no localStorage e redireciona ao painel interno
```

---

## Decisões de Design

1. **SQLite com WAL mode**: Permite operações simultâneas de leitura sem travar o arquivo de banco durante escritas.
2. **bcrypt 12 rounds**: Padrão seguro recomendado pela indústria para hashing de senhas.
3. **Decoplamento do Frontend**: O frontend é compilado de forma autônoma para produção em arquivos estáticos (HTML/JS/CSS), permitindo facilidade na transição de infraestrutura ou migração de frameworks no futuro.
4. **Mascaramento de Segurança**: A rota de consulta pública de manifestações (`/api/manifestacoes/{protocolo}`) mascara automaticamente CPF, e-mail e texto do cidadão, mantendo a integridade da privacidade dos dados pessoais expostos publicamente.
