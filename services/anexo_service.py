"""
services/anexo_service.py
Lógica de negócio para upload, validação e armazenamento de arquivos.
RF04 — Máx 5 arquivos, tipos permitidos, tamanho máx 10MB.
"""

import os
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

from config.settings import (
    UPLOADS_DIR, MAX_FILES_PER_MANIFESTACAO,
    MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB,
    ALLOWED_EXTENSIONS, BLOCKED_EXTENSIONS,
)
from repositories import anexo_repo

logger = logging.getLogger(__name__)


def validar_arquivo(arquivo) -> Tuple[bool, str]:
    """
    Valida um único arquivo enviado via Streamlit (UploadedFile).
    Verifica: tamanho, extensão permitida e extensão bloqueada.
    """
    nome = arquivo.name
    ext = Path(nome).suffix.lower()
    tamanho = arquivo.size

    # Bloqueia extensões perigosas independentemente
    if ext in BLOCKED_EXTENSIONS:
        return False, f"❌ '{nome}': tipo de arquivo não permitido por segurança ({ext})."

    # Verifica se a extensão está na lista de permitidos
    if ext not in ALLOWED_EXTENSIONS:
        permitidas = ", ".join(sorted(ALLOWED_EXTENSIONS))
        return False, f"❌ '{nome}': extensão '{ext}' não permitida. Use: {permitidas}"

    # Verifica tamanho
    if tamanho > MAX_FILE_SIZE_BYTES:
        tam_mb = tamanho / (1024 * 1024)
        return False, (
            f"❌ '{nome}': arquivo muito grande ({tam_mb:.1f} MB). "
            f"Máximo permitido: {MAX_FILE_SIZE_MB} MB."
        )

    return True, ""


def validar_lista_arquivos(arquivos: List) -> Tuple[bool, List[str]]:
    """
    Valida uma lista de arquivos.
    Retorna (tudo_ok, lista_de_erros).
    """
    erros = []

    if len(arquivos) > MAX_FILES_PER_MANIFESTACAO:
        erros.append(
            f"❌ Máximo de {MAX_FILES_PER_MANIFESTACAO} arquivos permitidos "
            f"(você tentou enviar {len(arquivos)})."
        )
        return False, erros

    for arquivo in arquivos:
        ok, msg = validar_arquivo(arquivo)
        if not ok:
            erros.append(msg)

    return len(erros) == 0, erros


def salvar_arquivos(manifestacao_id: int, arquivos: List) -> List[Dict]:
    """
    Salva os arquivos no disco e registra metadados no banco.
    Retorna lista de metadados dos arquivos salvos.

    Estratégia de nomeação: UUID aleatório preserva o nome original apenas nos metadados,
    evitando colisões e path traversal.
    """
    salvos = []
    pasta = UPLOADS_DIR / str(manifestacao_id)
    pasta.mkdir(parents=True, exist_ok=True)

    for arquivo in arquivos:
        ext = Path(arquivo.name).suffix.lower()
        nome_armazenado = f"{uuid.uuid4().hex}{ext}"
        caminho = pasta / nome_armazenado

        # Salva o arquivo
        conteudo = arquivo.read()
        with open(caminho, "wb") as f:
            f.write(conteudo)

        # Registra metadados no banco
        meta = {
            "manifestacao_id": manifestacao_id,
            "nome_original": arquivo.name,
            "nome_armazenado": nome_armazenado,
            "mime_type": arquivo.type if hasattr(arquivo, "type") else None,
            "tamanho_bytes": arquivo.size,
        }
        meta["id"] = anexo_repo.inserir(meta)
        salvos.append(meta)
        logger.info("Arquivo salvo: %s -> %s", arquivo.name, caminho)

    return salvos


def get_caminho_arquivo(manifestacao_id: int, nome_armazenado: str) -> Optional[Path]:
    """Retorna o caminho absoluto de um arquivo armazenado."""
    caminho = UPLOADS_DIR / str(manifestacao_id) / nome_armazenado
    if caminho.exists():
        return caminho
    return None
