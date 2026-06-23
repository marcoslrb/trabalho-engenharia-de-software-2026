"""
repositories/manifestacao_repo.py
Acesso a dados — tabela `manifestacoes`.
Todas as queries são parametrizadas (prevenção de SQL injection).
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from database.connection import db_session

logger = logging.getLogger(__name__)


def inserir(dados: Dict[str, Any]) -> int:
    """
    Insere uma nova manifestação e retorna seu ID.
    Dados pessoais só são persistidos quando eh_anonimo=False.
    RF11 — Segurança do anonimato garantida aqui.
    """
    eh_anonimo = bool(dados.get("eh_anonimo", False))

    # Proteção explícita: nunca persiste dados pessoais em manifestação anônima
    if eh_anonimo:
        nome = None
        email = None
        cpf = None
        telefone = None
    else:
        nome = dados.get("nome_cidadao") or None
        email = dados.get("email_cidadao") or None
        cpf = dados.get("cpf_cidadao") or None
        telefone = dados.get("telefone_cidadao") or None

    with db_session() as conn:
        cursor = conn.execute(
            """
            INSERT INTO manifestacoes
                (protocolo, texto_manifestacao, eh_anonimo, data_registro,
                 nome_cidadao, email_cidadao, cpf_cidadao, telefone_cidadao,
                 categoria, assunto, setor, status, data_atualizacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dados["protocolo"],
                dados["texto_manifestacao"],
                1 if eh_anonimo else 0,
                datetime.now(),
                nome,
                email,
                cpf,
                telefone,
                dados.get("categoria", "Reclamação"),
                dados.get("assunto") or None,
                dados.get("setor") or None,
                "Recebida",
                datetime.now(),
            ),
        )
        return cursor.lastrowid


def buscar_por_protocolo(protocolo: str) -> Optional[Dict]:
    """Busca manifestação pelo protocolo. Retorna dict ou None."""
    with db_session() as conn:
        row = conn.execute(
            "SELECT * FROM manifestacoes WHERE protocolo = ?",
            (protocolo.strip().upper(),),
        ).fetchone()
        return dict(row) if row else None


def buscar_por_id(manifestacao_id: int) -> Optional[Dict]:
    """Busca manifestação pelo ID interno."""
    with db_session() as conn:
        row = conn.execute(
            "SELECT * FROM manifestacoes WHERE id = ?", (manifestacao_id,)
        ).fetchone()
        return dict(row) if row else None


def listar_todas(
    filtro_status: Optional[str] = None,
    filtro_categoria: Optional[str] = None,
    filtro_anonimo: Optional[bool] = None,
    filtro_setor: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    limit: int = 500,
    offset: int = 0,
) -> List[Dict]:
    """
    Lista manifestações com filtros opcionais.
    RF10 — Painel com filtros por status, tipo, data e assunto.
    """
    query = "SELECT * FROM manifestacoes WHERE 1=1"
    params: List[Any] = []

    if filtro_status:
        query += " AND status = ?"
        params.append(filtro_status)

    if filtro_categoria:
        query += " AND categoria = ?"
        params.append(filtro_categoria)

    if filtro_anonimo is not None:
        query += " AND eh_anonimo = ?"
        params.append(1 if filtro_anonimo else 0)

    if filtro_setor:
        query += " AND setor = ?"
        params.append(filtro_setor)

    if data_inicio:
        query += " AND data_registro >= ?"
        params.append(data_inicio + " 00:00:00")

    if data_fim:
        query += " AND data_registro <= ?"
        params.append(data_fim + " 23:59:59")

    query += " ORDER BY data_registro DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with db_session() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def atualizar_status(
    manifestacao_id: int,
    status_novo: str,
    resposta_gestor: Optional[str] = None,
    parecer_encerramento: Optional[str] = None,
    setor: Optional[str] = None,
    responsavel_id: Optional[int] = None,
) -> bool:
    """
    Atualiza o status da manifestação e campos relacionados.
    RF08, RF13, RF14.
    """
    from config.settings import STATUS_ENCERRAMENTO
    campos = ["status = ?", "data_atualizacao = ?"]
    params: List[Any] = [status_novo, datetime.now()]

    if resposta_gestor is not None:
        campos.append("resposta_gestor = ?")
        params.append(resposta_gestor)

    if parecer_encerramento is not None:
        campos.append("parecer_encerramento = ?")
        params.append(parecer_encerramento)

    if setor is not None:
        campos.append("setor = ?")
        params.append(setor)

    if responsavel_id is not None:
        campos.append("responsavel_id = ?")
        params.append(responsavel_id)

    if status_novo in STATUS_ENCERRAMENTO:
        campos.append("data_encerramento = ?")
        params.append(datetime.now())

    params.append(manifestacao_id)
    query = f"UPDATE manifestacoes SET {', '.join(campos)} WHERE id = ?"

    with db_session() as conn:
        conn.execute(query, params)
        return True


def contar_por_status() -> Dict[str, int]:
    """Retorna contagem de manifestações agrupadas por status."""
    with db_session() as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) as total FROM manifestacoes GROUP BY status"
        ).fetchall()
        return {r["status"]: r["total"] for r in rows}


def contar_por_categoria() -> Dict[str, int]:
    """Retorna contagem agrupada por categoria."""
    with db_session() as conn:
        rows = conn.execute(
            "SELECT categoria, COUNT(*) as total FROM manifestacoes GROUP BY categoria"
        ).fetchall()
        return {r["categoria"]: r["total"] for r in rows}


def estatisticas_gerais() -> Dict[str, Any]:
    """Retorna métricas consolidadas para o dashboard. RF03."""
    with db_session() as conn:
        total = conn.execute("SELECT COUNT(*) FROM manifestacoes").fetchone()[0]
        anonimas = conn.execute(
            "SELECT COUNT(*) FROM manifestacoes WHERE eh_anonimo = 1"
        ).fetchone()[0]
        identificadas = total - anonimas
        concluidas = conn.execute(
            "SELECT COUNT(*) FROM manifestacoes WHERE status = 'Concluída'"
        ).fetchone()[0]
        abertas = total - concluidas

        return {
            "total": total,
            "anonimas": anonimas,
            "identificadas": identificadas,
            "concluidas": concluidas,
            "abertas": abertas,
        }
