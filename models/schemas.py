"""
models/schemas.py
Dataclasses representando as entidades do sistema.
Usados para tipagem e transporte de dados entre camadas.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Manifestacao:
    id: Optional[int]
    protocolo: str
    texto_manifestacao: str
    eh_anonimo: bool
    data_registro: datetime
    # Dados do cidadão (None em manifestações anônimas)
    nome_cidadao: Optional[str] = None
    email_cidadao: Optional[str] = None
    cpf_cidadao: Optional[str] = None
    telefone_cidadao: Optional[str] = None
    # Classificação
    categoria: str = "Reclamação"
    assunto: Optional[str] = None
    setor: Optional[str] = None
    # Gestão
    status: str = "Recebida"
    resposta_gestor: Optional[str] = None
    parecer_encerramento: Optional[str] = None
    responsavel_id: Optional[int] = None
    data_atualizacao: Optional[datetime] = None
    data_encerramento: Optional[datetime] = None


@dataclass
class HistoricoStatus:
    id: Optional[int]
    manifestacao_id: int
    status_novo: str
    data_alteracao: datetime
    status_anterior: Optional[str] = None
    observacao: Optional[str] = None
    usuario_id: Optional[int] = None


@dataclass
class Anexo:
    id: Optional[int]
    manifestacao_id: int
    nome_original: str
    nome_armazenado: str
    data_upload: datetime
    mime_type: Optional[str] = None
    tamanho_bytes: Optional[int] = None


@dataclass
class UsuarioInterno:
    id: Optional[int]
    username: str
    nome_completo: str
    email: str
    senha_hash: str
    perfil: str
    data_criacao: datetime
    ativo: bool = True
    ultimo_login: Optional[datetime] = None
    totp_secret: Optional[str] = None


@dataclass
class Categoria:
    id: Optional[int]
    nome: str
    ativo: bool = True


@dataclass
class Auditoria:
    id: Optional[int]
    acao: str
    data_acao: datetime
    usuario_id: Optional[int] = None
    entidade: Optional[str] = None
    entidade_id: Optional[int] = None
    detalhes: Optional[str] = None
