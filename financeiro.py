# --- CORREÇÕES NO financeiro.py ---
# Arquivo: financeiro.py

import streamlit as st
import sqlite3
from datetime import datetime, timedelta
# from database import get_db # Se não estiver usando, pode remover

def exibir_aba_financeiro():
    """Função principal que exibe toda a aba financeira."""
    
    # 1. Verificação de login
    if 'usuario' not in st.session_state or st.session_state.usuario is None:
        st.error("Você precisa estar logado.")
        return

    # 2. Definir user_id E plano_id logo no início
    user_id = st.session_state.usuario["id"]
    plano_id = st.session_state.usuario["id_plano"]
    # Se não tiver 'tipo_plano', podemos buscar ou usar o id_plano

    # >>>>>>>>>>>>>>>>> TODO O CÓDIGO RELACIONADO AO FINANCEIRO DEVE ESTAR AQUI DENTRO <<<<<<<<<<<<<<<<<<<
    
    # 3. 🔁 Carrega planos diretamente do banco (inclui qtde_palpites)
    #    Este bloco DEVE estar dentro da função
    conn_temp = sqlite3.connect("database.db")
    cursor_temp = conn_temp.cursor()
    cursor_temp.execute("SELECT id, nome, valor, palpites_dia, loteria FROM planos")
    planos_raw = cursor_temp.fetchall()
    conn_temp.close()

    # 🔁 Converte para dicionários por ID (como no código original)
    # Esta variável 'planos' só existe dentro desta função agora
    planos = {p[0]: {"nome": p[1], "valor": p[2], "palpites": p[3], "loteria": p[4]} for p in planos_raw}
    
    # Se 'planos' estiver vazio, pode haver um problema com o banco
    if not planos:
        st.error("Erro: Não foi possível carregar os planos disponíveis.")
        return

    # 4. Obter informações do plano atual do usuário
    plano_atual = planos.get(plano_id, {"nome": "Desconhecido", "valor": 0, "palpites": 0, "loteria": "Desconhecido"})

    # 5. ✅ CARD: Dados do plano atual
    st.subheader("💰 Informações Financeiras")

    st.markdown(f"""
    <div style="background-color:#f3f3f3; padding: 20px; border-radius: 12px; border: 1px solid #ccc">
        <h4 style="margin: 0 0 10px 0;"><b>Plano Atual:</b> {plano_atual["nome"]}</h4>
        <p style="margin: 0;"><b>- Valor Mensal :</b> R$ {plano_atual["valor"]:.2f}</p>
        <p style="margin: 0;"><b>- Palpites Disponíveis/mês:</b> {plano_atual["palpites"]}</p>
        <p style="margin: 0;"><b>- Loteria :</b> {plano_atual["loteria"]}</p>
    </div>
    """, unsafe_allow_html=True)

    # 6. 🔁 Últimos pagamentos (usando user_id)
    conn_hist = sqlite3.connect("database.db")
    cursor_hist = conn_hist.cursor()
    cursor_hist.execute('''
        SELECT data_pagamento, forma_pagamento, valor, data_validade, id_plano 
        FROM financeiro 
        WHERE id_cliente = ? 
        ORDER BY data_pagamento DESC 
        LIMIT 5
    ''', (user_id,))
    registros = cursor_hist.fetchall()
    conn_hist.close()

    # 7. Exibir últimos pagamentos
    if registros:
        st.markdown("### 📄 Últimos Pagamentos")
        for row in registros:
            data_pgto, forma, valor, validade, plano_pgto_id = row
            # Usa o dicionário 'planos' carregado anteriormente
            nome_plano = planos.get(plano_pgto_id, {}).get("nome", "Desconhecido")
            st.write(f"- [{data_pgto}] {nome_plano} - R$ {valor:.2f} via {forma} | válido até {validade}")
    else:
        st.info("Nenhum Pagamento Registrado Ainda.")

    st.markdown("---")
    st.markdown("### 💳 Simular Novo Plano e Pagamento")

    # --- LÓGICA DE SIMULAÇÃO DE TROCA DE PLANO ---
    # Esta parte também deve estar DENTRO da função
    nomes_planos_disponiveis = [planos[p]["nome"] for p in planos if p != plano_id]
    
    if nomes_planos_disponiveis: # Só mostra se houver outros planos além do atual
        # Recalcula nome_to_id DENTRO da função, onde 'planos' está definido
        nome_to_id = {planos[p]["nome"]: p for p in planos} # Mapeamento nome -> id

        # Usar st.form pode ajudar a isolar a lógica
        with st.form("form_simulacao_plano"):
            novo_plano_nome = st.selectbox("Escolha um Novo Plano", nomes_planos_disponiveis)
            forma_pagamento = st.selectbox("Forma de Pagamento", ["Cartão", "Débito", "Pix"])
            # Botão de submissão do formulário
            submitted = st.form_submit_button("Confirmar Simulação de Pagamento")

        # if st.button("Confirmar Simulação de Pagamento"): # Substituído pelo form_submit_button
        if submitted:
            # Obter ID do novo plano
            # Agora 'nome_to_id' e 'planos' estão definidos neste escopo
            novo_id = nome_to_id[novo_plano_nome] 
            novo_valor = planos[novo_id]["valor"] # Agora 'planos' está definido
            hoje = datetime.now()
            validade = hoje + timedelta(days=30)

            conn_pag = sqlite3.connect("database.db")
            cursor_pag = conn_pag.cursor()

            try:
                # Inserir registro de pagamento simulado
                cursor_pag.execute('''
                    INSERT INTO financeiro (id_cliente, id_plano, data_pagamento, forma_pagamento, valor, data_validade)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, novo_id,
                    hoje.strftime("%Y-%m-%d %H:%M:%S"),
                    forma_pagamento,
                    novo_valor,
                    validade.strftime("%Y-%m-%d")
                ))

                # Atualiza o plano do usuário na tabela 'usuarios'
                cursor_pag.execute('''
                    UPDATE usuarios SET id_plano = ? WHERE id = ?
                ''', (novo_id, user_id))

                # --- CORREÇÃO DA LÓGICA DE DESATIVAÇÃO ---
                cursor_pag.execute('''
                    UPDATE client_plans
                    SET ativo = 0
                    WHERE id_client = ? AND ativo = 1
                ''', (user_id,))

                cursor_pag.execute('''
                    INSERT INTO client_plans (id_client, id_plano, data_inclusao, data_expira_plan, ativo, palpites_dia_usado)
                    VALUES (?, ?, ?, ?, 1, 0)
                ''', (
                    user_id,
                    novo_id,
                    hoje.strftime("%Y-%m-%d %H:%M:%S"),
                    validade.strftime("%Y-%m-%d")
                ))
                # --- FIM DA CORREÇÃO ---

                conn_pag.commit()
                
                # >>>>>>>>>>>>>>>>> ATUALIZAÇÃO CRÍTICA DA SESSION_STATE <<<<<<<<<<<<<<<<<<<
                if 'usuario' in st.session_state and st.session_state.usuario is not None:
                    st.session_state.usuario['id_plano'] = novo_id
                    # Atualiza a variável local também para a exibição imediata
                    plano_id = novo_id
                    # Recarrega o plano_atual com as novas informações
                    plano_atual = planos.get(plano_id, {"nome": "Desconhecido", "valor": 0, "palpites": 0, "loteria": "Desconhecido"})
                    
                    st.success(f"Pagamento do Plano {novo_plano_nome} Registrado Com Sucesso!")
                    st.rerun() # Recarrega para refletir as mudanças imediatamente
                else:
                     st.error("Erro ao atualizar a sessão do usuário.")
                 
            except sqlite3.Error as e:
                conn_pag.rollback()
                st.error(f"Erro ao processar o pagamento: {e}")
            finally:
                conn_pag.close()
                
    else:
        st.info("Não há outros planos disponíveis para compra.")
    # --- FIM DA LÓGICA DE SIMULAÇÃO ---

    st.markdown("---")
    st.markdown("### ❌ Cancelar Plano Pago")

    # 9. Lógica de cancelamento de plano
    if plano_id != 1: 
        if st.button("Cancelar Plano e Voltar para o FREE"):
            conn_cancel = sqlite3.connect("database.db")
            cursor_cancel = conn_cancel.cursor()
            try:
                cursor_cancel.execute("UPDATE usuarios SET id_plano = 1 WHERE id = ?", (user_id,))
                # Opcional: desativar plano ativo em client_plans
                cursor_cancel.execute("UPDATE client_plans SET ativo = 0 WHERE id_client = ? AND ativo = 1", (user_id,))
                conn_cancel.commit()
                
                if 'usuario' in st.session_state and st.session_state.usuario is not None:
                    st.session_state.usuario['id_plano'] = 1
                    plano_id = 1
                    plano_atual = planos.get(plano_id, {"nome": "Desconhecido", "valor": 0, "palpites": 0, "loteria": "Desconhecido"})
                    
                st.success("Plano Cancelado. Agora Você Está no Plano FREE.")
                st.rerun()
                
            except sqlite3.Error as e:
                conn_cancel.rollback()
                st.error(f"Erro ao cancelar o plano: {e}")
            finally:
                conn_cancel.close()
    else:
        st.info("Você já Está no Plano FREE.")

# --- FIM DA FUNÇÃO exibir_aba_financeiro E DO ARQUIVO ---