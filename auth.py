import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
import time

# Função para conectar ao banco de dados
def get_db_connection():
    try:
        conn = sqlite3.connect('database.db', timeout=10)
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        return None

# Função de login
def login():
    st.title("Login")
    
    # Centraliza o formulário usando st.columns
    col1, col2, col3 = st.columns([1, 2, 1])  # Colunas para centralizar
    with col2:
        with st.form("login_form"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            
            if st.form_submit_button("Entrar"):
                conn = get_db_connection()
                if conn is None:
                    return
                
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT id, nome_completo, senha, tipo, id_plano 
                        FROM usuarios 
                        WHERE usuario = ? AND ativo = 1
                    """, (usuario,))
                    
                    user = cursor.fetchone()
                    
                    if user:
                        if pbkdf2_sha256.verify(senha, user[2]):
                            st.session_state.logado = True
                            st.session_state.usuario = {
                                'id': user[0],
                                'nome': user[1],
                                'tipo': user[3],
                                'id_plano': user[4],
                                'usuario': usuario
                            }
                            st.success("Login Realizado Com Sucesso!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Senha incorreta")
                    else:
                        st.error("Usuário NÃO Encontrado ou Conta Inativa")
                        
                except Exception as e:
                    st.error(f"Erro no sistema: {str(e)}")
                finally:
                    conn.close()

# Função de cadastro
def register():
    st.title("Cadastro")
    
    # Centraliza o formulário usando st.columns
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("register_form"):
            nome = st.text_input("Nome Completo *")
            email = st.text_input("Email *")
            usuario = st.text_input("Usuário *")
            senha = st.text_input("Senha *", type="password")
            
            # Adiciona a escolha do plano
            plano = st.selectbox("Escolha seu plano:", ["Free", "Silver", "Gold"], index=0)
            
            if st.form_submit_button("Cadastrar"):
                conn = get_db_connection()
                if conn is None:
                    return
                
                try:
                    cursor = conn.cursor()
                    
                    # Mapeia os planos para IDs correspondentes
                    plano_id_map = {"Free": 1, "Silver": 2, "Gold": 3}
                    id_plano = plano_id_map.get(plano)
                    
                    # Verifica se o usuário ou email já existem
                    cursor.execute("SELECT 1 FROM usuarios WHERE usuario = ? OR email = ?", (usuario, email))
                    if cursor.fetchone():
                        st.error("Usuário ou email já cadastrado")
                    else:
                        senha_hash = pbkdf2_sha256.hash(senha)
                        
                        # Insere o novo usuário com o plano escolhido
                        cursor.execute("""
                            INSERT INTO usuarios (nome_completo, email, usuario, senha, tipo, id_plano, ativo)
                            VALUES (?, ?, ?, ?, 'U', ?, 1)
                        """, (nome, email, usuario, senha_hash, id_plano))
                        
                        # Obtém o ID do usuário recém-criado
                        user_id = cursor.lastrowid
                        
                        # Insere o plano na tabela client_plans
                        cursor.execute("""
                            INSERT INTO client_plans (id_client, id_plano, data_expira_plan)
                            VALUES (?, ?, datetime('now', '+30 days'))
                        """, (user_id, id_plano))
                        
                        conn.commit()
                        st.success("Cadastro Realizado! FAÇA O LOGIN.")
                        time.sleep(1)
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Erro no cadastro: {str(e)}")
                finally:
                    conn.close()

# Função de logout
def logout():
    st.session_state.logged_in = False
    st.session_state.usuario = None
    st.success("Logout Realizado Com Sucesso.")
    st.rerun()  # Use isso se estiver usando Streamlit >= 1.32