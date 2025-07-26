import streamlit as st
from datetime import datetime, timedelta
import sqlite3
import csv
import streamlit.components.v1 as components
from dashboard import mostrar_dashboard
from palpites import gerar_palpite, historico_palpites, validar_palpite
from auth import logout
from perfil import editar_perfil
from financeiro import exibir_aba_financeiro
from importador import importar_dados
import requests
import pandas as pd
from passlib.hash import pbkdf2_sha256

#hash = pbkdf2_sha256.hash("minhasenha")
#pbkdf2_sha256.verify("minhasenha", hash)

senha = "654321"
hash = pbkdf2_sha256.hash(senha)

print(hash)


def usuario_logado():
    return st.session_state.get("logged_in") and st.session_state.get("usuario")

st.set_page_config(page_title="FaixaBet", layout="centered")

# Cabeçalho fixo
st.markdown("""
    <div style='
        width: 100%; 
        text-align: center; 
        padding: 6px 0; 
        font-size: 46px; 
        font-weight: bold; 
        color: green;
        border-bottom: 1px solid #DDD;
    '>Bem-vindo à FaixaBet®
        <hr style="margin: 0; border: 0; border-top: 1px solid #DDD;">
        <div style='text-align:center; font-size:16px; color:black; margin-top:4px;'>
             Aqui Não é Sorte   •      é  AI 
        </div>
    </div>
""", unsafe_allow_html=True)
def css_global():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        font-size: 18px;
    }
        
        @import url('https://fonts.googleapis.com/css2?family=Poppins&display=swap');
        html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        font-size: 18px;
    }
        /* Centraliza o título */
        .main > div > div > div > div {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        /* Título FaixaBet */
        .login-title {
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            color: #008000;
            margin-bottom: 24px;
        }

        /* Estilo dos inputs e botões */
        input, .stButton button {
            width: 50ch !important;
            max-width: 60%;
            margin-top: 8px;
            padding: 8px;
            border-radius: 8px;
        }

        /* Botões */
        .stButton button {
            background-color: #008000;
            color: white;
            font-weight: bold;
            border: none;
            cursor: pointer;
        }
        .stButton button:hover {
            background-color: #005e00;
        }

        /* Radio Buttons - horizontal e colorido */
        div[role="radiogroup"] > label[data-baseweb="radio"] div[aria-checked="true"] {
            background-color: #00C853;
            border-color: #00C853;
            color: white;
        }
        /* Texto do radio */
        label[data-baseweb="radio"] {
        font-size: 40px !important;
        color: #0d730d !important;
        font-weight: 500;
        }
        /* Cards simulados */
        .login-card {
            padding: 16px;
            background-color: #f9f9f9;
            border-radius: 12px;
            box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.1);
            margin-top: 16px;
        }

        <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        font-size: 18px;
    }

    .login-card {
        background-color: #f9f9f9;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-top: 30px;
    }
    .stButton button {
        font-size: 18px !important;
        padding: 10px 24px !important;
        transform: scale(1.1);
    }
    </style>
        </style>
    """, unsafe_allow_html=True)

if 'admin' not in st.session_state:
    st.session_state.admin = False

# Inicializa variáveis no session_state para evitar erros de atributo inexistente
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if usuario_logado():
    nome = st.session_state.usuario["nome"]
#    st.write(f"Olá, {nome}!")

def criar_usuario(nome, email, telefone, data_nascimento, usuario, senha, tipo, id_plano):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? OR email = ?", (usuario, email))
    if cursor.fetchone():
        st.error("Usuário ou email já cadastrado!")
        return False

    from passlib.hash import pbkdf2_sha256
    senha_hash = pbkdf2_sha256.hash(senha)
    try:
        cursor.execute('''
            INSERT INTO usuarios (
                nome_completo, email, telefone, data_nascimento, 
                senha, usuario, tipo, id_plano, dt_cadastro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (nome, email, telefone, data_nascimento, senha_hash, usuario, tipo, id_plano))

        id_cliente = cursor.lastrowid
        hoje = datetime.now()
        expiracao = hoje + timedelta(days=30)
        cursor.execute('''
            INSERT INTO client_plans (id_client, id_plano, ativo, data_inclusao, data_expira_plan)
            VALUES (?, ?, 1, ?, ?)
        ''', (id_cliente, id_plano, hoje.strftime('%Y-%m-%d'), expiracao.strftime('%Y-%m-%d')))

        conn.commit()
        st.success("Cadastro realizado com sucesso! Faça login para continuar.")
        return True

    except Exception as e:
        conn.rollback()
        print("Erro no cadastro:", e)
        st.error(f"Erro no cadastro: {e}")
        return False

    finally:
        conn.close()
def calcular_palpites_periodo(id_usuario):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM palpites WHERE id_usuario = ? AND DATE(substr(data, 1, 10)) = DATE('now')", (id_usuario,))
    dia = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM palpites WHERE id_usuario = ? AND strftime('%W', data) = strftime('%W', 'now')", (id_usuario,))
    semana = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM palpites WHERE id_usuario = ? AND strftime('%m', data) = strftime('%m', 'now')", (id_usuario,))
    mes = cursor.fetchone()[0]

    conn.close()
    return dia, semana, mes

def registrar_login(id_usuario):    
    try:
        resposta = requests.get("https://ipinfo.io/json", timeout=5)
        dados = resposta.json()
    except:
        dados = {}

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO log_user (
            id_cliente, data_hora, ip, hostname, city, region, country, loc, org, postal, timezone
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        id_usuario,
        agora,
        dados.get("ip", "desconhecido"),
        dados.get("hostname", ""),
        dados.get("city", ""),
        dados.get("region", ""),
        dados.get("country", ""),
        dados.get("loc", ""),
        dados.get("org", ""),
        dados.get("postal", ""),
        dados.get("timezone", "")
    ))

    conn.commit()
    conn.close()


# LOGIN / CADASTRO
if not st.session_state.get("logged_in", False):
    st.markdown("## Acesso ao Sistema")

    aba = st.radio("", ["Login", "Cadastro"], horizontal=True, label_visibility="collapsed")
    st.write("")

    if aba == "Login":
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
           

            if usuario_input == "ufaixa990" and senha_input == "ufaixa990!":
                st.session_state.logged_in = True
                st.session_state.usuario = {
                    "id": 0,
                    "nome": "Administrador",
                    "email": "adm@faixabet.com",
                    "tipo": "admin",
                    "id_plano": 0
                }
                st.session_state.admin = True
                st.success("Login administrativo realizado!")
                
                st.rerun()

            cursor.execute("""
                SELECT id, tipo, usuario, email, senha, ativo 
                FROM usuarios 
                WHERE usuario = ?
            """, (usuario_input,))
            user = cursor.fetchone()
            conn.close()

            if user:
                id, tipo, usuario, email, senha_hash, ativo = user
                if pbkdf2_sha256.verify(senha_input, senha_hash):
                    if ativo:
                        st.session_state.logged_in = True
                        st.session_state.usuario = {
                            "id": id,
                            "nome": usuario,
                            "email": email,
                            "tipo": tipo,
                            "id_plano": 1
                        }
                        if tipo == "admin":
                            st.session_state.admin = True
                        registrar_login(id)
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Conta inativa.")
                else:
                    st.error("Senha incorreta.")
            else:
                st.error("Usuário não encontrado.")

        st.markdown('<a class="recover" href="#">Esqueceu a senha?</a>', unsafe_allow_html=True)

    elif aba == "Cadastro":
        nome = st.text_input("Nome Completo*")
        email = st.text_input("Email*")
        telefone = st.text_input("Telefone")
        data_nascimento = st.date_input("Data de Nascimento")
        usuario = st.text_input("Nome de Usuário*")
        senha = st.text_input("Senha*", type="password")
        confirmar = st.text_input("Confirme a Senha*", type="password")

        if st.button("Cadastrar"):
            if senha != confirmar:
                st.error("As senhas não coincidem.")
            else:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM usuarios WHERE usuario = ? OR email = ?", (usuario, email))
                if cursor.fetchone():
                    st.error("Usuário ou email já cadastrado!")
                else:
                    senha_hash = pbkdf2_sha256.hash(senha)
                    cursor.execute('''
                        INSERT INTO usuarios (
                            nome_completo, email, telefone, data_nascimento, 
                            senha, usuario, tipo, id_plano, dt_cadastro
                        ) VALUES (?, ?, ?, ?, ?, ?, 'cliente', 1, datetime('now'))
                    ''', (nome, email, telefone, str(data_nascimento), senha_hash, usuario))

                    id_cliente = cursor.lastrowid
                    hoje = datetime.now()
                    expiracao = hoje + timedelta(days=30)

                    cursor.execute('''
                        INSERT INTO client_plans (id_client, id_plano, ativo, data_inclusao, data_expira_plan)
                        VALUES (?, 1, 1, ?, ?)
                    ''', (id_cliente, hoje.strftime('%Y-%m-%d'), expiracao.strftime('%Y-%m-%d')))

                    conn.commit()
                    st.success("Cadastro realizado com sucesso! Faça login para continuar.")
                conn.close()

        st.markdown('<a class="recover" href="#">← Voltar ao Login</a>', unsafe_allow_html=True)


    st.stop()


def admin_dashboard():
    st.markdown("<h2 style='color: green;'>Painel Administrativo - FaixaBet</h2>", unsafe_allow_html=True)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # 1. Total de usuários e média de palpites por dia
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) * 1.0 / COUNT(DISTINCT DATE(data))
        FROM palpites
    """)
    media_palpites_dia = round(cursor.fetchone()[0] or 0, 2)

    # 2. Usuários por plano
    cursor.execute("SELECT id_plano, COUNT(*) FROM usuarios GROUP BY id_plano")
    planos = {1: "Free", 2: "Silver", 3: "Gold"}
    dist_planos = {planos.get(row[0], "Desconhecido"): row[1] for row in cursor.fetchall()}

    # 3. Total de logins registrados
    cursor.execute("SELECT COUNT(*) FROM log_user")
    total_logins = cursor.fetchone()[0]

    # 4. Faturamento por plano
    cursor.execute("""
        SELECT p.nome, SUM(f.valor)
        FROM financeiro f
        JOIN planos p ON f.id_plano = p.id
        GROUP BY f.id_plano
    """)
    faturamento = {row[0]: round(row[1] or 0, 2) for row in cursor.fetchall()}

    conn.close()

    # ==== UI Cards Estilizados ====
    with st.container():
        st.markdown(" 📌 Visão Geral")
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"👥 **Total de Usuários**\n\n{total_usuarios}")
        with col2:
            st.info(f"📈 **Média de Palpites/dia**\n\n{media_palpites_dia}")

    with st.container():
        st.markdown(" 🧑‍💻 Usuários por Plano")
        col3, col4, col5 = st.columns(3)
        with col3:
            st.warning(f"🆓 **Free**\n\n{dist_planos.get('Free', 0)}")
        with col4:
            st.success(f"🥈 **Silver**\n\n{dist_planos.get('Silver', 0)}")
        with col5:
            st.error(f"🥇 **Gold**\n\n{dist_planos.get('Gold', 0)}")

    with st.container():
        st.markdown("🔐 Acessos e Receita")
        col6, col7 = st.columns(2)
        with col6:
            st.info(f"🔐 **Total de Logins**\n\n{total_logins}")
        with col7:
            st.success(f"💰 **Faturamento Total**\n\nR$ {sum(faturamento.values()):.2f}")

    with st.container():
        st.markdown(" 💸 Faturamento por Plano")
        for plano, valor in faturamento.items():
            st.write(f"• {plano}: R$ {valor:.2f}")

    # ================= Importar últimos resultados =================
    st.markdown("📥 **Importar Resultados Oficiais da Loteria**")

    if st.button("📂 Importar novos concursos da Lotofácil"):
        try:
 #           resultado = importar_dados("loteria.csv")
            resultado = importar_dados()


            if resultado["total"] > 0:
                st.success(f"✅ {resultado['total']} concursos importados com sucesso!")
                st.write(f"Concursos: {', '.join(map(str, resultado['importados']))}")
            else:
                st.info("ℹ️ Nenhum novo concurso para importar.")

            if resultado["erros"]:
                st.warning(f"⚠️ {len(resultado['erros'])} concursos não puderam ser importados.")
                with st.expander("Ver erros"):
                    for erro in resultado["erros"]:
                        st.text(f"- {erro}")

        except Exception as e:
            st.error(f"❌ Erro crítico ao importar resultados: {e}")

    st.markdown("---")
    st.markdown("🧪 Funções de Teste / Inicialização")

    if st.button("🚀 Popular usuários escassez (2.415)"):
        inseridos = popular_escassez()
        if inseridos:
            st.success(f"✅ {inseridos} usuários escassez inseridos.")
        else:
            st.info("ℹ️ Usuários escassez já estão no banco.")
            
    st.markdown("---")
    if st.button("🚪 Sair do Painel"):
        st.session_state.logged_in = False
        st.session_state.usuario = None
        st.session_state.admin = False
        st.success("Sessão encerrada.")
        st.rerun()
    st.markdown("---")
    st.markdown("📊 **Consulta de Palpites por Data**")

    st.markdown("<h5>Escolha a Data do Concurso</h5>", unsafe_allow_html=True)
    data_selecionada = st.date_input("", format="DD/MM/YYYY")

    st.markdown("---")
    st.markdown("📊 **Verificar Palpites com Resultados Oficiais**")

    st.markdown("<h5>Escolha a Data do Concurso</h5>", unsafe_allow_html=True)
    data_escolhida = st.date_input("📅 Data para verificação de palpites", format="DD/MM/YYYY")

    if st.button("🔍 Verificar Palpites e Contar Acertos"):
        try:
            # Formatar data
            data_str = data_escolhida.strftime("%d/%m/%Y")
            data_obj = datetime.strptime(data_str, "%d/%m/%Y")
            data_inicio = data_obj.strftime("%Y-%m-%d 00:00:00")
            data_fim = data_obj.strftime("%Y-%m-%d 23:59:59")

            # Conectar e buscar resultado oficial
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT numeros, concurso FROM resultados_oficiais
                WHERE data BETWEEN ? AND ?
                ORDER BY data DESC LIMIT 1
            """, (data_inicio, data_fim))
            resultado = cursor.fetchone()

            if resultado:
                numeros_str, concurso = resultado
                numeros_oficiais = list(map(int, numeros_str.split(",")))
                st.success(f"✅ Resultado oficial encontrado para o concurso {concurso}")
                st.markdown(f"<p style='font-size:20px;'>🧮 Números sorteados: <strong>{numeros_str}</strong></p>", unsafe_allow_html=True)

                # Buscar palpites da data
                df = pd.read_sql_query("SELECT * FROM palpites WHERE data BETWEEN ? AND ?", conn, params=(data_inicio, data_fim))

                if df.empty:
                    st.warning("⚠️ Nenhum palpite encontrado para essa data.")
                else:
                    def contar_acertos(palpites_df, numeros_oficiais):
                        acertos = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
                        for _, row in palpites_df.iterrows():
                            numeros = list(map(int, row['numeros'].split(',')))
                            qtd_acertos = len(set(numeros) & set(numeros_oficiais))
                            if qtd_acertos in acertos:
                                acertos[qtd_acertos] += 1
                        return acertos

                    resumo = contar_acertos(df, numeros_oficiais)
                    st.info("🎯 **Resumo de Acertos**")
                    for pontos in sorted(resumo.keys(), reverse=True):
                        st.write(f"💥 {pontos} pontos: {resumo[pontos]} palpites")

                    st.markdown("📝 Palpites do dia:")
                    st.dataframe(df)

            else:
                st.warning("⚠️ Nenhum resultado oficial encontrado para esta data.")

            conn.close()

        except Exception as e:
            st.error(f"❌ Erro ao verificar palpites: {e}")



def popular_escassez():
    import sqlite3
    from passlib.hash import pbkdf2_sha256
    from datetime import datetime
    import random

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario LIKE 'escassez%'")
    ja_existem = cursor.fetchone()[0]
    if ja_existem >= 2415:
        return 0  # já inseridos

    senha_hash = pbkdf2_sha256.hash("123456")
    hoje = datetime.now().strftime('%Y-%m-%d')

    usuarios_por_plano = {
        1: 1200,
        2: 800,
        3: 415
    }

    contador = 1

    for plano_id, quantidade in usuarios_por_plano.items():
        for _ in range(quantidade):
            nome = f"Usuário {contador} Escassez"
            email = f"escassez{contador}@fake.com"
            usuario = f"escassez{contador}"
            telefone = f"55{random.randint(1000000000, 9999999999)}"
            nascimento = f"{random.randint(1970, 2005)}-01-01"

            cursor.execute('''
                INSERT INTO usuarios (
                    nome_completo, email, telefone, data_nascimento,
                    senha, usuario, tipo, id_plano, dt_cadastro, ativo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ''', (
                nome, email, telefone, nascimento,
                senha_hash, usuario, "cliente", plano_id, hoje
            ))

            contador += 1

    conn.commit()
    conn.close()
    return contador - 1

# USUÁRIO LOGADO
if st.session_state.admin:
    admin_dashboard()
    st.stop()
    
nome_usuario = st.session_state.usuario.get("nome", "Usuário")
st.sidebar.title(f"Bem-Vindo, {nome_usuario}")
# === Banner promocional global ===
st.markdown("""
<div style="background-color:#FFF9C4; padding:14px; border-radius:8px; text-align:center; border:1px solid #FDD835; margin-bottom:20px;">
    <strong>Aproveite a sorte:</strong> uso 100% gratuito por tempo limitado!<br>
    💡 Em breve será necessário um plano para continuar usando.
</div>
""", unsafe_allow_html=True)
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM usuarios")
total_usuarios = cursor.fetchone()[0]

# Considera que escassez inicial foi 2415
base_escassez = 2415
meta = 10000
st.markdown(f"""
<div style="background-color:#E8F5E9; padding:12px; border-radius:8px; text-align:center; border:1px solid #A5D6A7; margin-bottom:20px;">
    📈 <strong>{total_usuarios:,} usuários cadastrados</strong><br>
    Rumo aos <strong>{meta:,}</strong> disponíveis! 🚀
</div>
""", unsafe_allow_html=True)


st.sidebar.markdown("""
    <div style='
        text-align: center; 
        padding: 8px 0; 
        font-size: 26px; 
        font-weight: bold; 
        color: green;
        border-bottom: 1px solid #DDD;
    '>FaixaBet®</div>
""", unsafe_allow_html=True)
opcao_selecionada = st.sidebar.radio("Menu", ["Dashboard", "Gerar Bets", "Histórico", "Validar","Financeiro","Editar Perfil", "Sair"])

if opcao_selecionada == "Dashboard":
    mostrar_dashboard()
    dia, semana, mes = calcular_palpites_periodo(st.session_state.usuario["id"])
    st.markdown("---")
    st.metric("Palpites hoje", dia)
    st.metric("Palpites na semana", semana)
    st.metric("Palpites no mês", mes)

elif opcao_selecionada == "Gerar Bets":
    gerar_palpite()

elif opcao_selecionada == "Histórico":
    historico_palpites()

elif opcao_selecionada == "Validar":
    validar_palpite()
    
elif opcao_selecionada == "Financeiro":
    st.subheader("Financeiro")
    exibir_aba_financeiro()
    
elif opcao_selecionada == "Editar Perfil":
    st.subheader("Editar")
    editar_perfil()

elif opcao_selecionada == "Sair":
    logout()
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'></div>", unsafe_allow_html=True)


st.sidebar.markdown("<div style='text-align:left; color:green; font-size:16px;'>FaixaBet v7.001</div>", unsafe_allow_html=True)

def exibir_aba_financeiro():
    if 'usuario' not in st.session_state or st.session_state.usuario is None:
        st.error("Você Precisa Estar Logado.")
        return

    user = st.session_state.usuario
    user_id = user['id']
    plano_id = user['id_plano']

    # 🔁 Carrega planos diretamente do banco
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, valor FROM planos")
    planos_raw = cursor.fetchall()
    conn.close()

    # 🔁 Transforma em dicionários
    planos = {p[0]: p[1] for p in planos_raw}
    precos = {p[0]: p[2] for p in planos_raw}

    plano_atual_nome = planos.get(plano_id, "Desconhecido")
    valor_atual = precos.get(plano_id, 0.0)

    st.subheader("💳 Informações Financeiras")
    st.markdown(f"**Plano atual:** {plano_atual_nome}")
    st.markdown(f"**Valor do plano:** R$ {valor_atual:.2f}")

   
    # Últimos pagamentos
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
        st.markdown(" Últimos Pagamentos")
        for row in registros:
            data_pgto, forma, valor, validade, plano_pgto = row
            st.write(f"- [{data_pgto}] {planos[plano_pgto]} - R$ {valor:.2f} via {forma} | válido até {validade}")
    else:
        st.info("Nenhum pagamento registrado ainda.")

    st.markdown("---")
    st.markdown("🔄 Simular Novo Pagamento")

    novo_plano = st.selectbox("Escolha um novo plano", ["Free", "Silver", "Gold"])
    forma_pagamento = st.selectbox("Forma de pagamento", ["Cartão", "Débito", "Pix"])

    if st.button("Confirmar e simular pagamento"):
        novo_id = 1 if novo_plano == "Free" else (2 if novo_plano == "Silver" else 3)
        novo_valor = precos[novo_id]
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
        st.success(f"Pagamento do plano {novo_plano} registrado com sucesso!")
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("❌ Cancelar plano pago")

    if plano_id != 1:
        if st.button("Cancelar plano e voltar para o Free"):
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET id_plano = 1 WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()

            st.session_state.usuario['id_plano'] = 1
            st.success("Plano cancelado. Agora você está no plano Free.")
            st.experimental_rerun()
    else:
        st.info("Você já está no plano Free.")
