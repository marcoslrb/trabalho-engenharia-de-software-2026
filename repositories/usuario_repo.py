"""
repositories/usuario_repo.py
Acesso a dados — tabela `usuarios_internos`.
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from database.connection import db_session

logger = logging.getLogger(__name__)


def criar_usuario(dados: Dict[str, Any]) -> int:
    """Cria um novo usuário interno e retorna seu ID."""
    with db_session() as conn:
        cursor = conn.execute(
            """
            INSERT INTO usuarios_internos
                (username, nome_completo, email, senha_hash, perfil, ativo, data_criacao)
            VALUES (?, ?, ?, ?, ?, 1, ?)
            """,
            (
                dados["username"].strip().lower(),
                dados["nome_completo"].strip(),
                dados["email"].strip().lower(),
                dados["senha_hash"],
                dados["perfil"],
                datetime.now(),
            ),
        )
        return cursor.lastrowid


def buscar_por_username(username: str) -> Optional[Dict]:
    """Busca usuário pelo username (case-insensitive)."""
    with db_session() as conn:
        row = conn.execute(
            "SELECT * FROM usuarios_internos WHERE username = ? AND ativo = 1",
            (username.strip().lower(),),
        ).fetchone()
        return dict(row) if row else None


def buscar_por_id(usuario_id: int) -> Optional[Dict]:
    """Busca usuário pelo ID."""
    with db_session() as conn:
        row = conn.execute(
            "SELECT * FROM usuarios_internos WHERE id = ?", (usuario_id,)
        ).fetchone()
        return dict(row) if row else None


def listar_todos() -> List[Dict]:
    """Lista todos os usuários internos (exceto senha_hash)."""
    with db_session() as conn:
        rows = conn.execute(
            """
            SELECT id, username, nome_completo, email, perfil, ativo,
                   data_criacao, ultimo_login
            FROM usuarios_internos
            ORDER BY nome_completo
            """
        ).fetchall()
        return [dict(r) for r in rows]


def atualizar_ultimo_login(usuario_id: int) -> None:
    """Registra data do último login bem-sucedido."""
    with db_session() as conn:
        conn.execute(
            "UPDATE usuarios_internos SET ultimo_login = ? WHERE id = ?",
            (datetime.now(), usuario_id),
        )


def atualizar_senha(usuario_id: int, senha_hash: str) -> None:
    """Atualiza o hash da senha do usuário."""
    with db_session() as conn:
        conn.execute(
            "UPDATE usuarios_internos SET senha_hash = ? WHERE id = ?",
            (senha_hash, usuario_id),
        )


def ativar_desativar(usuario_id: int, ativo: bool) -> None:
    """Ativa ou desativa um usuário."""
    with db_session() as conn:
        conn.execute(
            "UPDATE usuarios_internos SET ativo = ? WHERE id = ?",
            (1 if ativo else 0, usuario_id),
        )


def username_existe(username: str) -> bool:
    """Verifica se um username já está em uso."""
    with db_session() as conn:
        row = conn.execute(
            "SELECT id FROM usuarios_internos WHERE username = ?",
            (username.strip().lower(),),
        ).fetchone()
        return row is not None


def email_existe(email: str, excluir_id: Optional[int] = None) -> bool:
    """Verifica se um e-mail já está em uso."""
    with db_session() as conn:
        if excluir_id:
            row = conn.execute(
                "SELECT id FROM usuarios_internos WHERE email = ? AND id != ?",
                (email.strip().lower(), excluir_id),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id FROM usuarios_internos WHERE email = ?",
                (email.strip().lower(),),
            ).fetchone()
        return row is not None


def atualizar_totp_secret(usuario_id: int, secret: Optional[str]) -> None:
    """Armazena ou remove o segredo TOTP do usuário (para MFA)."""
    with db_session() as conn:
        conn.execute(
            "UPDATE usuarios_internos SET totp_secret = ? WHERE id = ?",
            (secret, usuario_id),
        )
