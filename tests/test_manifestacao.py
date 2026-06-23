"""
tests/test_manifestacao.py
Testes de persistência de manifestações.
Critérios: persistência anônima, bloqueio de dados pessoais, consulta por protocolo.
"""

import sys
import os
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(autouse=True)
def banco_temporario(tmp_path, monkeypatch):
    """Usa banco SQLite temporário para cada teste."""
    db_file = str(tmp_path / "test_ouvidoria.db")
    monkeypatch.setattr("config.settings.DATABASE_PATH", db_file)

    # Reinicializa a importação do módulo de conexão com o novo caminho
    import importlib
    import database.connection
    import database.migrations
    import repositories.manifestacao_repo
    import repositories.historico_repo
    import repositories.anexo_repo

    # Força recriação da conexão com o banco temporário
    from database.migrations import run_migrations
    run_migrations()
    yield


class TestPersistenciaManifestacao:
    def test_inserir_manifestacao_anonima(self):
        """Manifestação anônima deve persistir sem dados pessoais."""
        from repositories.manifestacao_repo import inserir, buscar_por_protocolo
        from services.protocolo_service import gerar_protocolo

        protocolo = gerar_protocolo()
        dados = {
            "protocolo": protocolo,
            "texto_manifestacao": "Teste de manifestação anônima com conteúdo suficiente.",
            "eh_anonimo": True,
            "nome_cidadao": "Tentativa de Nome",  # deve ser bloqueado
            "email_cidadao": "tentativa@email.com",  # deve ser bloqueado
            "cpf_cidadao": "11144477735",  # deve ser bloqueado
            "categoria": "Denúncia",
            "assunto": "Teste anônimo",
        }
        inserir(dados)

        resultado = buscar_por_protocolo(protocolo)
        assert resultado is not None
        assert resultado["protocolo"] == protocolo
        # Dados pessoais devem ser NULL
        assert resultado["nome_cidadao"] is None, "Nome não deve ser armazenado em anônima"
        assert resultado["email_cidadao"] is None, "E-mail não deve ser armazenado em anônima"
        assert resultado["cpf_cidadao"] is None, "CPF não deve ser armazenado em anônima"

    def test_inserir_manifestacao_identificada(self):
        """Manifestação identificada deve persistir com dados pessoais."""
        from repositories.manifestacao_repo import inserir, buscar_por_protocolo
        from services.protocolo_service import gerar_protocolo

        protocolo = gerar_protocolo()
        dados = {
            "protocolo": protocolo,
            "texto_manifestacao": "Teste de manifestação identificada com conteúdo.",
            "eh_anonimo": False,
            "nome_cidadao": "João da Silva",
            "email_cidadao": "joao@email.com",
            "cpf_cidadao": "11144477735",
            "categoria": "Reclamação",
            "assunto": "Teste identificado",
        }
        inserir(dados)

        resultado = buscar_por_protocolo(protocolo)
        assert resultado is not None
        assert resultado["nome_cidadao"] == "João da Silva"
        assert resultado["email_cidadao"] == "joao@email.com"

    def test_consulta_por_protocolo_inexistente(self):
        """Consulta com protocolo inválido deve retornar None."""
        from services.manifestacao_service import consultar_manifestacao
        resultado = consultar_manifestacao("OUT-INVALIDO-XXXX")
        assert resultado is None

    def test_consulta_por_protocolo_existente(self):
        """Consulta com protocolo válido deve retornar dados corretos."""
        from repositories.manifestacao_repo import inserir
        from services.manifestacao_service import consultar_manifestacao
        from services.protocolo_service import gerar_protocolo

        protocolo = gerar_protocolo()
        inserir({
            "protocolo": protocolo,
            "texto_manifestacao": "Manifestação para teste de consulta pública.",
            "eh_anonimo": True,
            "categoria": "Sugestão",
            "assunto": "Consulta teste",
        })

        resultado = consultar_manifestacao(protocolo)
        assert resultado is not None
        assert resultado["protocolo"] == protocolo
        assert resultado["status"] == "Recebida"

    def test_dados_pessoais_nao_vazam_em_consulta_publica_anonima(self):
        """A consulta pública não deve expor dados pessoais de anônimas."""
        from repositories.manifestacao_repo import inserir
        from services.manifestacao_service import consultar_manifestacao
        from services.protocolo_service import gerar_protocolo

        protocolo = gerar_protocolo()
        inserir({
            "protocolo": protocolo,
            "texto_manifestacao": "Manifestação anônima para teste de vazamento.",
            "eh_anonimo": True,
            "nome_cidadao": None,
            "email_cidadao": None,
            "cpf_cidadao": None,
            "categoria": "Denúncia",
            "assunto": "Teste vazamento",
        })

        resultado = consultar_manifestacao(protocolo)
        assert resultado is not None
        assert "cpf_cidadao" not in resultado, "CPF não deve aparecer na consulta pública"
        assert resultado.get("email_cidadao") is None
        assert resultado.get("nome_cidadao") is None

    def test_encerramento_requer_parecer(self):
        """Encerramento sem parecer deve retornar erro."""
        from repositories.manifestacao_repo import inserir
        from services.manifestacao_service import atualizar_status_manifestacao
        from services.protocolo_service import gerar_protocolo

        protocolo = gerar_protocolo()
        mid = inserir({
            "protocolo": protocolo,
            "texto_manifestacao": "Manifestação para teste de encerramento.",
            "eh_anonimo": True,
            "categoria": "Reclamação",
            "assunto": "Encerramento",
        })

        ok, msg = atualizar_status_manifestacao(
            manifestacao_id=mid,
            status_novo="Concluída",
            observacao="Testando",
            resposta_gestor=None,
            parecer_encerramento="",  # vazio = deve falhar
            setor=None,
            usuario_id=None,
        )
        assert ok is False
        assert "parecer" in msg.lower()
