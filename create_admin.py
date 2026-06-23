"""
create_admin.py
Script para criar o usuário administrador inicial do sistema.
Execute: python create_admin.py

Cria um usuário admin com credenciais padrão:
  username: admin
  senha: admin123

IMPORTANTE: Altere a senha imediatamente após o primeiro login!
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.migrations import run_migrations
from repositories import usuario_repo
from services.auth_service import hash_senha


def criar_admin_inicial():
    print("=== Sistema de Ouvidoria — Criação do Admin Inicial ===\n")

    # Garante que o banco está inicializado
    print("Inicializando banco de dados...")
    run_migrations()
    print("✅ Banco de dados inicializado.\n")

    # Verifica se já existe um admin
    if usuario_repo.username_existe("admin"):
        print("⚠️  Usuário 'admin' já existe. Nada foi alterado.")
        print("   Use a interface administrativa para gerenciar usuários.")
        return

    # Cria o admin
    usuario_repo.criar_usuario({
        "username": "admin",
        "nome_completo": "Administrador do Sistema",
        "email": "admin@ouvidoria.local",
        "senha_hash": hash_senha("admin123"),
        "perfil": "admin",
    })

    print("✅ Usuário administrador criado com sucesso!\n")
    print("   Username: admin")
    print("   Senha:    admin123")
    print("   Perfil:   Administrador\n")
    print("⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
    print("   Acesse a área administrativa > 👥 Usuários para gerenciar.\n")

    # Cria também um usuário atendente de exemplo
    if not usuario_repo.username_existe("atendente"):
        usuario_repo.criar_usuario({
            "username": "atendente",
            "nome_completo": "Atendente Demo",
            "email": "atendente@ouvidoria.local",
            "senha_hash": hash_senha("atendente123"),
            "perfil": "atendente",
        })
        print("✅ Usuário atendente de exemplo criado.")
        print("   Username: atendente")
        print("   Senha:    atendente123")
        print("   Perfil:   Atendente\n")

    print("Para iniciar o sistema, execute:")
    print("  streamlit run app.py")


if __name__ == "__main__":
    criar_admin_inicial()
