"""
ui/cidadao/home.py
Tela inicial do portal do cidadão.
"""

import streamlit as st
from repositories.manifestacao_repo import estatisticas_gerais
from utils.helpers import status_emoji


def render():
    st.markdown("""
    <div style="text-align:center; padding: 2rem 0 1rem 0;">
        <div style="font-size:3.5rem;">🏛️</div>
        <h1 style="color:#1f4e79; font-size:2.2rem; margin-bottom:0.3rem;">
            Sistema de Ouvidoria
        </h1>
        <p style="color:#555; font-size:1.1rem; max-width:600px; margin:auto;">
            Canal oficial para registro e acompanhamento de manifestações, denúncias,
            reclamações, sugestões e elogios.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#1f4e79,#2e75b6);
                    border-radius:12px; padding:24px; color:white; text-align:center;">
            <div style="font-size:2.5rem;">📝</div>
            <h3 style="margin:8px 0; color:white;">Abrir Manifestação</h3>
            <p style="color:rgba(255,255,255,0.85); font-size:0.9rem;">
                Registre sua denúncia, reclamação, sugestão ou elogio
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📝 Registrar Manifestação", use_container_width=True, type="primary", key="btn_abrir"):
            st.session_state["pagina_cidadao"] = "abertura"
            st.rerun()

    with col2:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#1e6b47,#28a745);
                    border-radius:12px; padding:24px; color:white; text-align:center;">
            <div style="font-size:2.5rem;">🔍</div>
            <h3 style="margin:8px 0; color:white;">Consultar Protocolo</h3>
            <p style="color:rgba(255,255,255,0.85); font-size:0.9rem;">
                Acompanhe o andamento da sua manifestação pelo número de protocolo
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Consultar Protocolo", use_container_width=True, key="btn_consultar"):
            st.session_state["pagina_cidadao"] = "consulta"
            st.rerun()

    st.markdown("---")

    # Estatísticas públicas (sem dados pessoais)
    try:
        stats = estatisticas_gerais()
        st.markdown("#### 📊 Situação da Ouvidoria")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Manifestações", stats["total"])
        c2.metric("Em Andamento", stats["abertas"])
        c3.metric("Concluídas", stats["concluidas"])
    except Exception:
        pass

    st.markdown("---")
    st.markdown("""
    <div style="background:#f8f9fa; border-radius:10px; padding:20px; margin-top:1rem;">
    <h4>ℹ️ Tipos de Manifestação</h4>
    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; margin-top:12px;">
        <div><strong>🚨 Denúncia</strong><br><small style="color:#666;">Irregularidades e infrações</small></div>
        <div><strong>😤 Reclamação</strong><br><small style="color:#666;">Insatisfação com serviços</small></div>
        <div><strong>📋 Solicitação</strong><br><small style="color:#666;">Pedidos e requerimentos</small></div>
        <div><strong>💡 Sugestão</strong><br><small style="color:#666;">Propostas de melhoria</small></div>
        <div><strong>👏 Elogio</strong><br><small style="color:#666;">Reconhecimento positivo</small></div>
        <div><strong>❓ Informação</strong><br><small style="color:#666;">Pedidos de esclarecimento</small></div>
    </div>
    </div>
    """, unsafe_allow_html=True)
