# Rastreabilidade de Requisitos — Sistema de Ouvidoria v2.0

> Documento de mapeamento entre requisitos do SRS e implementação.

## Requisitos Funcionais

| RF | Título | Status | Módulo | Observação |
|----|--------|--------|--------|-----------|
| RF01 | Cadastro de manifestação | ✅ Implementado | `ui/cidadao/abertura.py`, `services/manifestacao_service.py` | Categoria, assunto, descrição |
| RF02 | Modo anônimo | ✅ Implementado | `repositories/manifestacao_repo.py` | Dados pessoais bloqueados em nível de banco |
| RF03 | Identificação com CPF | ✅ Implementado | `utils/validators.py`, `ui/cidadao/abertura.py` | CPF obrigatório, validação pelo algoritmo oficial |
| RF04 | Upload de anexos | ✅ Implementado | `services/anexo_service.py`, `repositories/anexo_repo.py` | Máx 5 arquivos, 10 MB, extensões validadas |
| RF05 | Protocolo único | ✅ Implementado | `services/protocolo_service.py` | Formato OUT-AAAAMMDDHHMMSS-UUID8 + constraint UNIQUE |
| RF06 | Consulta por protocolo | ✅ Implementado | `ui/cidadao/consulta.py`, `services/manifestacao_service.py` | Sem barreiras extras, dados pessoais mascarados |
| RF07 | Linha do tempo de status | ✅ Implementado | `repositories/historico_repo.py`, `ui/cidadao/consulta.py` | Histórico cronológico com responsável |
| RF08 | Gestor altera status/setor | ✅ Implementado | `ui/admin/detalhe.py`, `services/manifestacao_service.py` | Formulário completo com setor e observação |
| RF09 | Login seguro do gestor | ✅ Implementado | `services/auth_service.py`, `ui/admin/login.py` | bcrypt 12 rounds + timeout de sessão |
| RF10 | Painel com filtros | ✅ Implementado | `ui/admin/dashboard.py` | Filtros: status, tipo, setor, período |
| RF11 | Tags/categorias gerenciáveis | ✅ Implementado | `database/migrations.py` (tabela categorias), `services/manifestacao_service.py` | Categorias na tabela própria, seed das categorias padrão |
| RF12 | Encaminhamento com observação | ✅ Implementado | `ui/admin/detalhe.py` | Seleção de setor + observação interna no atendimento |
| RF13 | Resposta ao cidadão | ✅ Implementado | `ui/admin/detalhe.py`, `ui/cidadao/consulta.py` | Campo resposta_gestor visível na consulta pública |
| RF14 | Encerramento com parecer | ✅ Implementado | `services/manifestacao_service.py`, `ui/admin/detalhe.py` | Parecer obrigatório, validação no service layer |
| RF15 | Notificação por e-mail de status | ✅ Implementado (stub) | `services/email_service.py` | Camada desacoplada; por padrão loga no console. Ativar com EMAIL_ENABLED=true |
| RF16 | Envio de protocolo por e-mail | ✅ Implementado (stub) | `services/email_service.py` | Template HTML completo, mesmo mecanismo do RF15 |
| RF17 | Relatórios gerenciais | ✅ Implementado | `ui/admin/relatorios.py` | Filtros por status, setor, período |
| RF18 | Exportação CSV/XLSX | ✅ Implementado | `ui/admin/relatorios.py` | Download direto via Streamlit |
| RF19 | Gerenciamento de usuários | ✅ Implementado | `ui/admin/admin_usuarios.py`, `repositories/usuario_repo.py` | Perfis: admin, gestor, atendente |

## Requisitos Não Funcionais

| RNF | Título | Status | Módulo/Observação |
|-----|--------|--------|-------------------|
| RNF01 | Usabilidade | ✅ Implementado | Interface Streamlit com feedback visual em todas as ações |
| RNF02 | Responsividade | ⚠️ Parcial | Streamlit é responsivo por padrão; layout wide configurado |
| RNF03 | Proteção do anonimato | ✅ Implementado | `repositories/manifestacao_repo.py` — dados pessoais nunca persistidos em anônimas |
| RNF04 | Isolamento de dados | ✅ Implementado | Separação físicia: área pública vs admin autenticada |
| RNF05 | Tempo de resposta | ⚠️ Parcial | SQLite local é rápido; sem teste de carga formal |
| RNF06 | Disponibilidade 24/7 | ❌ Não testável aqui | Requer deploy em infraestrutura com monitoramento |
| RNF07 | 500 usuários simultâneos | ❌ Não testável aqui | SQLite com WAL suporta leituras concorrentes; produção requer PostgreSQL |
| RNF08 | Escalabilidade | ❌ Não testável aqui | Arquitetura modular facilita migração para PostgreSQL |
| RNF09 | Manutenibilidade | ✅ Implementado | Código modular por camadas (config/database/models/repositories/services/ui) |
| RNF10 | Compatibilidade | ✅ Implementado | Streamlit roda em qualquer navegador moderno |
| RNF11 | Auditoria CRUD | ✅ Implementado | `database/migrations.py` (tabela auditoria), `services/auth_service.py` |
| RNF12 | Backup/recuperação | ❌ Não testável aqui | SQLite é um arquivo único — backup = cópia do `ouvidoria.db` |
| RNF13 | Integração com APIs gov. | ❌ Não implementado | Fora do escopo do MVP/trabalho |
| RNF14 | Documentação | ✅ Implementado | README.md, docs/arquitetura.md, docs/rastreabilidade.md |
| RNF15 | Feedback ao usuário | ✅ Implementado | st.success/error/warning em todas as operações |
| RNF16 | MFA para internos | ⚠️ Arquitetura preparada | Campo `totp_secret` no banco; `services/auth_service.py` tem funções TOTP; não ativado por padrão |
| RNF17 | Telemetria de recursos | ❌ Não testável aqui | Requer monitoramento de infraestrutura |
| RNF18 | Acessibilidade (e-Ping) | ⚠️ Parcial | Streamlit tem suporte básico de acessibilidade |
| RNF19 | Tecnologias open source | ✅ Implementado | Python, Streamlit, SQLite, bcrypt, pyotp — todos open source |
| RNF20 | Performance de banco | ✅ Implementado | WAL mode + índices criados nas migrações |

## Requisitos de Segurança

| Item | Status | Implementação |
|------|--------|--------------|
| Hash de senha (bcrypt) | ✅ | `services/auth_service.py` — 12 rounds |
| Controle de sessão | ✅ | `st.session_state` + timeout 60min |
| Perfis/permissões | ✅ | 3 perfis: admin, gestor, atendente |
| MFA (TOTP) | ⚠️ Arquitetura | `services/auth_service.py` — funções disponíveis, não ativado por padrão |
| Sanitização de entrada | ✅ | `utils/validators.py` + `sanitizar_texto()` |
| Queries parametrizadas | ✅ | Todos os repositórios |
| Proteção do anonimato | ✅ | `repositories/manifestacao_repo.py` — garantia em nível de dados |
| Separação público/interno | ✅ | Áreas distintas com controle de sessão |
| Dados pessoais em telas indevidas | ✅ | CPF mascarado, consulta pública não expõe dados sensíveis |
| Não armazenar CPF/e-mail em anônima | ✅ | Verificação explícita no `inserir()` do repositório |
| Tratamento de erros sem vazar detalhes | ✅ | Mensagens genéricas no login; logs internos para erros técnicos |

## Testes Automatizados

| Critério | Arquivo de Teste | Cobertura |
|----------|-----------------|-----------|
| Geração de protocolo único | `test_protocolo.py` | ✅ 6 testes |
| Validação de CPF | `test_validators.py` | ✅ 10 testes |
| Validação de e-mail | `test_validators.py` | ✅ 7 testes |
| Persistência manifestação anônima | `test_manifestacao.py` | ✅ |
| Bloqueio de dados pessoais em anônima | `test_manifestacao.py` | ✅ |
| Upload — limite de quantidade (5) | `test_anexos.py` | ✅ |
| Upload — limite de tamanho (10MB) | `test_anexos.py` | ✅ |
| Consulta por protocolo | `test_manifestacao.py` | ✅ |
| Autenticação (bcrypt) | `test_auth.py` | ✅ 8 testes |
| Encerramento com parecer obrigatório | `test_manifestacao.py` | ✅ |
