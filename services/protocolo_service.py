"""
services/protocolo_service.py
Geração de protocolo único e imutável para manifestações.
RF05 — Protocolo único gerado e exibido ao cidadão.
"""

import uuid
from datetime import datetime
from config.settings import PROTOCOL_PREFIX


def gerar_protocolo() -> str:
    """
    Gera um número de protocolo único no formato:
        OUT-AAAAMMDDHHMMSS-XXXXXXXX

    Onde:
    - OUT     = prefixo fixo (configurável em settings.py)
    - timestamp = data e hora no momento da submissão
    - hex     = 8 caracteres hexadecimais aleatórios (UUID4)

    Probabilidade de colisão: astronomicamente baixa.
    A constraint UNIQUE no banco garante a unicidade em nível de dados.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    aleatorio = uuid.uuid4().hex[:8].upper()
    return f"{PROTOCOL_PREFIX}-{timestamp}-{aleatorio}"
