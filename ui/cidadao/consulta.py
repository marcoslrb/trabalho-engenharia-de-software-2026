"""
ui/cidadao/consulta.py
Tela de consulta e acompanhamento de manifestação por protocolo.
RF06, RF07 — Consulta sem barreiras extras, com linha do tempo.
"""

import streamlit as st
from services.manifestacao_service import consultar_manifestacao
from repositories.anexo_repo import listar_por_manifestacao
from repositories.manifestacao_repo import buscar_por_protocolo
from utils.helpers import formatar_data_br, status_emoji, tamanho_legivel


def render():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h2 style="color:#1f4e79; margin-bottom:0.3rem;">🔍 Consultar Manifestação</h2>
        <p style="color:#555;">
            Informe o número de protocolo recebido no momento do registro para
            acompanhar o andamento da sua manifestação.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Voltar ao início", key="btn_voltar_consulta"):
        st.session_state["pagina_cidadao"] = "home"
        st.rerun()

    st.markdown("---")

    # Pré-preenche protocolo se veio da tela de abertura
    protocolo_default = st.session_state.pop("protocolo_consulta", "")

    with st.form("form_consulta"):
        protocolo_input = st.text_input(
            "Número do Protocolo",
            value=protocolo_default,
            placeholder="OUT-20260623120000-ABCD1234",
            max_chars=40,
            help="Digite o protocolo exatamente como exibido após o registro.",
        )
        consultar = st.form_submit_button("🔍 Consultar", use_container_width=True, type="primary")

    if consultar or protocolo_default:
        protocolo = protocolo_input.strip().upper()
        if not protocolo:
            st.warning("⚠️ Por favor, informe o número do protocolo.")
            return

        _exibir_resultado(protocolo)


def _exibir_resultado(protocolo: str):
    """Busca e exibe o resultado da consulta."""
    with st.spinner("Consultando..."):
        resultado = consultar_manifestacao(protocolo)

    if not resultado:
        st.error(f"❌ Protocolo **{protocolo}** não encontrado. Verifique o número e tente novamente.")
        return

    # Header do resultado
    status = resultado.get("status", "—")
    emoji = status_emoji(status)

    st.markdown(f"""
    <div style="background:#e7f3ff; border-left:5px solid #1f4e79;
                padding:16px; border-radius:8px; margin:16px 0;">
        <p style="margin:0; color:#555; font-size:0.85rem;">Protocolo localizado</p>
        <h3 style="margin:4px 0; color:#1f4e79; font-family:monospace;">{resultado['protocolo']}</h3>
        <div style="margin-top:8px;">
            <span style="background:#1f4e79; color:white; padding:4px 12px;
                         border-radius:20px; font-size:0.85rem; font-weight:bold;">
                {emoji} {status}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Detalhes
    col1, col2, col3 = st.columns(3)
    col1.metric("Categoria", resultado.get("categoria") or "—")
    col2.metric("Setor", resultado.get("setor") or "Não definido")
    col3.metric("Registrada em", formatar_data_br(resultado.get("data_registro")))

    if resultado.get("assunto"):
        st.markdown(f"**Assunto:** {resultado['assunto']}")

    if not resultado.get("eh_anonimo") and resultado.get("nome_cidadao"):
        st.caption(f"Manifestante: {resultado['nome_cidadao']}")

    # Resposta do gestor
    if resultado.get("resposta_gestor"):
        st.markdown("---")
        st.markdown("#### 💬 Resposta da Ouvidoria")
        st.info(resultado["resposta_gestor"])

    # Parecer de encerramento
    if resultado.get("data_encerramento") and resultado.get("status") == "Concluída":
        st.markdown(f"✅ **Encerrada em:** {formatar_data_br(resultado.get('data_encerramento'))}")

    # Linha do tempo
    historico = resultado.get("historico", [])
    if historico:
        st.markdown("---")
        st.markdown("#### 📅 Histórico de Andamento")

        for i, entrada in enumerate(reversed(historico)):
            icon = status_emoji(entrada.get("status_novo", ""))
            data = formatar_data_br(entrada.get("data_alteracao"))
            obs = entrada.get("observacao") or ""

            cor_bg = "#e8f8ef" if i == 0 else "#f8f9fa"
            cor_borda = "#28a745" if i == 0 else "#dee2e6"

            st.markdown(f"""
            <div style="background:{cor_bg}; border-left:3px solid {cor_borda};
                        padding:12px 16px; border-radius:6px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong>{icon} {entrada.get("status_novo", "")}</strong>
                    <small style="color:#888;">{data}</small>
                </div>
                {f'<p style="margin:4px 0 0 0; color:#555; font-size:0.9rem;">{obs}</p>' if obs else ''}
            </div>
            """, unsafe_allow_html=True)

    # Anexos (lista sem download público por segurança)
    try:
        manifestacao_raw = buscar_por_protocolo(protocolo)
        if manifestacao_raw:
            anexos = listar_por_manifestacao(manifestacao_raw["id"])
            if anexos:
                st.markdown("---")
                st.markdown(f"#### 📎 Anexos ({len(anexos)})")
                for a in anexos:
                    tamanho = tamanho_legivel(a.get("tamanho_bytes") or 0)
                    st.caption(f"📄 {a['nome_original']} — {tamanho}")
    except Exception:
        pass

    st.markdown("---")
    st.caption(
        "Para mais informações, entre em contato com a Ouvidoria pelo canal oficial. "
        f"Última atualização: {formatar_data_br(resultado.get('data_atualizacao'))}"
    )
