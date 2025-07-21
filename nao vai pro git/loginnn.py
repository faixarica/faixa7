import streamlit as st

# Zera layout
st.set_page_config(page_title="FaixaBet", layout="centered")
# CSS global
st.markdown("""
<style>
/* Centralizar tudo */
div.block-container {
    padding-top: 3rem;
    display: flex;
    flex-direction: column;
    align-items: center;
}

/* Título ajustado para mesma largura */
.login-title {
    font-size: 40px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
    color: #0d730d;
    width: 50ch;
    max-width: 60%;
}

/* Radio ativo */
label[data-baseweb="radio"] > div[aria-checked="true"] {
    background-color: #00C853 !important;
    border-color: #00C853 !important;
}

/* Hover no radio */
label[data-baseweb="radio"]:hover > div {
    border-color: #00C853 !important;
}

/* Texto do radio */
label[data-baseweb="radio"] {
    font-size: 45px !important;
    color: #0d730d !important;
    font-weight: 700;
}

/* Inputs e botões com largura unificada */
div[data-testid="stTextInput"], 
div[data-testid="stPassword"], 
div.stButton {
    width: 50ch !important;
    max-width: 60%;
    margin-top: 8px;
}

/* Link recuperar senha */
a.recover {
    font-size: 12px;
    color: #0055FF;
    display: block;
    text-align: center;
    margin-top: 10px;
    text-decoration: none;
}

</style>
""", unsafe_allow_html=True)

# Sessão de autenticação
if not st.session_state.get("logged_in", False):

    st.markdown('<div class="login-title">Bem-vindo à FaixaBet</div>', unsafe_allow_html=True)

    aba = st.radio("", ["Login", "Cadastro"], horizontal=True)

    st.write("")  # espaçamento

    if aba == "Login":
        usuario = st.text_input("Usuário", max_chars=60)
        senha = st.text_input("Senha", type="password", max_chars=60)
        if st.button("Entrar"):
            st.success(f"Tentando login para {usuario}")
        st.markdown('<a class="recover" href="#">Esqueceu a senha?</a>', unsafe_allow_html=True)

    elif aba == "Cadastro":
        nome = st.text_input("Nome Completo*", max_chars=60)
        email = st.text_input("Email*", max_chars=60)
        telefone = st.text_input("Telefone", max_chars=20)
        cidade = st.text_input("Cidade - Estado", max_chars=40)
        senha = st.text_input("Senha*", type="password", max_chars=20)
        confirmar = st.text_input("Confirme a Senha*", type="password", max_chars=20)
        if st.button("Cadastrar"):
            st.success(f"Cadastro de {nome} realizado com sucesso!")
        st.markdown('<a class="recover" href="#">← Voltar ao Login</a>', unsafe_allow_html=True)

    st.stop()
