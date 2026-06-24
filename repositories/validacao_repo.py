import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from database.connection import db_session

logger = logging.getLogger(__name__)

def listar_todas() -> List[Dict[str, Any]]:
    """Retorna todas as validações registradas."""
    with db_session() as conn:
        rows = conn.execute("SELECT * FROM validacoes ORDER BY createdAt DESC").fetchall()
        return [dict(r) for r in rows]

def inserir(dados: Dict[str, Any]) -> None:
    """Insere um novo registro de validação."""
    with db_session() as conn:
        conn.execute(
            """
            INSERT INTO validacoes
                (id, groupName, reviewer, reviewDate, decision, consistencyNote, completenessNote, rnfNote, createdAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dados["id"],
                dados["groupName"],
                dados["reviewer"],
                dados["reviewDate"],
                dados["decision"],
                dados.get("consistencyNote") or None,
                dados.get("completenessNote") or None,
                dados.get("rnfNote") or None,
                dados.get("createdAt") or datetime.now().isoformat(),
            ),
        )

def deletar(log_id: str) -> bool:
    """Deleta um registro de validação pelo ID."""
    with db_session() as conn:
        cursor = conn.execute("DELETE FROM validacoes WHERE id = ?", (log_id,))
        return cursor.rowcount > 0
