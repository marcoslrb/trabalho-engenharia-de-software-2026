"""
app.py — Ponto de entrada do Sistema de Ouvidoria v2.0
Executa: streamlit run app.py
"""

import sys
import os

# Garante que o diretório raiz do projeto está no sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from database.migrations import run_migrations
from services.auth_service import usuario_logado, encerrar_sessao

# ── Configuração da página ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sistema de Ouvidoria",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "Sistema de Ouvidoria v2.0 — Trabalho de Engenharia de Software 2026",
    },
)

# CSS global
st.markdown("""
<style>
    /* Remove padding extra do topo */
    .block-container { padding-top: 1.5rem; }
    /* Sidebar mais limpa */
    section[data-testid="stSidebar"] { background: #f0f4ff; }
    /* Métricas */
    [data-testid="metric-container"] { background: #fff; border-radius: 10px; padding: 12px; border: 1px solid #e0e8ff; }
    /* Botões primários */
    .stButton > button[kind="primary"] { background: linear-gradient(135deg, #1f4e79, #2e75b6); border: none; }
    /* Expander */
    details summary { font-size: 0.95rem; }
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-thumb { background: #b0c4de; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


def inicializar():
    """Inicializa banco de dados na primeira execução."""
    if "db_inicializado" not in st.session_state:
        run_migrations()
        st.session_state["db_inicializado"] = True


def sidebar_cidadao():
    """Sidebar da área do cidadão."""
    st.sidebar.markdown("## 🏛️ Ouvidoria")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📌 Menu do Cidadão")

    paginas = {
        "🏠 Início": "home",
        "📝 Registrar Manifestação": "abertura",
        "🔍 Consultar Protocolo": "consulta",
    }
    for label, pagina in paginas.items():
        ativo = st.session_state.get("pagina_cidadao") == pagina
        if st.sidebar.button(label, key=f"sb_{pagina}", use_container_width=True,
                             type="primary" if ativo else "secondary"):
            st.session_state["pagina_cidadao"] = pagina
            st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("🔐 Área Administrativa", use_container_width=True):
        st.session_state["area"] = "admin"
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption("📌 Versão 2.0 | 2026")


def sidebar_admin(user: dict):
    """Sidebar da área administrativa."""
    from config.settings import PERFIL_LABELS, PERFIL_ADMIN

    st.sidebar.markdown("## 🔐 Painel Administrativo")
    st.sidebar.markdown(f"**{user['nome_completo']}**")
    st.sidebar.caption(f"Perfil: {PERFIL_LABELS.get(user['perfil'], user['perfil'])}")
    st.sidebar.markdown("---")

    paginas = [
        ("📊 Dashboard", "dashboard"),
        ("📈 Relatórios", "relatorios"),
    ]
    if user["perfil"] == PERFIL_ADMIN:
        paginas.append(("👥 Usuários", "usuarios"))

    for label, pagina in paginas:
        ativo = st.session_state.get("pagina_admin") == pagina
        if st.sidebar.button(label, key=f"adm_{pagina}", use_container_width=True,
                             type="primary" if ativo else "secondary"):
            st.session_state["pagina_admin"] = pagina
            st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        encerrar_sessao()
        st.session_state["area"] = "cidadao"
        st.rerun()
    if st.sidebar.button("← Portal do Cidadão", use_container_width=True):
        st.session_state["area"] = "cidadao"
        st.rerun()


def main():
    inicializar()

    # Determina área ativa
    area = st.session_state.get("area", "cidadao")

    # ── ÁREA ADMINISTRATIVA ───────────────────────────────────────────────────
    if area == "admin":
        user = usuario_logado()

        if not user:
            # Tela de login
            from ui.admin.login import render as render_login
            render_login()
            return

        # Usuário autenticado — exibe painel
        sidebar_admin(user)
        pagina_admin = st.session_state.get("pagina_admin", "dashboard")

        if pagina_admin == "dashboard":
            from ui.admin.dashboard import render as render_dashboard
            render_dashboard()
        elif pagina_admin == "detalhe":
            from ui.admin.detalhe import render as render_detalhe
            render_detalhe()
        elif pagina_admin == "relatorios":
            from ui.admin.relatorios import render as render_relatorios
            render_relatorios()
        elif pagina_admin == "usuarios":
            from ui.admin.admin_usuarios import render as render_usuarios
            render_usuarios()
        else:
            from ui.admin.dashboard import render as render_dashboard
            render_dashboard()

    # ── ÁREA DO CIDADÃO ───────────────────────────────────────────────────────
    else:
        sidebar_cidadao()
        pagina = st.session_state.get("pagina_cidadao", "home")

        if pagina == "home":
            from ui.cidadao.home import render as render_home
            render_home()
        elif pagina == "abertura":
            from ui.cidadao.abertura import render as render_abertura
            render_abertura()
        elif pagina == "consulta":
            from ui.cidadao.consulta import render as render_consulta
            render_consulta()
        else:
            from ui.cidadao.home import render as render_home
            render_home()


if __name__ == "__main__":
    main()
