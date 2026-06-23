"""
repositories/historico_repo.py
Acesso a dados — tabela `historico_status`.
RF07 — Rastreabilidade de mudanças de status.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from database.connection import db_session


def registrar(
    manifestacao_id: int,
    status_novo: str,
    status_anterior: Optional[str] = None,
    observacao: Optional[str] = None,
    usuario_id: Optional[int] = None,
) -> int:
    """Registra uma mudança de status no histórico. Retorna o ID do registro."""
    with db_session() as conn:
        cursor = conn.execute(
            """
            INSERT INTO historico_status
                (manifestacao_id, status_anterior, status_novo, observacao,
                 usuario_id, data_alteracao)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (manifestacao_id, status_anterior, status_novo, observacao,
             usuario_id, datetime.now()),
        )
        return cursor.lastrowid


def listar_por_manifestacao(manifestacao_id: int) -> List[Dict]:
    """Retorna histórico completo de uma manifestação, em ordem cronológica."""
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT h.*, u.nome_completo as nome_responsavel
            FROM historico_status h
            LEFT JOIN usuarios_internos u ON h.usuario_id = u.id
            WHERE h.manifestacao_id = ?
            ORDER BY h.data_alteracao ASC
            """,
            (manifestacao_id,),
        ).fetchall()
        return [dict(r) for r in rows]
