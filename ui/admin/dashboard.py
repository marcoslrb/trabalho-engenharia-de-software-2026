"""
ui/admin/dashboard.py
Dashboard administrativo com métricas e listagem filtrada.
RF10, RF03 — Painel com filtros e métricas completas.
"""

import streamlit as st
import pandas as pd
from repositories.manifestacao_repo import (
    listar_todas, estatisticas_gerais,
    contar_por_status, contar_por_categoria,
)
from utils.helpers import formatar_data_br, status_emoji, truncar_texto
from config.settings import STATUS_FLOW, SETORES_PADRAO


def render():
    st.markdown("### 📊 Dashboard — Painel de Gestão")

    # ── Métricas gerais ─────────────────────────────────────────────────────────
    try:
        stats = estatisticas_gerais()
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("📋 Total", stats["total"])
        c2.metric("🔒 Anônimas", stats["anonimas"])
        c3.metric("👤 Identificadas", stats["identificadas"])
        c4.metric("⏳ Em andamento", stats["abertas"])
        c5.metric("✅ Concluídas", stats["concluidas"])
    except Exception as e:
        st.warning(f"Erro ao carregar estatísticas: {e}")

    st.markdown("---")

    # ── Filtros ─────────────────────────────────────────────────────────────────
    with st.expander("🔽 Filtros de busca", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_status = st.selectbox(
                "Status",
                ["Todos"] + STATUS_FLOW,
                key="dash_status",
            )
        with col2:
            filtro_tipo = st.selectbox(
                "Tipo (anonimato)",
                ["Todos", "Anônimas", "Identificadas"],
                key="dash_tipo",
            )
        with col3:
            filtro_setor = st.selectbox(
                "Setor",
                ["Todos"] + SETORES_PADRAO,
                key="dash_setor",
            )

        col4, col5 = st.columns(2)
        with col4:
            data_inicio = st.date_input("Data início", value=None, key="dash_di")
        with col5:
            data_fim = st.date_input("Data fim", value=None, key="dash_df")

    # ── Busca com filtros ───────────────────────────────────────────────────────
    params = {
        "filtro_status": None if filtro_status == "Todos" else filtro_status,
        "filtro_anonimo": None if filtro_tipo == "Todos" else (filtro_tipo == "Anônimas"),
        "filtro_setor": None if filtro_setor == "Todos" else filtro_setor,
        "data_inicio": str(data_inicio) if data_inicio else None,
        "data_fim": str(data_fim) if data_fim else None,
    }

    try:
        manifestacoes = listar_todas(**params)
    except Exception as e:
        st.error(f"Erro ao carregar manifestações: {e}")
        return

    st.markdown(f"#### 📋 Manifestações ({len(manifestacoes)} encontradas)")

    if not manifestacoes:
        st.info("📭 Nenhuma manifestação encontrada com os filtros aplicados.")
        return

    # ── Tabela de listagem ──────────────────────────────────────────────────────
    for m in manifestacoes:
        protocolo = m["protocolo"]
        status = m.get("status", "Recebida")
        categoria = m.get("categoria", "—")
        eh_anonimo = bool(m.get("eh_anonimo"))
        data = formatar_data_br(m.get("data_registro"))
        assunto = truncar_texto(m.get("assunto") or m.get("texto_manifestacao", ""), 80)
        emoji_s = status_emoji(status)

        tipo_badge = "🔒 Anônima" if eh_anonimo else "👤 Identificada"

        header = (
            f"{emoji_s} **{protocolo}** | {categoria} | {tipo_badge} | "
            f"`{status}` | {data}"
        )

        with st.expander(header):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Assunto:** {m.get('assunto') or '(sem assunto)'}")
                st.markdown(f"**Descrição:** {truncar_texto(m.get('texto_manifestacao', ''), 300)}")
                if not eh_anonimo:
                    nome = m.get("nome_cidadao") or "—"
                    email = m.get("email_cidadao") or "—"
                    st.markdown(f"**Cidadão:** {nome} | **E-mail:** {email}")
                if m.get("setor"):
                    st.markdown(f"**Setor:** {m['setor']}")
                if m.get("resposta_gestor"):
                    st.markdown(f"**Resposta:** {truncar_texto(m['resposta_gestor'], 150)}")
            with col2:
                if st.button("📂 Abrir", key=f"open_{protocolo}", use_container_width=True):
                    st.session_state["protocolo_selecionado"] = protocolo
                    st.session_state["pagina_admin"] = "detalhe"
                    st.rerun()

    # ── Gráficos resumidos ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📈 Distribuição por Status")
    try:
        dist_status = contar_por_status()
        if dist_status:
            df_status = pd.DataFrame(
                list(dist_status.items()), columns=["Status", "Quantidade"]
            ).sort_values("Quantidade", ascending=False)
            st.bar_chart(df_status.set_index("Status"))
    except Exception:
        pass
