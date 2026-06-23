"""
database/connection.py
Gerenciamento da conexão SQLite com configurações de segurança e performance.
"""

import sqlite3
import logging
from contextlib import contextmanager
from config.settings import DATABASE_PATH

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    """
    Retorna uma conexão SQLite configurada com:
    - WAL mode (melhor concorrência)
    - Foreign keys habilitadas
    - Row factory para acesso por nome de coluna
    """
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


@contextmanager
def db_session():
    """
    Context manager para uso seguro da conexão.
    Faz commit automaticamente em caso de sucesso e rollback em caso de erro.

    Uso:
        with db_session() as conn:
            conn.execute(...)
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("Erro na transação do banco de dados: %s", e, exc_info=True)
        raise
    finally:
        conn.close()
