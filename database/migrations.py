"""
database/migrations.py
Migração incremental e segura do schema SQLite.
Preserva dados existentes e adiciona colunas/tabelas novas conforme necessário.
"""

import logging
from database.connection import db_session

logger = logging.getLogger(__name__)


def _column_exists(conn, table: str, column: str) -> bool:
    """Verifica se uma coluna existe em uma tabela."""
    cursor = conn.execute(f"PRAGMA table_info({table})")
    cols = [row["name"] for row in cursor.fetchall()]
    return column in cols


def _table_exists(conn, table: str) -> bool:
    """Verifica se uma tabela existe no banco."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    )
    return cursor.fetchone() is not None


def _safe_add_column(conn, table: str, column: str, definition: str) -> None:
    """Adiciona coluna somente se ela não existir ainda."""
    if not _column_exists(conn, table, column):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        logger.info("Coluna '%s.%s' adicionada.", table, column)


def run_migrations() -> None:
    """
    Executa todas as migrações em ordem.
    Idempotente — pode ser chamado múltiplas vezes sem efeito colateral.
    """
    with db_session() as conn:
        _m001_create_manifestacoes(conn)
        _m002_extend_manifestacoes(conn)
        _m003_create_usuarios_internos(conn)
        _m004_create_historico_status(conn)
        _m005_create_anexos(conn)
        _m006_create_categorias(conn)
        _m007_create_auditoria(conn)
        _m008_seed_categorias(conn)
        _m009_create_indexes(conn)

    logger.info("Todas as migrações concluídas com sucesso.")


# ── Migração 001 — Tabela base de manifestações (compatível com MVP original) ──

def _m001_create_manifestacoes(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS manifestacoes (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            protocolo            TEXT UNIQUE NOT NULL,
            texto_manifestacao   TEXT NOT NULL,
            eh_anonimo           INTEGER NOT NULL DEFAULT 0,
            data_registro        TIMESTAMP NOT NULL,
            nome_cidadao         TEXT,
            email_cidadao        TEXT
        )
    """)


# ── Migração 002 — Extensão da tabela de manifestações ─────────────────────────

def _m002_extend_manifestacoes(conn) -> None:
    colunas = [
        ("cpf_cidadao",            "TEXT"),
        ("telefone_cidadao",       "TEXT"),
        ("categoria",              "TEXT DEFAULT 'Reclamação'"),
        ("assunto",                "TEXT"),
        ("setor",                  "TEXT"),
        ("status",                 "TEXT DEFAULT 'Recebida'"),
        ("resposta_gestor",        "TEXT"),
        ("parecer_encerramento",   "TEXT"),
        ("responsavel_id",         "INTEGER"),
        ("data_atualizacao",       "TIMESTAMP"),
        ("data_encerramento",      "TIMESTAMP"),
    ]
    for column, definition in colunas:
        _safe_add_column(conn, "manifestacoes", column, definition)


# ── Migração 003 — Usuários internos ───────────────────────────────────────────

def _m003_create_usuarios_internos(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_internos (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT UNIQUE NOT NULL,
            nome_completo   TEXT NOT NULL,
            email           TEXT UNIQUE NOT NULL,
            senha_hash      TEXT NOT NULL,
            perfil          TEXT NOT NULL DEFAULT 'atendente',
            ativo           INTEGER DEFAULT 1,
            data_criacao    TIMESTAMP NOT NULL,
            ultimo_login    TIMESTAMP,
            totp_secret     TEXT
        )
    """)


# ── Migração 004 — Histórico de status ─────────────────────────────────────────

def _m004_create_historico_status(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS historico_status (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            manifestacao_id     INTEGER NOT NULL,
            status_anterior     TEXT,
            status_novo         TEXT NOT NULL,
            observacao          TEXT,
            usuario_id          INTEGER,
            data_alteracao      TIMESTAMP NOT NULL,
            FOREIGN KEY (manifestacao_id) REFERENCES manifestacoes(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios_internos(id)
        )
    """)


# ── Migração 005 — Anexos ───────────────────────────────────────────────────────

def _m005_create_anexos(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS anexos (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            manifestacao_id     INTEGER NOT NULL,
            nome_original       TEXT NOT NULL,
            nome_armazenado     TEXT NOT NULL,
            mime_type           TEXT,
            tamanho_bytes       INTEGER,
            data_upload         TIMESTAMP NOT NULL,
            FOREIGN KEY (manifestacao_id) REFERENCES manifestacoes(id)
        )
    """)


# ── Migração 006 — Categorias/tags ─────────────────────────────────────────────

def _m006_create_categorias(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            nome    TEXT UNIQUE NOT NULL,
            ativo   INTEGER DEFAULT 1
        )
    """)


# ── Migração 007 — Auditoria ────────────────────────────────────────────────────

def _m007_create_auditoria(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS auditoria (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id      INTEGER,
            acao            TEXT NOT NULL,
            entidade        TEXT,
            entidade_id     INTEGER,
            detalhes        TEXT,
            data_acao       TIMESTAMP NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios_internos(id)
        )
    """)


# ── Migração 008 — Seed de categorias padrão ───────────────────────────────────

def _m008_seed_categorias(conn) -> None:
    from config.settings import CATEGORIAS_PADRAO
    for nome in CATEGORIAS_PADRAO:
        conn.execute(
            "INSERT OR IGNORE INTO categorias (nome, ativo) VALUES (?, 1)", (nome,)
        )


# ── Migração 009 — Índices ──────────────────────────────────────────────────────

def _m009_create_indexes(conn) -> None:
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_manifestacoes_protocolo ON manifestacoes(protocolo)",
        "CREATE INDEX IF NOT EXISTS idx_manifestacoes_status ON manifestacoes(status)",
        "CREATE INDEX IF NOT EXISTS idx_manifestacoes_data ON manifestacoes(data_registro)",
        "CREATE INDEX IF NOT EXISTS idx_historico_manifestacao ON historico_status(manifestacao_id)",
        "CREATE INDEX IF NOT EXISTS idx_anexos_manifestacao ON anexos(manifestacao_id)",
        "CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria(usuario_id)",
    ]
    for stmt in indexes:
        conn.execute(stmt)
