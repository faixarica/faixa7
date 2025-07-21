import streamlit as st

def main():
    # Configuração básica da página
    st.set_page_config(
        page_title="FaixaBet",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # CSS minimalista e eficiente
    st.markdown("""
    <style>
        /* Container principal centralizado */
        .main-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
            background: #f5f7fa;
        }
        
        /* Card único e bem posicionado */
        .auth-card {
            width: 100%;
            max-width: 340px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            padding: 25px;
            margin: 0 auto;
        }
        
        /* Melhorias nos inputs */
        .stTextInput input, 
        .stPassword input {
            padding: 10px 12px !important;
            border-radius: 6px !important;
        }
        
        /* Botões consistentes */
        .stButton button {
            width: 100% !important;
            padding: 10px !important;
            background: #066a75 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Controle de estado simplificado
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False

    # Estrutura única e bem organizada
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)
    
    # Card principal único
    with st.container():
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        
        if not st.session_state.show_register:
            # Formulário de Login
            st.header("Login")
            with st.form("login_form"):
                email = st.text_input("E-mail", placeholder="seu@email.com")
                senha = st.text_input("Senha", type="password", placeholder="••••••••")
                
                if st.form_submit_button("Entrar"):
                    if email and senha:
                        st.success("Login realizado com sucesso!")
                    else:
                        st.error("Por favor, preencha todos os campos")
            
            if st.button("Cadastre-se"):
                st.session_state.show_register = True
                st.rerun()
        
        else:
            # Formulário de Cadastro
            st.header("Cadastro")
            with st.form("register_form"):
                nome = st.text_input("Nome completo", placeholder="Seu nome completo")
                email = st.text_input("E-mail", placeholder="seu@email.com")
                senha = st.text_input("Senha", type="password", placeholder="••••••••")
                
                if st.form_submit_button("Cadastrar"):
                    if nome and email and senha:
                        st.success("Cadastro realizado com sucesso!")
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error("Por favor, preencha todos os campos")
            
            if st.button("Voltar para Login"):
                st.session_state.show_register = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()