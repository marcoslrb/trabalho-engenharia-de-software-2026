"""
config/settings.py
Configurações centralizadas do Sistema de Ouvidoria.
Todas as constantes e parâmetros ajustáveis ficam aqui.
"""

import os
from pathlib import Path

# ── Diretório raiz do projeto ──────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── Banco de dados ─────────────────────────────────────────────────────────────
DATABASE_PATH = str(BASE_DIR / "ouvidoria.db")

# ── Uploads ────────────────────────────────────────────────────────────────────
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

MAX_FILES_PER_MANIFESTACAO = 5
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Extensões permitidas para upload
ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".odt", ".txt",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
    ".xls", ".xlsx", ".ods", ".csv",
}

# Extensões perigosas sempre bloqueadas
BLOCKED_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".sh", ".ps1",
    ".js", ".vbs", ".dll", ".msi", ".jar",
    ".py", ".rb", ".php",
}

# ── E-mail (camada de serviço — desativado por padrão) ─────────────────────────
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "ouvidoria@exemplo.gov.br")
EMAIL_FROM_NAME = "Sistema de Ouvidoria"

# ── Autenticação / sessão ──────────────────────────────────────────────────────
SESSION_TIMEOUT_MINUTES = 60
# Rounds de hashing bcrypt (12 é padrão seguro; use 10 em dev para velocidade)
BCRYPT_ROUNDS = 12

# ── Protocolo ──────────────────────────────────────────────────────────────────
PROTOCOL_PREFIX = "OUT"

# ── Perfis de usuário interno ──────────────────────────────────────────────────
PERFIL_ADMIN = "admin"
PERFIL_GESTOR = "gestor"
PERFIL_ATENDENTE = "atendente"

PERFIS_VALIDOS = {PERFIL_ADMIN, PERFIL_GESTOR, PERFIL_ATENDENTE}

PERFIL_LABELS = {
    PERFIL_ADMIN: "Administrador",
    PERFIL_GESTOR: "Gestor",
    PERFIL_ATENDENTE: "Atendente",
}

# ── Status de manifestação ─────────────────────────────────────────────────────
STATUS_RECEBIDA = "Recebida"
STATUS_TRIAGEM = "Em triagem"
STATUS_ENCAMINHADA = "Encaminhada ao setor"
STATUS_EM_ANALISE = "Em análise"
STATUS_AGUARDANDO_RESPOSTA = "Aguardando resposta do cidadão"
STATUS_RESPOSTA_DISPONIVEL = "Resposta disponível"
STATUS_CONCLUIDA = "Concluída"

STATUS_FLOW = [
    STATUS_RECEBIDA,
    STATUS_TRIAGEM,
    STATUS_ENCAMINHADA,
    STATUS_EM_ANALISE,
    STATUS_AGUARDANDO_RESPOSTA,
    STATUS_RESPOSTA_DISPONIVEL,
    STATUS_CONCLUIDA,
]

STATUS_ENCERRAMENTO = {STATUS_CONCLUIDA}

# ── Categorias padrão ─────────────────────────────────────────────────────────
CATEGORIAS_PADRAO = [
    "Denúncia",
    "Reclamação",
    "Solicitação",
    "Sugestão",
    "Elogio",
    "Pedido de informação",
]

# ── Setores padrão ────────────────────────────────────────────────────────────
SETORES_PADRAO = [
    "Atendimento ao cidadão",
    "Limpeza urbana",
    "Saúde",
    "Educação",
    "Mobilidade",
    "Assistência social",
    "Meio ambiente",
    "Infraestrutura",
    "Ouvidoria geral",
]

# ── Validação de texto ────────────────────────────────────────────────────────
MANIFESTACAO_MIN_CHARS = 20
MANIFESTACAO_MAX_CHARS = 5000
ASSUNTO_MAX_CHARS = 120
