import streamlit as st

# Aplica o estilo CSS global para simular o "card"
st.markdown("""
    <style>
        .custom-card {
            background-color: rgba(250, 250, 250, 0.9);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
            width: 150%;      /* Ajuste aqui a largura desejada */
            height: 500px;   /* Ajuste aqui a altura desejada */
        }
    </style>
""", unsafe_allow_html=True)

# Cria o card com conteúdo (pode deixar vazio ou colocar info dentro)
st.markdown('<div class="custom-card">Seu conteúdo aqui</div>', unsafe_allow_html=True)
