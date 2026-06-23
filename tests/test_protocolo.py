"""
tests/test_protocolo.py
Testes de geração de protocolo único.
Critério de aceite: geração de protocolo único e imutável.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import re
import pytest
from services.protocolo_service import gerar_protocolo
from config.settings import PROTOCOL_PREFIX


class TestGerarProtocolo:
    def test_formato_correto(self):
        """Protocolo deve seguir o padrão OUT-AAAAMMDDHHMMSS-XXXXXXXX."""
        protocolo = gerar_protocolo()
        pattern = rf"^{PROTOCOL_PREFIX}-\d{{14}}-[A-F0-9]{{8}}$"
        assert re.match(pattern, protocolo), f"Formato inválido: {protocolo}"

    def test_prefixo_correto(self):
        protocolo = gerar_protocolo()
        assert protocolo.startswith(PROTOCOL_PREFIX + "-")

    def test_unicidade(self):
        """Gera 1000 protocolos e verifica que todos são únicos."""
        protocolos = {gerar_protocolo() for _ in range(1000)}
        assert len(protocolos) == 1000, "Colisão detectada na geração de protocolos!"

    def test_protocolo_nao_vazio(self):
        protocolo = gerar_protocolo()
        assert protocolo is not None
        assert len(protocolo) > 0

    def test_protocolo_e_string(self):
        protocolo = gerar_protocolo()
        assert isinstance(protocolo, str)

    def test_protocolo_apenas_maiusculas_e_hifens(self):
        """Protocolo deve conter apenas uppercase, dígitos e hífens."""
        protocolo = gerar_protocolo()
        assert re.match(r"^[A-Z0-9\-]+$", protocolo)
