"""
tests/test_anexos.py
Testes de upload e validação de arquivos.
Critérios: limite de quantidade (5), limite de tamanho (10MB), extensões bloqueadas.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import MagicMock
from services.anexo_service import validar_arquivo, validar_lista_arquivos
from config.settings import MAX_FILES_PER_MANIFESTACAO, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB


def mock_file(nome: str, tamanho: int = 1024, mime: str = "application/pdf"):
    """Cria um mock de UploadedFile do Streamlit."""
    f = MagicMock()
    f.name = nome
    f.size = tamanho
    f.type = mime
    return f


class TestValidacaoArquivo:
    def test_arquivo_valido_pdf(self):
        arquivo = mock_file("documento.pdf", 1024 * 100)  # 100 KB
        ok, msg = validar_arquivo(arquivo)
        assert ok is True, f"Esperava válido: {msg}"

    def test_arquivo_valido_jpg(self):
        arquivo = mock_file("foto.jpg", 1024 * 500)  # 500 KB
        ok, msg = validar_arquivo(arquivo)
        assert ok is True

    def test_arquivo_valido_xlsx(self):
        arquivo = mock_file("planilha.xlsx", 1024 * 200)
        ok, msg = validar_arquivo(arquivo)
        assert ok is True

    def test_arquivo_muito_grande(self):
        """Arquivo acima de 10 MB deve ser rejeitado."""
        tamanho = MAX_FILE_SIZE_BYTES + 1
        arquivo = mock_file("enorme.pdf", tamanho)
        ok, msg = validar_arquivo(arquivo)
        assert ok is False
        assert str(MAX_FILE_SIZE_MB) in msg

    def test_extensao_bloqueada_exe(self):
        """Arquivo .exe deve ser sempre bloqueado."""
        arquivo = mock_file("malware.exe", 1024)
        ok, msg = validar_arquivo(arquivo)
        assert ok is False
        assert ".exe" in msg.lower() or "segurança" in msg.lower()

    def test_extensao_bloqueada_bat(self):
        arquivo = mock_file("script.bat", 1024)
        ok, msg = validar_arquivo(arquivo)
        assert ok is False

    def test_extensao_bloqueada_js(self):
        arquivo = mock_file("codigo.js", 100)
        ok, msg = validar_arquivo(arquivo)
        assert ok is False

    def test_extensao_nao_permitida(self):
        """Extensão não listada como permitida deve ser rejeitada."""
        arquivo = mock_file("arquivo.rar", 1024)
        ok, msg = validar_arquivo(arquivo)
        assert ok is False

    def test_arquivo_no_limite_exato_tamanho(self):
        """Arquivo exatamente no limite deve ser aceito."""
        arquivo = mock_file("ok.pdf", MAX_FILE_SIZE_BYTES)
        ok, _ = validar_arquivo(arquivo)
        assert ok is True


class TestValidacaoListaArquivos:
    def test_lista_vazia_valida(self):
        ok, erros = validar_lista_arquivos([])
        assert ok is True
        assert len(erros) == 0

    def test_lista_com_max_arquivos_validos(self):
        """5 arquivos válidos deve ser aceito."""
        arquivos = [mock_file(f"doc{i}.pdf", 1024) for i in range(MAX_FILES_PER_MANIFESTACAO)]
        ok, erros = validar_lista_arquivos(arquivos)
        assert ok is True, f"Erros: {erros}"

    def test_lista_acima_do_limite(self):
        """6 arquivos deve ser rejeitado."""
        arquivos = [mock_file(f"doc{i}.pdf", 1024) for i in range(MAX_FILES_PER_MANIFESTACAO + 1)]
        ok, erros = validar_lista_arquivos(arquivos)
        assert ok is False
        assert any(str(MAX_FILES_PER_MANIFESTACAO) in e for e in erros)

    def test_lista_com_um_invalido(self):
        """Um arquivo inválido na lista deve rejeitar toda a lista."""
        arquivos = [
            mock_file("valido.pdf", 1024),
            mock_file("invalido.exe", 1024),  # inválido
        ]
        ok, erros = validar_lista_arquivos(arquivos)
        assert ok is False
        assert len(erros) >= 1
