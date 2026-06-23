"""
ui/admin/relatorios.py
Relatórios gerenciais exportáveis em CSV e XLSX.
RF17, RF18 — Relatórios exportáveis.
"""

import io
import streamlit as st
import pandas as pd
from repositories.manifestacao_repo import listar_todas
from utils.helpers import formatar_data_br
from config.settings import STATUS_FLOW, SETORES_PADRAO


def render():
    st.markdown("### 📈 Relatórios Gerenciais")
    st.info(
        "Gere relatórios filtrados e exporte em CSV ou XLSX. "
        "**Dados pessoais de manifestações anônimas são omitidos automaticamente.**"
    )

    # ── Filtros ─────────────────────────────────────────────────────────────────
    with st.form("form_relatorio"):
        col1, col2 = st.columns(2)
        with col1:
            status_sel = st.multiselect("Status", STATUS_FLOW, default=[], key="rel_status")
            data_inicio = st.date_input("Data início", value=None, key="rel_di")
        with col2:
            setor_sel = st.selectbox("Setor", ["Todos"] + SETORES_PADRAO, key="rel_setor")
            data_fim = st.date_input("Data fim", value=None, key="rel_df")

        incluir_texto = st.checkbox("Incluir texto completo da manifestação", value=False)
        gerar = st.form_submit_button("📊 Gerar Relatório", type="primary", use_container_width=True)

    if not gerar:
        return

    # ── Busca ───────────────────────────────────────────────────────────────────
    with st.spinner("Gerando relatório..."):
        params = {
            "filtro_status": None if not status_sel else None,  # usa loop abaixo
            "filtro_setor": None if setor_sel == "Todos" else setor_sel,
            "data_inicio": str(data_inicio) if data_inicio else None,
            "data_fim": str(data_fim) if data_fim else None,
        }
        manifestacoes = listar_todas(**params)

        # Filtro por múltiplos status
        if status_sel:
            manifestacoes = [m for m in manifestacoes if m.get("status") in status_sel]

    if not manifestacoes:
        st.warning("Nenhuma manifestação encontrada para os filtros selecionados.")
        return

    # ── Monta DataFrame ─────────────────────────────────────────────────────────
    linhas = []
    for m in manifestacoes:
        eh_anonimo = bool(m.get("eh_anonimo"))
        linha = {
            "Protocolo": m["protocolo"],
            "Data Registro": formatar_data_br(m.get("data_registro")),
            "Categoria": m.get("categoria") or "—",
            "Assunto": m.get("assunto") or "—",
            "Status": m.get("status") or "—",
            "Setor": m.get("setor") or "—",
            "Tipo": "Anônima" if eh_anonimo else "Identificada",
            # Dados pessoais apenas se identificado
            "Cidadão": "(Anônimo)" if eh_anonimo else (m.get("nome_cidadao") or "—"),
            "E-mail": "(Anônimo)" if eh_anonimo else (m.get("email_cidadao") or "—"),
            "Data Atualização": formatar_data_br(m.get("data_atualizacao")),
            "Data Encerramento": formatar_data_br(m.get("data_encerramento")) if m.get("data_encerramento") else "—",
        }
        if incluir_texto:
            linha["Descrição"] = m.get("texto_manifestacao") or ""
            linha["Resposta"] = m.get("resposta_gestor") or "—"
            linha["Parecer"] = m.get("parecer_encerramento") or "—"

        linhas.append(linha)

    df = pd.DataFrame(linhas)

    # ── Exibição ────────────────────────────────────────────────────────────────
    st.markdown(f"#### 📋 Resultado: {len(df)} manifestações")
    st.dataframe(df, use_container_width=True)

    # ── Exportação ──────────────────────────────────────────────────────────────
    st.markdown("#### ⬇️ Exportar")
    col_csv, col_xlsx = st.columns(2)

    with col_csv:
        csv_data = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "📄 Download CSV",
            data=csv_data.encode("utf-8-sig"),
            file_name="relatorio_ouvidoria.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_xlsx:
        xlsx_buffer = io.BytesIO()
        with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Manifestações")
        xlsx_buffer.seek(0)
        st.download_button(
            "📊 Download XLSX",
            data=xlsx_buffer.getvalue(),
            file_name="relatorio_ouvidoria.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    # ── Sumário estatístico ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📊 Sumário")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Por Status:**")
        st.dataframe(df["Status"].value_counts().reset_index().rename(columns={"index": "Status", "Status": "Qtd"}))
    with col2:
        st.markdown("**Por Categoria:**")
        st.dataframe(df["Categoria"].value_counts().reset_index().rename(columns={"index": "Categoria", "Categoria": "Qtd"}))
