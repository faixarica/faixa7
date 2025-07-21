import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
from database import carregar_planos
from passlib.hash import pbkdf2_sha256

def hash_senha(senha: str, salt: str = "faixabet_salt") -> str:
    return hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), 100000).hex()

def editar_perfil():
    st.markdown("<div style='text-align:right; color:green; font-size:10px;'><strong>FaixaBet v7.001</strong></div>", unsafe_allow_html=True)

    if 'usuario' not in st.session_state or st.session_state.usuario is None:
        st.error("Você Precisa eEtar Logado.")
        return

    usuario = st.session_state.usuario
    user_id = usuario['id']

    # Buscar dados do usuário
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT usuario, nome_completo, email, telefone, data_nascimento, id_plano FROM usuarios WHERE id = ?", (user_id,))
    dados = cursor.fetchone()
    conn.close()

    if not dados:
        st.error("Usuário NÃO Encontrado.")
        return

    usuario_atual, nome_atual, email_atual, telefone_atual, nascimento_atual, plano_atual_id = dados

    planos = carregar_planos()

    st.subheader("👤 Editar Dados Pessoais")
    nome_usuario = st.text_input("Nome de Usuário", value=usuario_atual)
    nome = st.text_input("Nome completo", value=nome_atual)
    email = st.text_input("Email", value=email_atual)
    telefone = st.text_input("Telefone", value=telefone_atual)
    nascimento = st.date_input("Data de nascimento", value=datetime.strptime(nascimento_atual, "%Y-%m-%d").date())

    st.markdown("---")

    st.subheader("🔒 Alterar Senha")
    nova_senha = st.text_input("Nova Senha", type="password")
    confirmar_senha = st.text_input("Confirmar Nova Senha", type="password")

    if st.button("Salvar Alterações"):
        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            # Verifica se o nome de usuário já está em uso por outro
            cursor.execute("SELECT id FROM usuarios WHERE usuario = ? AND id != ?", (nome_usuario, user_id))
            if cursor.fetchone():
                st.warning("Nome de usuário já está em uso por outro usuário.")
                return

            # Atualizar dados pessoais
            cursor.execute("""
                UPDATE usuarios 
                SET usuario = ?, nome_completo = ?, email = ?, telefone = ?, data_nascimento = ?
                WHERE id = ?
            """, (nome_usuario, nome, email, telefone, str(nascimento), user_id))

            # Atualizar senha se preenchida
            if nova_senha.strip():
                if nova_senha == confirmar_senha:
                    senha_hash = pbkdf2_sha256.hash(nova_senha)
                    cursor.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (senha_hash, user_id))
                    st.success("Senha Atualizada com Sucesso!")
                else:
                    st.warning("As Senhas NÃO coincidem. A Senha NÃO foi Alterada.")

            conn.commit()
            st.success("Perfil Atualizado com Sucesso!")

        except Exception as e:
            conn.rollback()
            st.error(f"Erro ao Atualizar Perfil: {e}")
        finally:
            conn.close()
