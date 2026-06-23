"""
ui/admin/detalhe.py
Tela de detalhe e atendimento de uma manifestação.
RF08, RF11, RF12, RF13, RF14 — Gestão completa de atendimento.
"""

import streamlit as st
from repositories.manifestacao_repo import buscar_por_protocolo
from repositories.historico_repo import listar_por_manifestacao
from repositories.anexo_repo import listar_por_manifestacao as listar_anexos
from services.manifestacao_service import atualizar_status_manifestacao
from services.auth_service import usuario_logado, registrar_acao
from utils.helpers import formatar_data_br, status_emoji, tamanho_legivel
from utils.validators import mascarar_cpf
from config.settings import STATUS_FLOW, STATUS_ENCERRAMENTO, SETORES_PADRAO


def render():
    protocolo = st.session_state.get("protocolo_selecionado")

    if st.button("← Voltar ao Dashboard", key="btn_voltar_detalhe"):
        st.session_state["pagina_admin"] = "dashboard"
        st.rerun()

    if not protocolo:
        st.info("Selecione uma manifestação no dashboard.")
        return

    manifestacao = buscar_por_protocolo(protocolo)
    if not manifestacao:
        st.error(f"Manifestação '{protocolo}' não encontrada.")
        return

    st.markdown(f"### 📂 Manifestação: `{protocolo}`")

    eh_anonimo = bool(manifestacao.get("eh_anonimo"))
    status_atual = manifestacao.get("status", "Recebida")

    # ── Informações do cidadão ──────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 👤 Solicitante")
        if eh_anonimo:
            st.markdown("🔒 **Manifestação anônima** — dados pessoais não disponíveis.")
        else:
            st.markdown(f"**Nome:** {manifestacao.get('nome_cidadao') or '—'}")
            st.markdown(f"**E-mail:** {manifestacao.get('email_cidadao') or '—'}")
            if manifestacao.get("cpf_cidadao"):
                cpf_mask = mascarar_cpf(manifestacao["cpf_cidadao"])
                st.markdown(f"**CPF:** {cpf_mask}")
            if manifestacao.get("telefone_cidadao"):
                st.markdown(f"**Telefone:** {manifestacao['telefone_cidadao']}")

    with col2:
        st.markdown("#### 📋 Classificação")
        st.markdown(f"**Categoria:** {manifestacao.get('categoria') or '—'}")
        st.markdown(f"**Assunto:** {manifestacao.get('assunto') or '—'}")
        st.markdown(f"**Setor:** {manifestacao.get('setor') or '(não definido)'}")
        st.markdown(f"**Registrada:** {formatar_data_br(manifestacao.get('data_registro'))}")
        st.markdown(f"**Status:** {status_emoji(status_atual)} {status_atual}")

    # ── Texto da manifestação ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📝 Descrição da Manifestação")
    st.markdown(
        f'<div style="background:#f8f9fa; border-left:4px solid #1f4e79; '
        f'padding:16px; border-radius:6px;">{manifestacao.get("texto_manifestacao", "")}</div>',
        unsafe_allow_html=True,
    )

    # ── Anexos ──────────────────────────────────────────────────────────────────
    anexos = listar_anexos(manifestacao["id"])
    if anexos:
        st.markdown("---")
        st.markdown(f"#### 📎 Anexos ({len(anexos)})")
        for a in anexos:
            col_a, col_b = st.columns([4, 1])
            with col_a:
                tamanho = tamanho_legivel(a.get("tamanho_bytes") or 0)
                st.markdown(f"📄 **{a['nome_original']}** — {tamanho} | {formatar_data_br(a['data_upload'])}")
            with col_b:
                _botao_download(manifestacao["id"], a)

    # ── Painel de atendimento ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### ⚙️ Atendimento")

    user = usuario_logado()
    encerrada = status_atual in STATUS_ENCERRAMENTO

    if encerrada:
        st.success("✅ Esta manifestação está **concluída**.")
        if manifestacao.get("parecer_encerramento"):
            st.markdown("**Parecer de encerramento:**")
            st.info(manifestacao["parecer_encerramento"])
        if manifestacao.get("resposta_gestor"):
            st.markdown("**Resposta ao cidadão:**")
            st.info(manifestacao["resposta_gestor"])
    else:
        with st.form("form_atendimento"):
            col1, col2 = st.columns(2)
            with col1:
                novo_status = st.selectbox(
                    "Novo status *",
                    options=STATUS_FLOW,
                    index=STATUS_FLOW.index(status_atual) if status_atual in STATUS_FLOW else 0,
                )
            with col2:
                novo_setor = st.selectbox(
                    "Encaminhar para setor",
                    options=["(Manter atual)"] + SETORES_PADRAO,
                    index=0,
                )

            observacao = st.text_area(
                "Observação interna",
                placeholder="Nota interna sobre a ação realizada (não visível ao cidadão).",
                height=80,
            )

            resposta_gestor = st.text_area(
                "Resposta ao cidadão",
                value=manifestacao.get("resposta_gestor") or "",
                placeholder="Resposta que será exibida ao cidadão ao consultar o protocolo.",
                height=120,
            )

            encerrar = novo_status in STATUS_ENCERRAMENTO
            if encerrar:
                st.warning("⚠️ Você está encerrando esta manifestação. O parecer abaixo é **obrigatório**.")

            parecer = st.text_area(
                "Parecer de encerramento" + (" *" if encerrar else ""),
                value=manifestacao.get("parecer_encerramento") or "",
                placeholder="Descreva detalhadamente o resultado e providências tomadas. Obrigatório ao concluir.",
                height=120,
                disabled=not encerrar,
            )

            salvar = st.form_submit_button("💾 Salvar Atualização", type="primary", use_container_width=True)

            if salvar:
                setor_novo = None if novo_setor == "(Manter atual)" else novo_setor
                ok, msg = atualizar_status_manifestacao(
                    manifestacao_id=manifestacao["id"],
                    status_novo=novo_status,
                    observacao=observacao or None,
                    resposta_gestor=resposta_gestor or None,
                    parecer_encerramento=parecer if encerrar else None,
                    setor=setor_novo,
                    usuario_id=user["id"] if user else None,
                )
                if ok:
                    registrar_acao(
                        "ATUALIZAR_STATUS",
                        "manifestacoes",
                        manifestacao["id"],
                        f"{status_atual} → {novo_status}",
                    )
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    # ── Histórico de status ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📅 Histórico de Status")
    historico = listar_por_manifestacao(manifestacao["id"])

    if not historico:
        st.info("Nenhuma atualização de status registrada ainda.")
    else:
        for entrada in reversed(historico):
            emoji_s = status_emoji(entrada.get("status_novo", ""))
            data = formatar_data_br(entrada.get("data_alteracao"))
            resp = entrada.get("nome_responsavel") or "Sistema"
            obs = entrada.get("observacao") or ""
            ant = entrada.get("status_anterior")

            st.markdown(f"""
            <div style="border-left:3px solid #1f4e79; padding:10px 16px;
                        margin-bottom:8px; background:#f8f9fa; border-radius:4px;">
                <strong>{emoji_s} {entrada['status_novo']}</strong>
                {f' &larr; <em style="color:#888">{ant}</em>' if ant else ''}
                <span style="float:right; color:#888; font-size:0.85rem;">{data} | {resp}</span>
                {f'<p style="margin:6px 0 0 0; color:#555; font-size:0.9rem;">{obs}</p>' if obs else ''}
            </div>
            """, unsafe_allow_html=True)


def _botao_download(manifestacao_id: int, anexo: dict):
    """Tenta exibir botão de download do arquivo."""
    try:
        from services.anexo_service import get_caminho_arquivo
        caminho = get_caminho_arquivo(manifestacao_id, anexo["nome_armazenado"])
        if caminho and caminho.exists():
            with open(caminho, "rb") as f:
                st.download_button(
                    "⬇️",
                    data=f.read(),
                    file_name=anexo["nome_original"],
                    mime=anexo.get("mime_type") or "application/octet-stream",
                    key=f"dl_{anexo['id']}",
                )
        else:
            st.caption("(arquivo não disponível)")
    except Exception:
        st.caption("(erro)")
