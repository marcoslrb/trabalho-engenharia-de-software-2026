"""
services/manifestacao_service.py
Regras de negócio para criação e gestão de manifestações.
Orquestra validação → persistência → histórico → e-mail.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from services.protocolo_service import gerar_protocolo
from services import email_service
from repositories import manifestacao_repo, historico_repo
from utils.validators import (
    validar_cpf, validar_email, validar_texto_manifestacao,
    validar_assunto, validar_nome, sanitizar_texto,
)
from config.settings import STATUS_CONCLUIDA, STATUS_ENCERRAMENTO

logger = logging.getLogger(__name__)


def registrar_manifestacao(dados: Dict, arquivos: List = None) -> Tuple[bool, str, Optional[str]]:
    """
    Registra uma nova manifestação.
    Retorna (sucesso, mensagem, protocolo).

    Fluxo:
    1. Validação dos dados
    2. Sanitização do texto
    3. Proteção do anonimato
    4. Persistência no banco
    5. Histórico inicial
    6. Envio de e-mail (se identificado e e-mail informado)
    7. Salva anexos (se houver)
    """
    erros = _validar_dados_manifestacao(dados)
    if erros:
        return False, "\n".join(erros), None

    # Sanitização
    dados["texto_manifestacao"] = sanitizar_texto(dados["texto_manifestacao"])
    if dados.get("assunto"):
        dados["assunto"] = dados["assunto"].strip()

    # Geração do protocolo
    protocolo = gerar_protocolo()
    dados["protocolo"] = protocolo

    # Persistência
    manifestacao_id = manifestacao_repo.inserir(dados)

    # Histórico inicial
    historico_repo.registrar(
        manifestacao_id=manifestacao_id,
        status_novo="Recebida",
        observacao="Manifestação registrada pelo cidadão.",
    )

    # Notificação por e-mail (apenas identificados com e-mail)
    if not dados.get("eh_anonimo") and dados.get("email_cidadao"):
        email_service.notificar_protocolo_gerado(
            email=dados["email_cidadao"],
            nome=dados.get("nome_cidadao", ""),
            protocolo=protocolo,
        )

    # Salvar anexos
    if arquivos:
        from services.anexo_service import salvar_arquivos
        salvar_arquivos(manifestacao_id, arquivos)

    return True, "Manifestação registrada com sucesso!", protocolo


def _validar_dados_manifestacao(dados: Dict) -> List[str]:
    """Valida todos os campos de entrada. Retorna lista de erros."""
    erros = []
    eh_anonimo = bool(dados.get("eh_anonimo", False))

    # Texto obrigatório
    ok, msg = validar_texto_manifestacao(dados.get("texto_manifestacao", ""))
    if not ok:
        erros.append(msg)

    # Assunto (obrigatório)
    ok, msg = validar_assunto(dados.get("assunto", ""), obrigatorio=True)
    if not ok:
        erros.append(msg)

    # Dados pessoais apenas se identificado
    if not eh_anonimo:
        ok, msg = validar_cpf(dados.get("cpf_cidadao", ""))
        if not ok:
            erros.append(msg)

        ok, msg = validar_nome(dados.get("nome_cidadao", ""), obrigatorio=True)
        if not ok:
            erros.append(msg)

        # E-mail é obrigatório para identificado
        ok, msg = validar_email(dados.get("email_cidadao", ""))
        if not ok:
            erros.append(msg)

    return erros


def atualizar_status_manifestacao(
    manifestacao_id: int,
    status_novo: str,
    observacao: Optional[str],
    resposta_gestor: Optional[str],
    parecer_encerramento: Optional[str],
    setor: Optional[str],
    usuario_id: Optional[int],
) -> Tuple[bool, str]:
    """
    Atualiza status de uma manifestação com histórico e notificação.
    RF08, RF13, RF14.
    """
    # Busca dados atuais
    manifestacao = manifestacao_repo.buscar_por_id(manifestacao_id)
    if not manifestacao:
        return False, "Manifestação não encontrada."

    # Valida parecer de encerramento (obrigatório ao concluir)
    if status_novo in STATUS_ENCERRAMENTO:
        if not parecer_encerramento or not parecer_encerramento.strip():
            return False, "O parecer de encerramento é obrigatório ao concluir uma manifestação."

    status_anterior = manifestacao.get("status")

    # Atualiza no banco
    manifestacao_repo.atualizar_status(
        manifestacao_id=manifestacao_id,
        status_novo=status_novo,
        resposta_gestor=resposta_gestor,
        parecer_encerramento=parecer_encerramento,
        setor=setor,
        responsavel_id=usuario_id,
    )

    # Registra no histórico
    historico_repo.registrar(
        manifestacao_id=manifestacao_id,
        status_novo=status_novo,
        status_anterior=status_anterior,
        observacao=observacao or f"Status atualizado para: {status_novo}",
        usuario_id=usuario_id,
    )

    # Notificações por e-mail (apenas para cidadãos identificados)
    email = manifestacao.get("email_cidadao")
    nome = manifestacao.get("nome_cidadao")
    protocolo = manifestacao.get("protocolo", "")

    if email:
        if status_novo in STATUS_ENCERRAMENTO:
            email_service.notificar_encerramento(email, nome, protocolo, parecer_encerramento)
        else:
            email_service.notificar_atualizacao_status(email, nome, protocolo, status_novo)

    return True, "Status atualizado com sucesso."


def consultar_manifestacao(protocolo: str) -> Optional[Dict]:
    """
    Consulta pública de manifestação por protocolo.
    RF06 — Sem barreiras extras além do protocolo.
    Dados pessoais sensíveis são mascarados na resposta.
    """
    manifestacao = manifestacao_repo.buscar_por_protocolo(protocolo)
    if not manifestacao:
        return None

    # Mascaramento de dados sensíveis para exibição pública
    resultado = {
        "protocolo": manifestacao["protocolo"],
        "categoria": manifestacao.get("categoria"),
        "assunto": manifestacao.get("assunto"),
        "status": manifestacao.get("status"),
        "setor": manifestacao.get("setor"),
        "data_registro": manifestacao.get("data_registro"),
        "data_atualizacao": manifestacao.get("data_atualizacao"),
        "data_encerramento": manifestacao.get("data_encerramento"),
        "resposta_gestor": manifestacao.get("resposta_gestor"),
        "eh_anonimo": bool(manifestacao.get("eh_anonimo")),
    }

    # Exibe nome apenas se identificado (sem CPF/e-mail na visão pública)
    if not manifestacao.get("eh_anonimo") and manifestacao.get("nome_cidadao"):
        resultado["nome_cidadao"] = manifestacao["nome_cidadao"]

    # Histórico de status
    historico = historico_repo.listar_por_manifestacao(manifestacao["id"])
    resultado["historico"] = [
        {
            "status_novo": h["status_novo"],
            "data_alteracao": h["data_alteracao"],
            "observacao": h.get("observacao"),
        }
        for h in historico
    ]

    return resultado


def listar_categorias_ativas() -> List[str]:
    """Retorna lista de categorias ativas para o formulário."""
    from database.connection import db_session
    with db_session() as conn:
        rows = conn.execute(
            "SELECT nome FROM categorias WHERE ativo = 1 ORDER BY nome"
        ).fetchall()
        return [r["nome"] for r in rows]
