"""
tests/test_validators.py
Testes unitários de validação de CPF e e-mail.
Cobre os critérios de aceite: validação de CPF e validação de e-mail.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from utils.validators import (
    validar_cpf, validar_email, validar_texto_manifestacao,
    validar_nome, formatar_cpf, mascarar_cpf,
)


# ── Testes de CPF ──────────────────────────────────────────────────────────────

class TestValidarCPF:
    def test_cpf_valido_sem_mascara(self):
        ok, msg = validar_cpf("11144477735")
        assert ok is True, f"Esperava CPF válido, mas: {msg}"

    def test_cpf_valido_com_mascara(self):
        ok, msg = validar_cpf("111.444.777-35")
        assert ok is True, f"Esperava CPF válido, mas: {msg}"

    def test_cpf_invalido_digito_verificador(self):
        ok, msg = validar_cpf("11144477736")
        assert ok is False
        assert "inválido" in msg.lower()

    def test_cpf_todos_digitos_iguais(self):
        for d in "0123456789":
            ok, msg = validar_cpf(d * 11)
            assert ok is False, f"CPF {d*11} deveria ser inválido"

    def test_cpf_tamanho_errado(self):
        ok, msg = validar_cpf("1234567890")  # 10 dígitos
        assert ok is False
        assert "11 dígitos" in msg

    def test_cpf_vazio(self):
        ok, msg = validar_cpf("")
        assert ok is False
        assert "obrigatório" in msg.lower()

    def test_cpf_none(self):
        ok, msg = validar_cpf(None)
        assert ok is False

    def test_formatar_cpf(self):
        resultado = formatar_cpf("11144477735")
        assert resultado == "111.444.777-35"

    def test_mascarar_cpf(self):
        resultado = mascarar_cpf("11144477735")
        assert "***" in resultado
        assert "35" in resultado

    def test_cpf_com_espacos(self):
        ok, msg = validar_cpf("111.444.777-35")
        assert ok is True


# ── Testes de E-mail ───────────────────────────────────────────────────────────

class TestValidarEmail:
    def test_email_valido(self):
        ok, _ = validar_email("usuario@exemplo.com")
        assert ok is True

    def test_email_valido_subdominio(self):
        ok, _ = validar_email("user@mail.dominio.gov.br")
        assert ok is True

    def test_email_sem_arroba(self):
        ok, msg = validar_email("usuarioemail.com")
        assert ok is False
        assert "inválido" in msg.lower()

    def test_email_sem_dominio(self):
        ok, msg = validar_email("usuario@")
        assert ok is False

    def test_email_vazio(self):
        ok, msg = validar_email("")
        assert ok is False
        assert "obrigatório" in msg.lower()

    def test_email_muito_longo(self):
        ok, msg = validar_email("a" * 250 + "@x.com")
        assert ok is False

    def test_email_com_espacos_valido(self):
        # Trim deve tratar espaços
        ok, _ = validar_email("  user@exemplo.com  ")
        assert ok is True


# ── Testes de Texto de Manifestação ───────────────────────────────────────────

class TestValidarTextoManifestacao:
    def test_texto_valido(self):
        ok, _ = validar_texto_manifestacao("Este é um texto de manifestação com mais de 20 caracteres.")
        assert ok is True

    def test_texto_muito_curto(self):
        ok, msg = validar_texto_manifestacao("Curto demais")
        assert ok is False
        assert "pelo menos" in msg.lower()

    def test_texto_vazio(self):
        ok, msg = validar_texto_manifestacao("")
        assert ok is False
        assert "vazia" in msg.lower()

    def test_texto_apenas_espacos(self):
        ok, msg = validar_texto_manifestacao("   ")
        assert ok is False

    def test_texto_muito_longo(self):
        ok, msg = validar_texto_manifestacao("a" * 5001)
        assert ok is False
        assert "5000" in msg
