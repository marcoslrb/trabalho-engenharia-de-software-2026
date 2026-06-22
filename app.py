import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import uuid
import os

# Configuração da página Streamlit
st.set_page_config(
    page_title="Sistema de Ouvidoria",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS customizado
st.markdown("""
    <style>
    .header {
        color: #1f77b4;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .protocol-box {
        background-color: #e7f3ff;
        border-left: 4px solid #1f77b4;
        padding: 15px;
        margin: 15px 0;
        border-radius: 5px;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        margin: 15px 0;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# ========== CONFIGURAÇÃO DO BANCO DE DADOS ==========
DATABASE_PATH = "ouvidoria.db"

def initialize_database():
    """Inicializa o banco de dados SQLite com a tabela de manifestações"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS manifestacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            protocolo TEXT UNIQUE NOT NULL,
            texto_manifestacao TEXT NOT NULL,
            eh_anonimo BOOLEAN NOT NULL,
            data_registro TIMESTAMP NOT NULL,
            nome_cidadao TEXT,
            email_cidadao TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def gerar_protocolo():
    """Gera um número de protocolo único"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    aleatorio = str(uuid.uuid4().hex[:8]).upper()
    protocolo = f"OUT-{timestamp}-{aleatorio}"
    return protocolo

def salvar_manifestacao(protocolo, texto, eh_anonimo, nome=None, email=None):
    """Salva uma manifestação no banco de dados"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO manifestacoes 
            (protocolo, texto_manifestacao, eh_anonimo, data_registro, nome_cidadao, email_cidadao)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (protocolo, texto, eh_anonimo, datetime.now(), nome, email))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar manifestação: {e}")
        return False

def obter_manifestacoes():
    """Recupera todas as manifestações do banco de dados"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT protocolo, texto_manifestacao, eh_anonimo, data_registro, nome_cidadao, email_cidadao
            FROM manifestacoes
            ORDER BY data_registro DESC
        ''')
        
        resultados = cursor.fetchall()
        conn.close()
        return resultados
    except Exception as e:
        st.error(f"Erro ao recuperar manifestações: {e}")
        return []

# ========== INTERFACE DO CIDADÃO ==========
def interface_cidadao():
    """Interface para registro de manifestações pelo cidadão"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="header">📝 Registro de Manifestação</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.write("Bem-vindo ao Sistema de Ouvidoria. Utilize este formulário para registrar sua manifestação.")
    
    with st.form("form_manifestacao"):
        st.subheader("Dados da Manifestação")
        
        # Campo para texto da manifestação
        texto_manifestacao = st.text_area(
            "Descreva sua manifestação (denúncia, sugestão, reclamação, etc.):",
            placeholder="Digite aqui o texto de sua manifestação...",
            height=150,
            max_chars=5000
        )
        
        st.markdown("---")
        st.subheader("Informações Adicionais")
        
        # Opção de anonimato
        eh_anonimo = st.checkbox(
            "Desejo manter minha manifestação anônima",
            value=False,
            help="Se marcado, sua manifestação será registrada sem identificação pessoal"
        )
        
        # Dados do cidadão (opcional se não for anônimo)
        if not eh_anonimo:
            col1, col2 = st.columns(2)
            with col1:
                nome_cidadao = st.text_input("Seu nome (opcional):")
            with col2:
                email_cidadao = st.text_input("Seu email (opcional):")
        else:
            nome_cidadao = None
            email_cidadao = None
        
        st.markdown("---")
        
        # Botão de submissão
        submitted = st.form_submit_button(
            "✅ Registrar Manifestação",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if not texto_manifestacao.strip():
                st.error("❌ Por favor, descreva sua manifestação.")
            else:
                # Gerar protocolo e salvar
                protocolo = gerar_protocolo()
                sucesso = salvar_manifestacao(
                    protocolo=protocolo,
                    texto=texto_manifestacao,
                    eh_anonimo=eh_anonimo,
                    nome=nome_cidadao if nome_cidadao else None,
                    email=email_cidadao if email_cidadao else None
                )
                
                if sucesso:
                    st.markdown(f'''
                    <div class="success-box">
                    <h3>✅ Manifestação Registrada com Sucesso!</h3>
                    <p><strong>Seu número de protocolo:</strong></p>
                    <h2 style="color: #28a745; font-family: monospace;">{protocolo}</h2>
                    <p><em>Guarde este número para referência futura. Você poderá utilizá-lo para acompanhar sua manifestação.</em></p>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    st.balloons()
                else:
                    st.error("❌ Erro ao registrar a manifestação. Tente novamente.")

# ========== INTERFACE DO GESTOR ==========
def interface_gestor():
    """Interface de dashboard para o gestor/analista"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="header">📊 Painel de Gestão - Denúncias Registradas</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Buscar manifestações
    manifestacoes = obter_manifestacoes()
    
    # Estatísticas
    if manifestacoes:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Manifestações", len(manifestacoes))
        
        with col2:
            anonimas = sum(1 for m in manifestacoes if m[2])
            st.metric("Denúncias Anônimas", anonimas)
        
        with col3:
            identificadas = sum(1 for m in manifestacoes if not m[2])
            st.metric("Denúncias Identificadas", identificadas)
        
        with col4:
            st.metric("Taxa de Anonimato", f"{(anonimas/len(manifestacoes)*100):.1f}%")
        
        st.markdown("---")
        st.subheader("📋 Listagem de Manifestações")
        
        # Opções de filtro
        col1, col2 = st.columns(2)
        with col1:
            filtro_anonimo = st.selectbox(
                "Filtrar por tipo:",
                ["Todas", "Apenas Anônimas", "Apenas Identificadas"]
            )
        
        # Aplicar filtro
        if filtro_anonimo == "Apenas Anônimas":
            manifestacoes_filtradas = [m for m in manifestacoes if m[2]]
        elif filtro_anonimo == "Apenas Identificadas":
            manifestacoes_filtradas = [m for m in manifestacoes if not m[2]]
        else:
            manifestacoes_filtradas = manifestacoes
        
        # Exibir manifestações em cards
        if manifestacoes_filtradas:
            for idx, manifestacao in enumerate(manifestacoes_filtradas, 1):
                protocolo, texto, eh_anonimo, data_registro, nome, email = manifestacao
                
                # Formatar data
                try:
                    data_obj = datetime.strptime(data_registro, "%Y-%m-%d %H:%M:%S.%f")
                except:
                    data_obj = datetime.strptime(data_registro, "%Y-%m-%d %H:%M:%S")
                data_formatada = data_obj.strftime("%d/%m/%Y às %H:%M")
                
                with st.expander(f"📌 {protocolo} - {data_formatada}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write("**Texto da Manifestação:**")
                        st.write(texto)
                    
                    with col2:
                        status_anonimato = "🔒 Anônimo" if eh_anonimo else "👤 Identificado"
                        st.write(f"**Status:** {status_anonimato}")
                    
                    if not eh_anonimo:
                        col1, col2 = st.columns(2)
                        with col1:
                            if nome:
                                st.write(f"**Nome:** {nome}")
                        with col2:
                            if email:
                                st.write(f"**Email:** {email}")
                    
                    # Divider
                    st.divider()
        else:
            st.info("Nenhuma manifestação encontrada com os filtros aplicados.")
    else:
        st.info("📭 Nenhuma manifestação registrada até o momento.")

# ========== APLICAÇÃO PRINCIPAL ==========
def main():
    """Função principal da aplicação"""
    # Inicializar banco de dados
    initialize_database()
    
    # Sidebar - Seleção de tipo de usuário
    st.sidebar.markdown("## 👥 Seleção de Perfil")
    st.sidebar.markdown("---")
    
    tipo_usuario = st.sidebar.radio(
        "Escolha seu perfil:",
        ["Cidadão", "Gestor/Analista"],
        index=0,
        help="Selecione o tipo de usuário para acessar a interface apropriada"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Informações")
    st.sidebar.write("""
    **Sistema de Ouvidoria**
    
    - **Cidadão**: Registre suas manifestações
    - **Gestor**: Acompanhe e gerencie as denúncias
    
    Versão: 1.0
    """)
    
    # Exibir interface apropriada
    if tipo_usuario == "Cidadão":
        interface_cidadao()
    else:
        interface_gestor()

if __name__ == "__main__":
    main()
