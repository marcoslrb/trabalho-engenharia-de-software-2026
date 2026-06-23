# Pendências e Limitações — Sistema de Ouvidoria v2.0

## Itens com Implementação Parcial ou Não Testáveis em Ambiente Local

### RNF06 — Disponibilidade 24/7
- **Limitação**: Não verificável em ambiente de desenvolvimento local.
- **Como validar em produção**: Deploy em servidor com monitoramento (ex.: UptimeRobot, AWS CloudWatch).
- **Implementado**: Sistema não tem ponto único de falha em nível de código.

### RNF07 — Suporte a 500 usuários simultâneos
- **Limitação**: SQLite não suporta alta concorrência de escritas. WAL mode melhora leituras.
- **Proposta de produção**: Migrar para PostgreSQL (a camada de repositórios facilita essa troca).
- **Como validar**: Teste de carga com Locust ou Apache JMeter.

### RNF13 — Integração com APIs Governamentais
- **Limitação**: Fora do escopo do trabalho.
- **Proposta**: Validação de CPF via API da Receita Federal e integração com e-Ping.

### RNF16 — MFA (Multi-Factor Authentication)
- **Status**: Arquitetura preparada.
- **O que existe**: Campo `totp_secret` na tabela `usuarios_internos`, funções `gerar_totp_secret()`, `verificar_totp()`, `gerar_qrcode_totp()` em `services/auth_service.py`.
- **Para ativar**: Adicionar fluxo de configuração de TOTP no painel do usuário e verificação de código após login.

### RF15/RF16 — Notificações por E-mail
- **Status**: Camada de serviço implementada e funcional.
- **Limitação**: Por padrão, e-mails são logados no console (sem SMTP configurado).
- **Para ativar**: Defina as variáveis de ambiente `EMAIL_ENABLED=true`, `EMAIL_HOST`, `EMAIL_USER`, `EMAIL_PASSWORD`.

### Upload — Validação de MIME Type Real
- **Status**: Validação por extensão implementada.
- **Limitação**: A biblioteca `python-magic` para validação real de MIME type requer instalação de dependências nativas no Windows (`libmagic`).
- **Proposta de produção**: Instalar `python-magic-bin` ou usar serviço de antivírus para scan de uploads.

### RNF18 — Conformidade e-Ping/Acessibilidade
- **Status**: Streamlit tem suporte básico (labels, formulários).
- **Limitação**: Auditoria formal de acessibilidade requer ferramenta especializada (WCAG 2.1).

## Itens Priorizados para Versão Futura

1. **Dashboard de categorias**: Tela de admin para criar/editar/desativar categorias.
2. **Busca por texto livre**: Busca por palavras-chave no texto das manifestações.
3. **Atribuição de responsável**: Selecionar atendente específico para cada manifestação.
4. **Sistema de tags múltiplas**: Relação N:N entre manifestações e categorias.
5. **Paginação no dashboard**: Para bases com muitas manifestações.
6. **Exportação de auditoria**: Relatório das ações administrativas.
