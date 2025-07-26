import streamlit as st
import random
from datetime import datetime
from database import get_db
import pyperclip 
import os
import sqlite3
import numpy as np

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    # Função para verificar o limite de palpites
def verificar_limite_palpites(id_usuario):
    conn = get_db()
    cursor = conn.cursor()

    # Obtém dados do plano atual do usuário
    cursor.execute("""
        SELECT p.palpites_dia, p.limite_palpites_mes, p.nome
        FROM usuarios u
        JOIN planos p ON u.id_plano = p.id
        WHERE u.id = ?
    """, (id_usuario,))
    resultado = cursor.fetchone()

    if not resultado:
        conn.close()
        return False, "Plano não encontrado", 0

    palpites_dia, limite_mes, nome_plano = resultado

    # Conta quantos palpites foram feitos hoje
    cursor.execute("""
        SELECT COUNT(*) FROM palpites
        WHERE id_usuario = ? AND DATE(data) = DATE('now')
    """, (id_usuario,))
    usados_dia = cursor.fetchone()[0]

    # Conta quantos palpites foram feitos no mês atual
    cursor.execute("""
        SELECT COUNT(*) FROM palpites
        WHERE id_usuario = ? AND strftime('%Y-%m', data) = strftime('%Y-%m', 'now')
    """, (id_usuario,))
    usados_mes = cursor.fetchone()[0]

    conn.close()

    if usados_dia >= palpites_dia:
        return False, nome_plano, 0

    if usados_mes >= limite_mes:
        return False, nome_plano, 0

    palpites_restantes_mes = limite_mes - usados_mes
    return True, nome_plano, palpites_restantes_mes

def obter_limite_dezenas_por_plano(tipo_plano):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT limite_dezenas FROM planos WHERE nome = ?", (tipo_plano,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else 15  # fallback padrão

# Função para atualizar o contador de palpites
def atualizar_contador_palpites(id_usuario):

    conn = get_db()
    cursor = conn.cursor()
    
    # Busca o ID do plano mais recente
    cursor.execute("""
        SELECT id FROM client_plans
        WHERE id_client = ?
        ORDER BY data_inclusao DESC
        LIMIT 1
    """, (id_usuario,))
    plan_id = cursor.fetchone()[0]
    resultado = cursor.fetchone()
    if resultado is None:
        conn.close()
        raise ValueError(f"Nenhum plano encontrado para o usuário {id_usuario}")
    plan_id = resultado[0]

    
    # Atualiza o contador de palpites
    cursor.execute("""
        UPDATE client_plans
        SET palpites_dia_usado = palpites_dia_usado + 1
        WHERE id = ?
    """, (plan_id,))
    conn.commit()
    conn.close()

# Função para gerar palpite estatístico
def gerar_palpite_estatistico(limite=15):
    conn = get_db()
    cursor = conn.cursor()
    
    # Busca todos os resultados oficiais
    cursor.execute('''
        SELECT n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11,n12,n13,n14,n15 
        FROM resultados_oficiais
    ''')
    
    resultados = cursor.fetchall()

    # Junta todos os números em uma única lista
    todos_numeros = [num for row in resultados for num in row]

    # Calcula frequência dos números de 1 a 25
    frequencia = {num: todos_numeros.count(num) for num in range(1, 26)}

    # Ordena por frequência
    numeros_ordenados = sorted(frequencia.items(), key=lambda x: x[1], reverse=True)
    top_10 = [num for num, _ in numeros_ordenados[:10]]
    outros = [num for num, _ in numeros_ordenados[10:20]]
    baixa_freq = [num for num, _ in numeros_ordenados[20:]]

    # Gera palpite balanceado
    palpite = (
        random.sample(top_10, 7) +
        random.sample(outros, 5) +
        random.sample(baixa_freq, 3)
    )
    return sorted(palpite)[:limite]

# Função para gerar palpite aleatório
def gerar_palpite_aleatorio(limite=15):
    return sorted(random.sample(range(1, 26), limite))

# Função para gerar palpite baseado em pares/ímpares
def gerar_palpite_pares_impares(limite=15):
    # Calcula quantos pares e ímpares para respeitar o limite total
    # Distribuição aproximada: metade pares, metade ímpares (ajustado para somar o limite)
    num_pares = limite // 2
    num_impares = limite - num_pares

    pares = random.sample(range(2, 26, 2), num_pares)
    impares = random.sample(range(1, 26, 2), num_impares)

    pares_impares_ajustado = sorted(pares + impares)
    return pares_impares_ajustado

# Funções carregar modelos LSTM
# 2. ADICIONAR estas funções (substituindo as originais):
@st.cache_resource
def carregar_modelo_14():
    # Importacao movida para dentro da funcao
    from tensorflow.keras.models import load_model
    try:
        model = load_model("modelo_lstm_14.h5")
        return model
    except Exception as e:
         st.error(f"Erro ao carregar modelo LSTM 14: {e}. Certifique-se de que o arquivo 'modelo_lstm_14.h5' existe.")
         return None

@st.cache_resource
def carregar_modelo_lstm():
     # Importacao movida para dentro da funcao
     from tensorflow.keras.models import load_model
     try:
         model = load_model("modelo_lstm.h5")
         return model
     except Exception as e:
         st.error(f"Erro ao carregar modelo LSTM: {e}. Certifique-se de que o arquivo 'modelo_lstm.h5' existe.")
         return None

# 3. SUBSTITUIR a funcao gerar_palpite_lstm ORIGINAL por esta:
def gerar_palpite_lstm(limite=15):
    # ... (conexao e busca de dados - mantem igual) ...
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11,n12,n13,n14,n15 
        FROM resultados_oficiais
    """)
    resultados = cursor.fetchall()
    conn.close()
    
    if len(resultados) < 5: # Pode manter 5 se so precisa dos ultimos
        raise ValueError("Histórico insuficiente para previsão com LSTM.")

    # Importacoes movidas
    import numpy as np # Mantem numpy

    def to_binario(jogo):
        binario = [0] * 25
        for n in jogo:
            binario[n - 1] = 1
        return binario
    
    # Prepara dados (apenas para entrada, NAO para treinar)
    binarios = [to_binario(r) for r in resultados]
    # Usa os ultimos 5 resultados como entrada para predicao
    entrada = np.array([binarios[-5:]])

    # Carrega o modelo usando a funcao cacheada
    modelo = carregar_modelo_lstm()
    if modelo is None:
       raise ValueError("Não foi possível carregar o modelo LSTM.")

    # Predicao (sem treinamento)
    pred = modelo.predict(entrada, verbose=0)[0]
    pred = np.clip(pred, 1e-8, 1)
    pred /= pred.sum()
    numeros = sorted(np.random.choice(range(1, 26), size=limite, replace=False, p=pred))
    return ",".join(map(str, numeros)) # Ou return numeros se quiser lista

# 4. SUBSTITUIR a funcao gerar_palpite_lstm_14 ORIGINAL por esta:
def gerar_palpite_lstm_14(limite=15):
    # ... (conexao e busca de dados - mantem igual) ...
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11,n12,n13,n14,n15 
        FROM resultados_oficiais
        ORDER BY concurso DESC
        LIMIT 5
    """)
    ultimos = cursor.fetchall()
    conn.close()

    if len(ultimos) < 5:
        raise ValueError("Histórico insuficiente para previsão com LSTM 14.")

    # Importacao movida
    import numpy as np

    def to_binario(jogo):
        binario = [0] * 25
        for n in jogo:
            binario[n - 1] = 1
        return binario

    entrada = np.array([[to_binario(j) for j in reversed(ultimos)]])

    # Carrega o modelo usando a funcao cacheada
    modelo = carregar_modelo_14()
    if modelo is None:
       raise ValueError("Não foi possível carregar o modelo LSTM 14.")

    pred = modelo.predict(entrada, verbose=0)[0]
    pred = np.clip(pred, 1e-8, 1)
    pred /= pred.sum()
    numeros = sorted(np.random.choice(range(1, 26), size=limite, replace=False, p=pred))
    return ",".join(map(str, numeros)) # Ou return numeros

# --- FIM DAS CORREÇÕES NO palpites.py ---

# Função principal para gerar palpites
def gerar_palpite():
    st.title("Gerar Palpite")

    id_usuario = st.session_state.usuario["id"]
    tipo_plano = st.session_state.usuario["tipo"]

    # 1. Verifica se ainda pode gerar palpites este mês
    permitido, nome_plano, palpites_restantes = verificar_limite_palpites(id_usuario)
    if not permitido:
        st.error(f"Você atingiu o Limite de Palpites do Plano {nome_plano} para este mês.")
        return

    # 2. Determina limite de dezenas conforme o plano (ex: 15, 17, 20)
    limite_dezenas = obter_limite_dezenas_por_plano(tipo_plano)

    # 3. Define os modelos de geração permitidos
    modelos_disponiveis = ["Aleatório", "Estatístico", "Pares/Ímpares"]
    if nome_plano in ["Silver", "Gold"]:
        modelos_disponiveis.append("LSTM")
        modelos_disponiveis.append("LSTM (14 acertos)")

    modelo = st.selectbox("Modelo de Geração:", modelos_disponiveis)
    if not modelo:
      st.warning("Por favor, selecione um modelo de geração.")
      return

    # 4. Permite ao usuário escolher quantos palpites gerar
    num_palpites = st.number_input(
        "Quantos Palpites Deseja Gerar?",
        min_value=1,
        max_value=palpites_restantes,
        value=1,
        step=1
    )

    if st.button("Gerar Palpites"):
        palpites_gerados = []
        try:
            for _ in range(num_palpites):
                if modelo == "Aleatório":
                    palpite = gerar_palpite_aleatorio(limite=limite_dezenas)
                elif modelo == "Estatístico":
                    palpite = gerar_palpite_estatistico(limite=limite_dezenas)
                elif modelo == "Pares/Ímpares":
                    palpite = gerar_palpite_pares_impares(limite=limite_dezenas)
                elif modelo == "LSTM":
                    palpite = gerar_palpite_lstm(limite=limite_dezenas)
                elif modelo == "LSTM (14 acertos)":
                    palpite = gerar_palpite_lstm_14(limite=limite_dezenas)
                else:
                    st.error("Modelo inválido.")
                    return

                salvar_palpite(palpite, modelo)
                atualizar_contador_palpites(id_usuario)
                palpites_gerados.append(palpite)

            st.success(f"{num_palpites} Palpite(s) Gerado(s) com Sucesso:")

            for i, p in enumerate(palpites_gerados, 1):
                texto = f"Palpite {i}: {p}"
                st.markdown(
                    f"""
                        <div style="padding: 10px; background-color: #f4f4f4; border-radius: 8px; margin-bottom: 10px;">
                             <span style="font-family: 'Poppins', sans-serif; font-size: 16px; font-weight: bold;">
                                {texto}
                             </span>
                            <button onclick="navigator.clipboard.writeText('{texto}')" 
                                     style="float:right; background:none; border:none; cursor:pointer;" 
                                    title="Copiar">
                               📋
                            </button>
                        </div>
                    """,
                    unsafe_allow_html=True
                )

            with st.expander("ℹ️ Aviso Sobre Cópia"):
                st.markdown(
                    "Em Alguns navegadores de celular ou Safari, o Botão de Cópia pode não Funcionar Corretamente. "
                    "Use o seu Botão ou como as teclas de costume para Copy"
                )

        except Exception as e:
            st.error(f"Erro ao Gerar seus Palpites: {str(e)}")

# Função para salvar o palpite no banco de dados
def salvar_palpite(palpite, modelo):
    conn = get_db()
    cursor = conn.cursor()

    # Se for lista, converte corretamente
    if isinstance(palpite, list):
        numeros_formatados = ",".join(map(str, palpite))
    else:
        numeros_formatados = str(palpite).strip("[] ")  # remove colchetes se vier como string

    cursor.execute('''
        INSERT INTO palpites (id_usuario, numeros, modelo, data)
        VALUES (?, ?, ?, ?)
    ''', (
        st.session_state.usuario["id"],
        numeros_formatados,
        modelo,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

# Função para exibir o histórico de palpites
def historico_palpites():

    if "usuario" not in st.session_state or not st.session_state.usuario:
        st.warning("Você precisa estar logado para acessar o histórico.")
        return

    st.markdown("### 📜 Histórico de Palpites")

    opcoes_modelo = ["Todos", "Aleatório", "Estatístico", "Ímpares-Pares", "LSTM", "LSTM (14 acertos)"]
    filtro_modelo = st.selectbox("Filtrar por modelo:", opcoes_modelo)

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT numeros, modelo, data, status FROM palpites WHERE id_usuario = ?"
    params = [st.session_state.usuario["id"]]

    if filtro_modelo != "Todos":
        query += " AND modelo = ?"
        params.append(filtro_modelo)

    query += " ORDER BY data DESC"
    cursor.execute(query, params)
    palpites = cursor.fetchall()
    conn.close()

    if palpites:
        for i in range(0, len(palpites), 2):  # 2 colunas por linha
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(palpites):
                    numeros, modelo, data, status = palpites[i + j]
                    status_str = "✅ Válido" if status == "S" else "⏳ Não usado"
                    with cols[j]:
                        st.markdown(f"""
                            <div style='background:#fdfdfd; padding:8px 12px; border-radius:8px; border:1px solid #ccc; margin-bottom:10px; min-height:80px'>
                                <div style='font-size:13px; color:#555; font-weight:bold;'>{modelo} | {status_str}</div>
                                <div style='font-size:11px; color:gray;'>{data}</div>
                                <div style='font-family: monospace; font-size:14px; margin-top:4px;'>{numeros}</div>
                                <button onclick="navigator.clipboard.writeText('{numeros}')" style="margin-top:6px; padding:3px 6px; font-size:11px; border:none; background-color:#1f77b4; color:white; border-radius:5px; cursor:pointer;">
                                    Copiar
                                </button>
                            </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("Nenhum palpite encontrado.")

# Função para validar um palpite
def validar_palpite():
    if "usuario" not in st.session_state or not st.session_state.usuario:
        st.warning("Você precisa estar logado para validar um palpite.")
        return

    st.markdown("### 📤 Validar Palpite")

    # Mostrar últimos palpites
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, numeros, modelo, data, status
        FROM palpites
        WHERE id_usuario = ?
        ORDER BY data DESC
        LIMIT 10
    """, (st.session_state.usuario["id"],))
    palpites = cursor.fetchall()
    conn.close()

    if not palpites:
        st.info("Você ainda não gerou nenhum palpite.")
        return

    st.markdown("#### Selecione um palpite para validar:")
    opcoes = {f"#{pid} | {modelo} | {data}": pid for pid, _, modelo, data, _ in palpites}
    selecao = st.selectbox("Palpites disponíveis:", list(opcoes.keys()))

    if st.button("✅ Validar este palpite"):
        palpite_id = opcoes[selecao]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE palpites
            SET status = 'S'
            WHERE id = ? AND id_usuario = ?
        """, (palpite_id, st.session_state.usuario["id"]))
        conn.commit()
        conn.close()
        st.success(f"Palpite #{palpite_id} marcado como validado com sucesso! Agora ele será destacado como oficial.")

    # Exibir cards com status
    st.markdown("---")
    st.markdown("### Seus últimos palpites:")

    for i in range(0, len(palpites), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(palpites):
                pid, numeros, modelo, data, status = palpites[i + j]
                status_texto = "✅ Validado" if status == "S" else "⏳ Não validado"
                cor_status = "#28a745" if status == "S" else "#666"
                bg = "#e9f7ef" if status == "S" else "#f8f8f8"
                
                # 👉 Aqui está a linha que você quer adicionar:
                cor_modelo = "#663399" if modelo == "LSTM (14 acertos)" else "#1f77b4"
                with cols[j]:
                    st.markdown(f"""
                        <div style='background:{bg}; padding:10px; border-radius:8px; border:1px solid #ccc; margin-bottom:10px'>
                            <div style='font-size:13px; color:{cor_status}; font-weight:bold;'>{status_texto}</div>
                            <div style='font-size:12px; color:#888;'>{modelo} | {data}</div>
                            <div style='font-family: monospace; font-size:14px; margin-top:4px;'>{numeros}</div>
                        </div>
                    """, unsafe_allow_html=True)                
                  