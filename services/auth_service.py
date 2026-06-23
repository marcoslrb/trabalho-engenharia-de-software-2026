"""
services/auth_service.py
Autenticação segura para a área administrativa.
RF09 — Login seguro; RNF16 — Arquitetura preparada para MFA (TOTP).
"""

import bcrypt
import pyotp
import qrcode
import io
import logging
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict
from repositories import usuario_repo
from repositories.manifestacao_repo import inserir as inserir_auditoria_placeholder
from database.connection import db_session
from config.settings import BCRYPT_ROUNDS, SESSION_TIMEOUT_MINUTES

logger = logging.getLogger(__name__)


# ── Hash de senha ──────────────────────────────────────────────────────────────

def hash_senha(senha: str) -> str:
    """Gera hash bcrypt seguro da senha."""
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt(BCRYPT_ROUNDS)).decode("utf-8")


def verificar_senha(senha: str, hash_str: str) -> bool:
    """Verifica senha contra hash bcrypt armazenado."""
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), hash_str.encode("utf-8"))
    except Exception:
        return False


# ── Login / Sessão ─────────────────────────────────────────────────────────────

def tentar_login(username: str, senha: str) -> tuple[bool, str, Optional[Dict]]:
    """
    Tenta autenticar um usuário interno.
    Retorna (sucesso, mensagem, dados_usuario).
    Nunca revela se o problema é username ou senha (prevenção de enumeração).
    """
    if not username or not senha:
        return False, "Usuário e senha são obrigatórios.", None

    usuario = usuario_repo.buscar_por_username(username)

    if not usuario:
        # Tempo constante para evitar timing attack
        bcrypt.checkpw(b"dummy", bcrypt.hashpw(b"dummy", bcrypt.gensalt(4)))
        return False, "Usuário ou senha inválidos.", None

    if not verificar_senha(senha, usuario["senha_hash"]):
        _registrar_auditoria(usuario["id"], "LOGIN_FALHOU", "usuarios_internos", usuario["id"])
        return False, "Usuário ou senha inválidos.", None

    usuario_repo.atualizar_ultimo_login(usuario["id"])
    _registrar_auditoria(usuario["id"], "LOGIN_OK", "usuarios_internos", usuario["id"])
    return True, "Login realizado com sucesso.", dict(usuario)


def iniciar_sessao(usuario: Dict) -> None:
    """Salva dados do usuário autenticado na sessão Streamlit."""
    st.session_state["usuario_logado"] = {
        "id": usuario["id"],
        "username": usuario["username"],
        "nome_completo": usuario["nome_completo"],
        "email": usuario["email"],
        "perfil": usuario["perfil"],
        "login_em": datetime.now().isoformat(),
    }


def encerrar_sessao() -> None:
    """Remove todos os dados de sessão administrativa."""
    keys_to_remove = [k for k in st.session_state if k.startswith("usuario_") or k == "pagina_admin"]
    for k in keys_to_remove:
        del st.session_state[k]


def usuario_logado() -> Optional[Dict]:
    """
    Retorna os dados do usuário logado ou None se a sessão expirou/não existe.
    Verifica timeout de sessão automaticamente.
    """
    user = st.session_state.get("usuario_logado")
    if not user:
        return None

    # Verificação de timeout
    login_em = datetime.fromisoformat(user["login_em"])
    if datetime.now() - login_em > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        encerrar_sessao()
        return None

    return user


def requer_perfil(*perfis: str):
    """
    Decorator/helper para verificar se o usuário tem o perfil necessário.
    Uso: requer_perfil('gestor', 'admin')
    """
    user = usuario_logado()
    if not user:
        return False
    return user["perfil"] in perfis


# ── TOTP / MFA ─────────────────────────────────────────────────────────────────

def gerar_totp_secret() -> str:
    """Gera um novo segredo TOTP aleatório."""
    return pyotp.random_base32()


def gerar_totp_uri(secret: str, username: str) -> str:
    """Gera URI para configuração em app autenticador (Google Authenticator, etc.)."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name="Sistema de Ouvidoria")


def gerar_qrcode_totp(uri: str) -> bytes:
    """Gera imagem PNG do QR Code para configuração do TOTP."""
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def verificar_totp(secret: str, codigo: str) -> bool:
    """Verifica um código TOTP. Aceita janela de ±1 intervalo (30s)."""
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(codigo.strip(), valid_window=1)
    except Exception:
        return False


# ── Auditoria ──────────────────────────────────────────────────────────────────

def _registrar_auditoria(
    usuario_id: Optional[int],
    acao: str,
    entidade: Optional[str] = None,
    entidade_id: Optional[int] = None,
    detalhes: Optional[str] = None,
) -> None:
    """Registra ação administrativa na tabela de auditoria."""
    try:
        with db_session() as conn:
            conn.execute(
                """
                INSERT INTO auditoria
                    (usuario_id, acao, entidade, entidade_id, detalhes, data_acao)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (usuario_id, acao, entidade, entidade_id, detalhes, datetime.now()),
            )
    except Exception as e:
        logger.error("Falha ao registrar auditoria: %s", e)


def registrar_acao(acao: str, entidade: str = None, entidade_id: int = None, detalhes: str = None) -> None:
    """Versão pública para registrar ações do usuário logado."""
    user = usuario_logado()
    uid = user["id"] if user else None
    _registrar_auditoria(uid, acao, entidade, entidade_id, detalhes)
