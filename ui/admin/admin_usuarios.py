"""
ui/admin/admin_usuarios.py
Gestão de usuários internos — exclusiva para perfil 'admin'.
RF19 — Gerenciamento de usuários administradores.
"""

import streamlit as st
from repositories import usuario_repo
from services.auth_service import hash_senha, usuario_logado, registrar_acao
from utils.helpers import formatar_data_br
from config.settings import PERFIS_VALIDOS, PERFIL_LABELS, PERFIL_ADMIN


def render():
    user = usuario_logado()
    if not user or user["perfil"] != PERFIL_ADMIN:
        st.error("❌ Acesso restrito a administradores do sistema.")
        return

    st.markdown("### 👥 Gerenciamento de Usuários Internos")
    st.info("Crie, ative/desative e gerencie os usuários com acesso à área administrativa.")

    tab_lista, tab_novo = st.tabs(["📋 Usuários Cadastrados", "➕ Novo Usuário"])

    # ── Lista de usuários ────────────────────────────────────────────────────────
    with tab_lista:
        usuarios = usuario_repo.listar_todos()
        if not usuarios:
            st.info("Nenhum usuário cadastrado.")
        else:
            for u in usuarios:
                ativo = bool(u.get("ativo", 1))
                cor = "#e8f8ef" if ativo else "#fff3cd"
                status_txt = "✅ Ativo" if ativo else "⚠️ Inativo"

                with st.expander(f"{status_txt} — **{u['nome_completo']}** ({u['username']}) | {PERFIL_LABELS.get(u['perfil'], u['perfil'])}"):
                    col1, col2, col3 = st.columns(3)
                    col1.markdown(f"**E-mail:** {u['email']}")
                    col2.markdown(f"**Perfil:** {PERFIL_LABELS.get(u['perfil'], u['perfil'])}")
                    col3.markdown(f"**Último login:** {formatar_data_br(u.get('ultimo_login'))}")

                    # Não permite desativar o próprio usuário
                    if u["id"] != user["id"]:
                        c1, c2 = st.columns(2)
                        with c1:
                            label = "⛔ Desativar" if ativo else "✅ Ativar"
                            if st.button(label, key=f"toggle_{u['id']}"):
                                usuario_repo.ativar_desativar(u["id"], not ativo)
                                registrar_acao("TOGGLE_USUARIO", "usuarios_internos", u["id"])
                                st.success("Usuário atualizado!")
                                st.rerun()
                        with c2:
                            if st.button("🔑 Resetar senha", key=f"reset_{u['id']}"):
                                st.session_state[f"reset_user_{u['id']}"] = True

                    # Form de reset de senha
                    if st.session_state.get(f"reset_user_{u['id']}"):
                        with st.form(f"form_reset_{u['id']}"):
                            nova_senha = st.text_input("Nova senha", type="password", min_chars=6)
                            confirmar = st.text_input("Confirmar senha", type="password")
                            salvar = st.form_submit_button("Salvar nova senha")
                            if salvar:
                                if nova_senha != confirmar:
                                    st.error("As senhas não conferem.")
                                elif len(nova_senha) < 6:
                                    st.error("A senha deve ter pelo menos 6 caracteres.")
                                else:
                                    usuario_repo.atualizar_senha(u["id"], hash_senha(nova_senha))
                                    registrar_acao("RESET_SENHA", "usuarios_internos", u["id"])
                                    st.success("Senha atualizada!")
                                    del st.session_state[f"reset_user_{u['id']}"]
                                    st.rerun()

    # ── Criação de novo usuário ──────────────────────────────────────────────────
    with tab_novo:
        st.markdown("#### ➕ Criar Novo Usuário")
        with st.form("form_novo_usuario"):
            col1, col2 = st.columns(2)
            with col1:
                nome_completo = st.text_input("Nome completo *", max_chars=200)
                username = st.text_input("Username *", placeholder="ex.: joao.silva", max_chars=50)
                perfil = st.selectbox(
                    "Perfil *",
                    options=list(PERFIS_VALIDOS),
                    format_func=lambda p: PERFIL_LABELS.get(p, p),
                )
            with col2:
                email = st.text_input("E-mail *", max_chars=254)
                senha = st.text_input("Senha *", type="password", min_chars=6)
                confirmar_senha = st.text_input("Confirmar senha *", type="password")

            criar = st.form_submit_button("➕ Criar Usuário", type="primary", use_container_width=True)

            if criar:
                erros = []
                if not nome_completo.strip():
                    erros.append("Nome é obrigatório.")
                if not username.strip():
                    erros.append("Username é obrigatório.")
                elif usuario_repo.username_existe(username):
                    erros.append(f"Username '{username}' já está em uso.")
                if not email.strip():
                    erros.append("E-mail é obrigatório.")
                elif usuario_repo.email_existe(email):
                    erros.append(f"E-mail '{email}' já está em uso.")
                if not senha:
                    erros.append("Senha é obrigatória.")
                elif len(senha) < 6:
                    erros.append("A senha deve ter pelo menos 6 caracteres.")
                elif senha != confirmar_senha:
                    erros.append("As senhas não conferem.")

                if erros:
                    for e in erros:
                        st.error(f"❌ {e}")
                else:
                    novo_id = usuario_repo.criar_usuario({
                        "username": username,
                        "nome_completo": nome_completo,
                        "email": email,
                        "senha_hash": hash_senha(senha),
                        "perfil": perfil,
                    })
                    registrar_acao("CRIAR_USUARIO", "usuarios_internos", novo_id)
                    st.success(f"✅ Usuário **{username}** criado com sucesso! (Perfil: {PERFIL_LABELS.get(perfil)})")
                    st.rerun()
