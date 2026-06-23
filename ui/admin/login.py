"""
ui/admin/login.py
Tela de login para a área administrativa.
RF09 — Login seguro com bcrypt.
"""

import streamlit as st
from services.auth_service import tentar_login, iniciar_sessao


def render():
    # Centraliza o card de login
    col_esq, col_centro, col_dir = st.columns([1, 2, 1])

    with col_centro:
        st.markdown("""
        <div style="text-align:center; padding:2rem 0 1.5rem 0;">
            <div style="font-size:3rem;">🔐</div>
            <h2 style="color:#1f4e79; margin-bottom:0.3rem;">Área Administrativa</h2>
            <p style="color:#666; font-size:0.95rem;">
                Acesso restrito a atendentes, gestores e administradores.
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_login"):
            username = st.text_input(
                "Usuário",
                placeholder="seu.usuario",
                autocomplete="username",
            )
            senha = st.text_input(
                "Senha",
                type="password",
                placeholder="••••••••",
                autocomplete="current-password",
            )
            entrar = st.form_submit_button("🔐 Entrar", use_container_width=True, type="primary")

            if entrar:
                if not username or not senha:
                    st.error("❌ Usuário e senha são obrigatórios.")
                else:
                    with st.spinner("Verificando credenciais..."):
                        sucesso, mensagem, usuario = tentar_login(username, senha)

                    if sucesso:
                        iniciar_sessao(usuario)
                        st.success(f"✅ Bem-vindo, **{usuario['nome_completo']}**!")
                        st.rerun()
                    else:
                        st.error(f"❌ {mensagem}")

        st.markdown("---")
        st.caption(
            "🔒 Esta área é protegida por autenticação segura (bcrypt). "
            "Tentativas de acesso são registradas para auditoria."
        )
        if st.button("← Voltar ao Portal do Cidadão", key="btn_volta_login"):
            st.session_state["area"] = "cidadao"
            st.rerun()
