"""
repositories/anexo_repo.py
Acesso a dados — tabela `anexos`.
RF04 — Metadados dos arquivos anexados.
"""

from datetime import datetime
from typing import Optional, List, Dict
from database.connection import db_session


def inserir(dados: Dict) -> int:
    """Registra metadados de um arquivo anexado. Retorna o ID."""
    with db_session() as conn:
        cursor = conn.execute(
            """
            INSERT INTO anexos
                (manifestacao_id, nome_original, nome_armazenado,
                 mime_type, tamanho_bytes, data_upload)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                dados["manifestacao_id"],
                dados["nome_original"],
                dados["nome_armazenado"],
                dados.get("mime_type"),
                dados.get("tamanho_bytes"),
                datetime.now(),
            ),
        )
        return cursor.lastrowid


def listar_por_manifestacao(manifestacao_id: int) -> List[Dict]:
    """Retorna todos os anexos de uma manifestação."""
    with db_session() as conn:
        rows = conn.execute(
            "SELECT * FROM anexos WHERE manifestacao_id = ? ORDER BY data_upload",
            (manifestacao_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def contar_por_manifestacao(manifestacao_id: int) -> int:
    """Conta quantos anexos uma manifestação já possui."""
    with db_session() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM anexos WHERE manifestacao_id = ?",
            (manifestacao_id,),
        ).fetchone()
        return row[0]
