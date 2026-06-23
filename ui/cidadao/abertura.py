"""
ui/cidadao/abertura.py
Formulário completo de abertura de manifestação.
RF01, RF02, RF03, RF04, RF05 — Todos os campos e validações obrigatórios.
"""

import streamlit as st
from services import manifestacao_service, anexo_service
from config.settings import (
    MAX_FILES_PER_MANIFESTACAO, MAX_FILE_SIZE_MB,
    MANIFESTACAO_MIN_CHARS, MANIFESTACAO_MAX_CHARS,
    SETORES_PADRAO,
)


def render():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h2 style="color:#1f4e79; margin-bottom:0.3rem;">📝 Registrar Manifestação</h2>
        <p style="color:#555;">
            Preencha o formulário abaixo para registrar sua manifestação.
            Ao final, você receberá um número de protocolo único para acompanhamento.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Voltar ao início", key="btn_voltar_abertura"):
        st.session_state["pagina_cidadao"] = "home"
        st.rerun()

    st.markdown("---")

    # Categorias disponíveis
    categorias = manifestacao_service.listar_categorias_ativas()

    with st.form("form_manifestacao_v2", clear_on_submit=False):
        # ── Tipo e assunto ──────────────────────────────────────────────────────
        st.markdown("#### 📋 Informações da Manifestação")
        col1, col2 = st.columns(2)
        with col1:
            categoria = st.selectbox(
                "Tipo de manifestação *",
                options=categorias,
                help="Selecione o tipo que melhor descreve sua manifestação.",
            )
        with col2:
            setor = st.selectbox(
                "Setor relacionado",
                options=["(Não sei informar)"] + SETORES_PADRAO,
                help="Setor ou área responsável pelo tema da manifestação.",
            )

        assunto = st.text_input(
            "Assunto (resumo breve) *",
            max_chars=120,
            placeholder="Ex.: Buraco na calçada da Rua das Flores",
            help="Resumo de até 120 caracteres para identificação rápida.",
        )

        texto_manifestacao = st.text_area(
            "Descrição detalhada *",
            height=200,
            max_chars=MANIFESTACAO_MAX_CHARS,
            placeholder=(
                "Descreva detalhadamente sua manifestação. "
                f"Mínimo {MANIFESTACAO_MIN_CHARS} caracteres, máximo {MANIFESTACAO_MAX_CHARS}.\n\n"
                "Inclua: local, data, pessoas envolvidas, evidências disponíveis."
            ),
        )
        chars = len(texto_manifestacao) if texto_manifestacao else 0
        st.caption(f"{chars}/{MANIFESTACAO_MAX_CHARS} caracteres")

        st.markdown("---")

        # ── Identificação ───────────────────────────────────────────────────────
        st.markdown("#### 👤 Identificação")
        st.info(
            "ℹ️ Você pode enviar sua manifestação anonimamente. "
            "Se optar por se identificar, o CPF é **obrigatório**. "
            "Manifestações identificadas permitem notificação por e-mail sobre o andamento."
        )

        eh_anonimo = st.checkbox(
            "🔒 Quero manter minha manifestação **anônima**",
            value=False,
            help="Manifestações anônimas não armazenam nenhum dado pessoal.",
        )

        nome_cidadao = email_cidadao = cpf_cidadao = telefone_cidadao = None

        if not eh_anonimo:
            st.markdown("**Dados de identificação** (obrigatórios)")
            col1, col2 = st.columns(2)
            with col1:
                nome_cidadao = st.text_input(
                    "Nome completo *",
                    placeholder="Seu nome e sobrenome",
                    max_chars=200,
                )
                cpf_cidadao = st.text_input(
                    "CPF *",
                    placeholder="000.000.000-00",
                    max_chars=14,
                    help="CPF é obrigatório para manifestações identificadas.",
                )
            with col2:
                email_cidadao = st.text_input(
                    "E-mail *",
                    placeholder="voce@email.com",
                    max_chars=254,
                    help="Será usado para notificações sobre sua manifestação.",
                )
                telefone_cidadao = st.text_input(
                    "Telefone (opcional)",
                    placeholder="(00) 00000-0000",
                    max_chars=20,
                )

        st.markdown("---")

        # ── Anexos ──────────────────────────────────────────────────────────────
        st.markdown("#### 📎 Arquivos Anexos (opcional)")
        st.caption(
            f"Máximo {MAX_FILES_PER_MANIFESTACAO} arquivos | "
            f"Máximo {MAX_FILE_SIZE_MB} MB por arquivo | "
            "Formatos: PDF, DOC, DOCX, TXT, JPG, PNG, XLS, XLSX, entre outros."
        )

        arquivos_upload = st.file_uploader(
            "Selecione os arquivos",
            accept_multiple_files=True,
            type=None,  # Validação manual para mensagens específicas
            key="upload_manifestacao",
        )

        st.markdown("---")

        # ── Submissão ───────────────────────────────────────────────────────────
        submitted = st.form_submit_button(
            "✅ Registrar Manifestação",
            use_container_width=True,
            type="primary",
        )

        if submitted:
            _processar_formulario(
                eh_anonimo=eh_anonimo,
                categoria=categoria,
                assunto=assunto,
                texto_manifestacao=texto_manifestacao,
                setor=setor if setor != "(Não sei informar)" else None,
                nome_cidadao=nome_cidadao,
                email_cidadao=email_cidadao,
                cpf_cidadao=cpf_cidadao,
                telefone_cidadao=telefone_cidadao,
                arquivos_upload=arquivos_upload,
            )


def _processar_formulario(**dados_form):
    """Processa e valida o formulário antes de chamar o service."""
    arquivos = dados_form.pop("arquivos_upload") or []

    # Validação de arquivos antes de tudo
    if arquivos:
        ok, erros = anexo_service.validar_lista_arquivos(arquivos)
        if not ok:
            for erro in erros:
                st.error(erro)
            return

    # Monta dados para o service
    dados = {
        "eh_anonimo": dados_form["eh_anonimo"],
        "categoria": dados_form["categoria"],
        "assunto": dados_form.get("assunto", ""),
        "texto_manifestacao": dados_form.get("texto_manifestacao", ""),
        "setor": dados_form.get("setor"),
        "nome_cidadao": dados_form.get("nome_cidadao"),
        "email_cidadao": dados_form.get("email_cidadao"),
        "cpf_cidadao": dados_form.get("cpf_cidadao"),
        "telefone_cidadao": dados_form.get("telefone_cidadao"),
    }

    sucesso, mensagem, protocolo = manifestacao_service.registrar_manifestacao(
        dados, arquivos if arquivos else None
    )

    if sucesso:
        st.session_state["ultimo_protocolo"] = protocolo
        st.success("✅ Manifestação registrada com sucesso!")
        _exibir_protocolo(protocolo, dados_form.get("email_cidadao"), dados_form["eh_anonimo"])
        st.balloons()
    else:
        # Exibe cada erro de validação separadamente
        for linha in mensagem.strip().split("\n"):
            if linha.strip():
                st.error(linha)


def _exibir_protocolo(protocolo: str, email: str, eh_anonimo: bool):
    """Exibe o protocolo gerado com instruções claras."""
    st.markdown(f"""
    <div style="background:#e7f3ff; border-left:5px solid #1f77b4;
                padding:20px; border-radius:8px; margin:16px 0;">
        <p style="margin:0; color:#555; font-size:0.9rem;">Número de Protocolo:</p>
        <h2 style="margin:8px 0; color:#1f4e79; font-family:monospace; letter-spacing:2px;">
            {protocolo}
        </h2>
        <p style="margin:0; color:#333;">
            <strong>📌 Guarde este número!</strong>
            Ele é a única forma de acompanhar sua manifestação.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not eh_anonimo and email:
        st.info(f"📧 Um e-mail de confirmação foi enviado para **{email}** com o número do protocolo.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Acompanhar esta manifestação", use_container_width=True, key="btn_acompanhar_pos"):
            st.session_state["protocolo_consulta"] = protocolo
            st.session_state["pagina_cidadao"] = "consulta"
            st.rerun()
    with col2:
        if st.button("📝 Registrar nova manifestação", use_container_width=True, key="btn_nova_pos"):
            st.session_state.pop("ultimo_protocolo", None)
            st.rerun()
