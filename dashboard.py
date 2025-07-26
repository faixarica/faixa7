import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import numpy as np

# Função para aplicar estilo CSS personalizado
def apply_custom_css():
    st.markdown("""
        <style>
            .card {
                padding: 15px;
                margin: 10px 0;
                border-left: 6px solid #6C63FF;
                border-radius: 10px;
                background-color: #f0f2f6;
                text-align: center;
                font-size: 16px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            .metric-title {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #333;
            }
            .metric-value {
                font-size: 22px;
                color: #6C63FF;
            }
            .scrollable-container {
                max-height: 700px;
                overflow-y: auto;
                padding-right: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

# Função para calcular a frequência dos números
def calcular_frequencia_numeros():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Busca todos os resultados oficiais
    cursor.execute("""
        SELECT n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11,n12,n13,n14,n15 
        FROM resultados_oficiais
    """)
    resultados = cursor.fetchall()
    conn.close()
    
    # Calcula a frequência de cada número
    todos_numeros = [num for resultado in resultados for num in resultado]
    frequencia = {num: todos_numeros.count(num) for num in range(1, 26)}
    return pd.DataFrame(list(frequencia.items()), columns=["Número", "Frequência"]), len(resultados)

# Função para calcular a distribuição de pares e ímpares
def calcular_distribuicao_pares_impares():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Busca todos os resultados oficiais
    cursor.execute("""
        SELECT n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11,n12,n13,n14,n15 
        FROM resultados_oficiais
    """)
    resultados = cursor.fetchall()
    conn.close()
    
    # Calcula a distribuição de pares e ímpares
    total_pares = 0
    total_impares = 0
    for resultado in resultados:
        pares = sum(1 for num in resultado if num % 2 == 0)
        impares = 15 - pares
        total_pares += pares
        total_impares += impares
    return {"Pares": total_pares, "Ímpares": total_impares}


    
    # Aplica o estilo CSS personalizado
    apply_custom_css()
    st.title("Dashboard")
    
    # Conexão com o banco de dados
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Último resultado do sorteio (incluindo data e número do concurso)
    cursor.execute("""
        SELECT n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11,n12,n13,n14,n15, data, concurso
        FROM resultados_oficiais
        ORDER BY rowid DESC
        LIMIT 1
    """)
    ultimo_resultado = cursor.fetchone()
    
    # Estatísticas gerais
    cursor.execute("""
        SELECT COUNT(*) FROM palpites
    """)
    total_palpites = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(DISTINCT id_usuario) FROM palpites
    """)
    total_usuarios_ativos = cursor.fetchone()[0]
    
    conn.close()
    
    # Exibição dos Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-title">Total de Palpites</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_palpites}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-title">Usuários Ativos</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_usuarios_ativos}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-title">Último Sorteio</div>', unsafe_allow_html=True)
        if ultimo_resultado:
            numeros = ", ".join(map(str, ultimo_resultado[:15]))
            data_sorteio = ultimo_resultado[15]
            concurso = ultimo_resultado[16]
            st.markdown(f'<div class="metric-value">Concurso: {concurso} ({data_sorteio})<br>{numeros}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-value">N/A</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráficos Estatísticos
    st.subheader("📊 Análise Estatística")
    
    if "usuario" in st.session_state and st.session_state.usuario:
        plano_id = st.session_state.usuario.get("id_plano", 1)
    
    if plano_id >= 2:
        st.subheader("📊 Gráficos Exclusivos para Assinantes")
        st.markdown('<div class="small-chart">', unsafe_allow_html=True)
        st.pyplot(grafico_frequencia_palpites())
        st.pyplot(grafico_pares_impares())
        st.pyplot(grafico_distribuicao_linhas())
        st.pyplot(grafico_distribuicao_colunas())
        st.pyplot(grafico_sequencias_consecutivas())
        st.pyplot(grafico_numeros_atrasados())
        st.pyplot(grafico_comparacao_modelos())
        st.pyplot(grafico_soma_palpite())
        st.pyplot(grafico_ultimos_palpites_grid())
        st.pyplot(grafico_mapa_calor_cartela())
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("🔒 Gráficos avançados disponíveis nos planos Silver e Gold.")
 
    
    # Gráfico 1: Frequência dos Números
    st.write("### Frequência dos Números Sorteados")
    df_frequencia, total_sorteios = calcular_frequencia_numeros()
    st.write(f"Base de cálculo: Últimos {total_sorteios} sorteios")
    fig, ax = plt.subplots(figsize=(7, 3.5))  # Diminuído em 30%
    sns.barplot(data=df_frequencia,x="Número",  y="Frequência", hue="Número",  alette="viridis",ax=ax, legend=False)
    ax.set_title("Frequência dos Números Sorteados", fontsize=14)
    ax.set_xlabel("Números", fontsize=12)
    ax.set_ylabel("Frequência", fontsize=12)
    st.markdown('<div class="small-chart">', unsafe_allow_html=True)
    st.markdown("**📈 Frequência nos palpites dos usuários**")
    with st.expander("ℹ️ O que significa esse gráfico?"):
        st.write("Este gráfico mostra quantas vezes cada número foi escolhido pelos usuários da plataforma FaixaBet ao gerar palpites. "
        "Você pode usar isso para identificar os números mais populares ('quentes') entre todos os jogadores.")

    st.pyplot(grafico_frequencia_palpites())   
    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráfico 2: Distribuição de Pares e Ímpares
    st.write("### Distribuição de Pares e Ímpares")
    distribuicao = calcular_distribuicao_pares_impares()
    fig, ax = plt.subplots(figsize=(4.2, 2.8))  # Diminuído em 30%
    ax.pie([distribuicao["Pares"], distribuicao["Ímpares"]], labels=["Pares", "Ímpares"], autopct='%1.1f%%', colors=["#4CAF50", "#FF9800"])
    ax.set_title("Distribuição de Pares e Ímpares", fontsize=14)
    st.markdown('<div class="small-chart">', unsafe_allow_html=True)
    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráfico 3: Média de Palpites por Usuário
    st.write("### Média de Palpites Gerados por Usuário")
    media_palpites = total_palpites / total_usuarios_ativos if total_usuarios_ativos > 0 else 0
    st.write(f"Explicação: Esta métrica calcula quantos palpites, em média, cada usuário ativo gerou. Total de palpites: {total_palpites}, Total de usuários ativos: {total_usuarios_ativos}.")
    fig, ax = plt.subplots(figsize=(4.2, 2.8))  # Diminuído em 30%
    ax.bar(["Média de Palpites"], [media_palpites], color="#03A9F4")
    ax.set_title("Média de Palpites por Usuário", fontsize=14)
    ax.set_ylabel("Palpites", fontsize=12)
    st.markdown('<div class="small-chart">', unsafe_allow_html=True)
    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)  
 
 # Dashboard principal

# Função principal do Dashboard
def mostrar_dashboard():
    apply_custom_css()
    st.title("Painel Estatístico")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11,n12,n13,n14,n15, data, concurso
        FROM resultados_oficiais
        ORDER BY rowid DESC LIMIT 1
    """)
    ultimo_resultado = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM palpites")
    total_palpites = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT id_usuario) FROM palpites")
    total_usuarios_ativos = cursor.fetchone()[0]

    conn.close()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-title">Total de Palpites</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_palpites}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-title">Usuários Ativos</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_usuarios_ativos}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-title">Último Sorteio</div>', unsafe_allow_html=True)
        if ultimo_resultado:
            numeros = ", ".join(map(str, ultimo_resultado[:15]))
            data_sorteio = ultimo_resultado[15]
            concurso = ultimo_resultado[16]
            st.markdown(f'<div class="metric-value">Concurso: {concurso} ({data_sorteio})<br>{numeros}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-value">N/A</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Recupera o plano do usuário logado (padrão: 1)
    plano_id = 1
    if "usuario" in st.session_state and st.session_state.usuario:
        plano_id = st.session_state.usuario.get("id_plano", 1)

    abas = st.tabs([
        "Frequência", "Pares/Impares", " Soma", "Mapa de Calor", "Comparativos"
    ])

    with abas[0]:
        st.subheader("Frequência dos Números Sorteados")
        df_frequencia, total_sorteios = calcular_frequencia_numeros()
        st.write(f"Base de cálculo: Últimos {total_sorteios} sorteios")
        fig, ax = plt.subplots(figsize=(7, 3.5))
        sns.barplot(data=df_frequencia,x="Número",  y="Frequência", hue="Número",  palette="viridis",ax=ax, legend=False)
        ax.set_title("Frequência dos Números Sorteados", fontsize=14)
        st.pyplot(fig)

        with st.expander("ℹ️ Explicação"):
            st.write("Este gráfico mostra quais números mais saíram nos sorteios oficiais.")

    with abas[1]:
        st.subheader("Distribuição de Pares e Ímpares")
        distribuicao = calcular_distribuicao_pares_impares()
        fig, ax = plt.subplots()
        ax.pie([distribuicao["Pares"], distribuicao["Ímpares"]],
               labels=["Pares", "Ímpares"], autopct='%1.1f%%', colors=["#4CAF50", "#FF9800"])
        ax.set_title("Pares vs Ímpares")
        st.pyplot(fig)

        with st.expander("ℹ️ Explicação"):
            st.write("Mostra a proporção de números pares e ímpares escolhidos nos jogos.")

    with abas[2]:
        st.subheader("Soma dos Palpites")
        fig = grafico_soma_palpite()
        st.pyplot(fig)

        with st.expander("ℹ️ Explicação"):
            st.write("Mostra a distribuição da soma total dos números escolhidos em cada jogo.")

    with abas[3]:
        st.subheader("Mapa de Calor da Cartela")
        fig = grafico_mapa_calor_cartela()
        st.pyplot(fig)

        with st.expander("ℹ️ Explicação"):
            st.write("Mostra a quantidade de vezes que cada número foi usado em posições da cartela 5x5.")

    with abas[4]:
        if plano_id >= 2:
            st.subheader("Comparativo de Modelos de Palpite")
            fig = grafico_comparacao_modelos()
            st.pyplot(fig)

            st.subheader("Sequências Consecutivas")
            fig = grafico_sequencias_consecutivas()
            st.pyplot(fig)

            st.subheader("Palpites Recentes (Visual)")
            fig = grafico_ultimos_palpites_grid()
            st.pyplot(fig)
        else:
            st.info("🔒 Estes gráficos estão disponíveis apenas para usuários Silver e Gold.")

    st.markdown("""
        <hr style="margin-top:30px;">
        <div style='text-align:center; font-size:12px; color:gray;'>
            Aqui Não é Sorte • é AI 
        </div>
    """, unsafe_allow_html=True)
  
# Função para buscar informações do plano
def buscar_planos_disponiveis():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, preco FROM planos WHERE nome IN ('Silver', 'Gold')")
    planos = cursor.fetchall()
    conn.close()
    return {nome: {"id": pid, "preco": preco} for pid, nome, preco in planos}

def grafico_frequencia_palpites():
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT numeros FROM palpites", conn)
    conn.close()

    # Expande os palpites para colunas
    todos_numeros = df["numeros"].dropna().apply(lambda x: list(map(int, x.split(","))))
    todos_numeros = pd.Series([num for sublist in todos_numeros for num in sublist])

    # Frequência
    frequencia = todos_numeros.value_counts().sort_index()
    df_freq = pd.DataFrame({"Número": frequencia.index, "Frequência": frequencia.values})

    # Gráfico
    fig, ax = plt.subplots(figsize=(7, 3.5))
    sns.barplot(data=df_freq, x="Número", y="Frequência", palette="Blues", ax=ax)
    ax.set_title("Frequência nos Palpites dos Usuários", fontsize=14)
    ax.set_xlabel("Números")
    ax.set_ylabel("Frequência")

    return fig

def grafico_pares_impares():
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT numeros FROM palpites", conn)
    conn.close()

    df = df.dropna()
    df["pares"] = df["numeros"].apply(lambda x: sum(1 for n in map(int, x.split(",")) if n % 2 == 0))
    pares_counts = df["pares"].value_counts().sort_index()
    labels = [f"{p} Pares / {15 - p} Ímpares" for p in pares_counts.index]

    fig, ax = plt.subplots()
    ax.pie(pares_counts, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title("Distribuição de Pares e Ímpares nos Palpites")
    return fig

def grafico_distribuicao_linhas():
    linha_map = {i: (i - 1) // 5 + 1 for i in range(1, 26)}
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT numeros FROM palpites", conn)
    conn.close()

    numeros = df["numeros"].dropna().apply(lambda x: [linha_map[int(n)] for n in x.split(",")])
    linhas = pd.Series([linha for sublist in numeros for linha in sublist])
    linha_freq = linhas.value_counts().sort_index()

    fig, ax = plt.subplots()
    sns.barplot(x=linha_freq.index, y=linha_freq.values, ax=ax, palette="Blues")
    ax.set_title("Frequência por Linha (Horizontal)")
    ax.set_xlabel("Linha")
    ax.set_ylabel("Frequência")
    return fig

def grafico_distribuicao_colunas():
    col_map = {i: (i - 1) % 5 + 1 for i in range(1, 26)}
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT numeros FROM palpites", conn)
    conn.close()

    numeros = df["numeros"].dropna().apply(lambda x: [col_map[int(n)] for n in x.split(",")])
    colunas = pd.Series([col for sublist in numeros for col in sublist])
    col_freq = colunas.value_counts().sort_index()

    fig, ax = plt.subplots()
    sns.barplot(x=col_freq.index, y=col_freq.values, ax=ax, palette="Purples")
    ax.set_title("Frequência por Coluna (Vertical)")
    ax.set_xlabel("Coluna")
    ax.set_ylabel("Frequência")
    return fig

def grafico_sequencias_consecutivas():
    def contar_seq(nums):
        nums = sorted(map(int, nums.split(",")))
        cont, total = 1, 0
        for i in range(1, len(nums)):
            if nums[i] == nums[i - 1] + 1:
                cont += 1
            else:
                if cont > 1:
                    total += 1
                cont = 1
        if cont > 1:
            total += 1
        return total

    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT numeros FROM palpites", conn)
    conn.close()
    
    df["seq"] = df["numeros"].dropna().apply(contar_seq)
    fig, ax = plt.subplots()
    sns.histplot(df["seq"], bins=range(0, 6), discrete=True, ax=ax, color="green")
    ax.set_title("Ocorrência de Sequências Consecutivas nos Palpites")
    ax.set_xlabel("Qtde de Sequências por Jogo")
    return fig

def grafico_numeros_atrasados():
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT numeros, data FROM palpites", conn)
    conn.close()

    df = df.dropna()
    ultimos = {}
    for _, row in df.iterrows():
        for n in map(int, row["numeros"].split(",")):
            ultimos[n] = row["data"]
    
    hoje = pd.to_datetime("today")
    dias = {k: (hoje - pd.to_datetime(v)).days for k, v in ultimos.items()}
    df_dias = pd.DataFrame(list(dias.items()), columns=["Número", "Dias sem sair"]).sort_values("Dias sem sair", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data=df_dias, x="Número", y="Dias sem sair", palette="Oranges", ax=ax)
    ax.set_title("Números Mais Atrasados nos Palpites")
    return fig

def grafico_comparacao_modelos():
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT modelo FROM palpites", conn)
    conn.close()

    contagem = df["modelo"].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=contagem.index, y=contagem.values, palette="Set2", ax=ax)
    ax.set_title("Comparativo: Geração de Palpites por Modelo")
    ax.set_ylabel("Total de Jogos Gerados")
    return fig

def grafico_soma_palpite():
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT numeros FROM palpites", conn)
    conn.close()

    df["soma"] = df["numeros"].dropna().apply(lambda x: sum(map(int, x.split(","))))
    fig, ax = plt.subplots()
    sns.histplot(df["soma"], bins=20, kde=True, color="navy", ax=ax)
    ax.set_title("Soma Total dos Números por Palpite")
    return fig

def grafico_ultimos_palpites_grid():
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT numeros, data FROM palpites ORDER BY data DESC LIMIT 10", conn)
    conn.close()

    fig, ax = plt.subplots(figsize=(10, 3))
    for i, row in enumerate(df.itertuples(), start=0):
        nums = list(map(int, row.numeros.split(",")))
        for num in nums:
            ax.text(num, 10 - i, "■", ha="center", va="center", fontsize=10)

    ax.set_xlim(1, 25)
    ax.set_ylim(0, 10)
    ax.set_xticks(range(1, 26))
    ax.set_yticks([])
    ax.set_title("Últimos 10 Palpites Visualmente")
    return fig

def grafico_mapa_calor_cartela():
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT numeros FROM palpites", conn)
    conn.close()

    contagem = defaultdict(int)

    for linha in df["numeros"].dropna():
        numeros = linha.strip("[] ").split(",")
        for n in numeros:
            try:
                contagem[int(n)] += 1
            except ValueError:
                continue  # Ignora valores inválidos

    # Garante que todos de 1 a 25 estejam presentes
    for i in range(1, 26):
        contagem[i] += 0

    matriz = np.array([contagem[i] for i in range(1, 26)]).reshape(5, 5)

    fig, ax = plt.subplots()
    sns.heatmap(matriz, annot=True, fmt="d", cmap="YlGnBu", ax=ax, cbar=False)
    ax.set_title("Mapa de Calor dos Números por Posição (Estilo Cartela)")
    return fig
