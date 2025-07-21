import streamlit as st
import sqlite3
from datetime import datetime, timedelta

def exibir_aba_financeiro():
    if 'usuario' not in st.session_state or st.session_state.usuario is None:
        st.error("Você precisa estar logado.")
        return

    user = st.session_state.usuario
    user_id = user['id']
    plano_id = user['id_plano']

    # 🔁 Carrega planos diretamente do banco (inclui qtde_palpites)
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, valor, palpites_dia, loteria FROM planos")
    planos_raw = cursor.fetchall()
    conn.close()

    # 🔁 Converte para dicionários por ID
    planos = {p[0]: {"nome": p[1], "valor": p[2], "palpites": p[3],"loteria": p[4]} for p in planos_raw}

    plano_atual = planos.get(plano_id, {"nome": "Desconhecido", "valor": 0, "palpites": 0,"loteria":"Desconhecido"})

    # ✅ CARD: Dados do plano atual
    st.subheader("💰 Informações Financeiras")

    st.markdown(f"""
    <div style="background-color:#f3f3f3; padding: 20px; border-radius: 12px; border: 1px solid #ccc">
        <h4 style="margin: 0 0 10px 0;"><b>Plano Atual:</b> {plano_atual["nome"]}</h4>
        <p style="margin: 0;"><b>- Valor Mensal :</b> R$ {plano_atual["valor"]:.2f}</p>
        <p style="margin: 0;"><b>- Palpites Disponíveis/mês:</b> {plano_atual["palpites"]}</p>
        <p style="margin: 0;"><b>- Loteria :</b> {plano_atual["loteria"]}</p>

    </div>
    """, unsafe_allow_html=True)

    # 🔁 Últimos pagamentos
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT data_pagamento, forma_pagamento, valor, data_validade, id_plano 
        FROM financeiro 
        WHERE id_cliente = ? 
        ORDER BY data_pagamento DESC 
        LIMIT 5
    ''', (user_id,))
    registros = cursor.fetchall()
    conn.close()

    if registros:
        st.markdown("### 📄 Últimos Pagamentos")
        for row in registros:
            data_pgto, forma, valor, validade, plano_pgto = row
            nome_plano = planos.get(plano_pgto, {}).get("nome", "Desconhecido")
            st.write(f"- [{data_pgto}] {nome_plano} - R$ {valor:.2f} via {forma} | válido até {validade}")
    else:
        st.info("Nenhum Pagamento Registrado Ainda.")

    st.markdown("---")
    st.markdown("### 🔄 Simular Novo Plano e Pagamento")

    nomes_planos = [planos[p]["nome"] for p in planos]
    nome_to_id = {planos[p]["nome"]: p for p in planos}

    novo_plano_nome = st.selectbox("Escolha um Novo Plano", nomes_planos)
    forma_pagamento = st.selectbox("Forma de Pagamento", ["Cartão", "Débito", "Pix"])

    if st.button("Confirmar Simulação de Pagamento"):
        novo_id = nome_to_id[novo_plano_nome]
        novo_valor = planos[novo_id]["valor"]
        hoje = datetime.now()
        validade = hoje + timedelta(days=30)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO financeiro (id_cliente, id_plano, data_pagamento, forma_pagamento, valor, data_validade)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id, novo_id,
            hoje.strftime("%Y-%m-%d %H:%M:%S"),
            forma_pagamento,
            novo_valor,
            validade.strftime("%Y-%m-%d")
        ))

        cursor.execute('''
            UPDATE usuarios SET id_plano = ? WHERE id = ?
        ''', (novo_id, user_id))

        conn.commit()
        conn.close()

        st.session_state.usuario['id_plano'] = novo_id
        st.success(f"Pagamento do Plano {novo_plano_nome} Registrado Com Sucesso!")
        st.rerun()

    st.markdown("---")
    st.markdown("### ❌ Cancelar Plano Pago")

    if plano_id != 1:
        if st.button("Cancelar Plano e Voltar para o FREE"):
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET id_plano = 1 WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()

            st.session_state.usuario['id_plano'] = 1
            st.success("Plano Cancelado. Agora Você Está no Plano FREE.")
            st.rerun()
    else:
        st.info("Você já Está no Plano FREE.")
