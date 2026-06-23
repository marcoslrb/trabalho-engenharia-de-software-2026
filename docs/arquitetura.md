# Arquitetura do Sistema de Ouvidoria v2.0

## Visão Geral

O sistema segue uma arquitetura em camadas clássica, adaptada para Streamlit:

```
┌─────────────────────────────────────────────┐
│                   app.py                     │  ← Ponto de entrada + roteamento
└─────────────────────┬───────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │           ui/             │  ← Camada de apresentação (Streamlit)
        │  cidadao/    admin/       │
        └─────────────┬─────────────┘
                      │
        ┌─────────────┴─────────────┐
        │         services/         │  ← Regras de negócio
        │  manifestacao  auth       │
        │  email  anexo  protocolo  │
        └─────────────┬─────────────┘
                      │
        ┌─────────────┴─────────────┐
        │       repositories/       │  ← Acesso a dados (queries SQL)
        │  manifestacao  usuario    │
        │  historico     anexo      │
        └─────────────┬─────────────┘
                      │
        ┌─────────────┴─────────────┐
        │        database/          │  ← Conexão e migrações
        │  connection  migrations   │
        └─────────────┬─────────────┘
                      │
                  ouvidoria.db      ← SQLite (arquivo local)
```

## Camadas e Responsabilidades

### `config/settings.py`
Único ponto de configuração do sistema. Constantes, caminhos, limites e parâmetros de segurança.

### `database/`
- **connection.py**: Gerencia conexão SQLite com WAL mode e foreign keys habilitadas.
- **migrations.py**: Migrações incrementais e idempotentes. Nunca destroem dados existentes.

### `models/schemas.py`
Dataclasses Python tipadas para transporte de dados entre camadas.

### `repositories/`
**Único ponto de acesso ao banco de dados.** Todas as queries são parametrizadas.
Nunca contém lógica de negócio.

### `services/`
Regras de negócio puras. Orquestra validação → repositórios → e-mail → auditoria.
Não conhece Streamlit.

### `ui/`
Apenas apresentação Streamlit. Chama services, nunca repositórios diretamente.
Dividida em `cidadao/` (área pública) e `admin/` (área autenticada).

### `utils/`
Funções puras e reutilizáveis. Sem efeitos colaterais.

## Banco de Dados

### Tabelas

| Tabela | Finalidade |
|--------|-----------|
| `manifestacoes` | Registro principal de manifestações |
| `historico_status` | Trilha de auditoria de mudanças de status |
| `anexos` | Metadados dos arquivos enviados |
| `usuarios_internos` | Atendentes, gestores e administradores |
| `categorias` | Tags/categorias gerenciáveis |
| `auditoria` | Log de ações administrativas |

### Estratégia de Migração
As migrações usam `CREATE TABLE IF NOT EXISTS` e `ALTER TABLE ADD COLUMN` (com verificação prévia de existência).
O banco original é preservado — novas colunas recebem valor `NULL` em registros antigos.

## Fluxo de Dados — Manifestação Anônima

```
Cidadão → formulário → abertura.py
  → manifestacao_service.validar_dados()
  → protocolo_service.gerar_protocolo()
  → manifestacao_repo.inserir()
     ↓ eh_anonimo=True → nome/email/cpf = NULL (GARANTIA DE BANCO)
  → historico_repo.registrar("Recebida")
  → exibe protocolo ao cidadão
```

## Fluxo de Autenticação

```
Admin → login.py
  → auth_service.tentar_login()
     → usuario_repo.buscar_por_username()
     → bcrypt.checkpw(senha, hash)
     → registrar auditoria (sucesso ou falha)
  → auth_service.iniciar_sessao() → st.session_state
  → roteamento para dashboard
```

## Decisões de Design

1. **SQLite com WAL mode**: permite leituras concorrentes sem bloquear escritas.
2. **bcrypt 12 rounds**: balanço entre segurança e performance em ambiente local.
3. **Email como stub**: desacoplado via `email_service.py` — basta configurar variáveis de ambiente.
4. **CPF mascarado**: `mascarar_cpf()` exibe apenas primeiros 3 e últimos 2 dígitos.
5. **Protocolo imutável**: gerado uma vez, constraint UNIQUE no banco impede duplicatas.
6. **TOTP preparado**: campo `totp_secret` e funções em `auth_service.py` prontos para ativação.
