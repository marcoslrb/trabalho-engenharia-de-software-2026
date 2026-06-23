"""
tests/test_auth.py
Testes de autenticação.
Critério: login seguro com bcrypt.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest


@pytest.fixture(autouse=True)
def banco_temporario(tmp_path, monkeypatch):
    monkeypatch.setattr("config.settings.DATABASE_PATH", str(tmp_path / "test_auth.db"))
    from database.migrations import run_migrations
    run_migrations()
    yield


class TestAuth:
    def _criar_usuario_teste(self):
        from repositories.usuario_repo import criar_usuario
        from services.auth_service import hash_senha
        return criar_usuario({
            "username": "teste_user",
            "nome_completo": "Usuário de Teste",
            "email": "teste@ouvidoria.local",
            "senha_hash": hash_senha("senha_segura_123"),
            "perfil": "atendente",
        })

    def test_hash_senha_diferente_do_original(self):
        """Hash não deve igualar à senha original em texto plano."""
        from services.auth_service import hash_senha
        senha = "minha_senha_123"
        h = hash_senha(senha)
        assert h != senha
        assert len(h) > 0

    def test_verificar_senha_correta(self):
        """Verificação deve retornar True para senha correta."""
        from services.auth_service import hash_senha, verificar_senha
        senha = "senha_123"
        h = hash_senha(senha)
        assert verificar_senha(senha, h) is True

    def test_verificar_senha_incorreta(self):
        """Verificação deve retornar False para senha incorreta."""
        from services.auth_service import hash_senha, verificar_senha
        h = hash_senha("correta")
        assert verificar_senha("incorreta", h) is False

    def test_login_bem_sucedido(self):
        """Login com credenciais corretas deve ter sucesso."""
        self._criar_usuario_teste()
        from services.auth_service import tentar_login
        ok, msg, user = tentar_login("teste_user", "senha_segura_123")
        assert ok is True
        assert user is not None
        assert user["username"] == "teste_user"

    def test_login_senha_errada(self):
        """Login com senha errada deve falhar com mensagem genérica."""
        self._criar_usuario_teste()
        from services.auth_service import tentar_login
        ok, msg, user = tentar_login("teste_user", "senha_errada")
        assert ok is False
        assert user is None
        # Mensagem não deve revelar se é o username ou a senha que está errada
        assert "inválidos" in msg.lower()

    def test_login_usuario_inexistente(self):
        """Login com usuário inexistente deve falhar com mesma mensagem genérica."""
        from services.auth_service import tentar_login
        ok, msg, user = tentar_login("nao_existe", "qualquer_senha")
        assert ok is False
        assert user is None
        assert "inválidos" in msg.lower()

    def test_login_campos_vazios(self):
        """Login com campos vazios deve falhar."""
        from services.auth_service import tentar_login
        ok, msg, user = tentar_login("", "")
        assert ok is False

    def test_dois_hashes_diferentes_para_mesma_senha(self):
        """bcrypt gera salt diferente a cada vez — dois hashes devem ser distintos."""
        from services.auth_service import hash_senha, verificar_senha
        senha = "mesma_senha"
        h1 = hash_senha(senha)
        h2 = hash_senha(senha)
        assert h1 != h2  # salts diferentes
        # Mas ambos devem validar a senha original
        assert verificar_senha(senha, h1) is True
        assert verificar_senha(senha, h2) is True
