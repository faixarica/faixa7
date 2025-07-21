from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.schema import CreateTable
import re

# === CONFIGURAÇÕES ===
SQLITE_DB_PATH = 'database.db'

postgres_url = 'postgresql://neondb_owner:npg_Lqjh6vGBVi5r@ep-black-hill-acpnaibc-pooler.sa-east-1.aws.neon.tech/Faixabs?sslmode=require&channel_binding=require'

# === CONEXÕES ===
sqlite_engine = create_engine(f'sqlite:///{SQLITE_DB_PATH}')
sqlite_conn = sqlite_engine.connect()

pg_engine = create_engine(postgres_url)
pg_conn = pg_engine.connect()

metadata = MetaData()
metadata.reflect(bind=sqlite_engine)

# === AJUSTES DE COMPATIBILIDADE SQL ===
def ajustar_ddl_postgres(ddl: str) -> str:
    # datetime → now()
    ddl = re.sub(r"TEXT DEFAULT datetime\('now'\)", "TIMESTAMP DEFAULT now()", ddl, flags=re.IGNORECASE)
    ddl = re.sub(r"DEFAULT datetime\('now'\)", "DEFAULT now()", ddl, flags=re.IGNORECASE)

    # REAL → FLOAT
    ddl = re.sub(r"\bREAL\b", "FLOAT", ddl, flags=re.IGNORECASE)

    # INTEGER DEFAULT 0/1 → mantido como INTEGER (evita conflitos de FK)
    # Se quiser aplicar boolean apenas a campos isolados, pode fazer manual depois

    # AUTOINCREMENT → SERIAL
    ddl = re.sub(r"(\w+)\s+INTEGER PRIMARY KEY AUTOINCREMENT", r"\1 SERIAL PRIMARY KEY", ddl, flags=re.IGNORECASE)

    # Remover aspas
    ddl = ddl.replace('"', '')
    return ddl

# === EXECUÇÃO: CRIAR TABELAS ===
erros_criacao = []

for table in metadata.sorted_tables:
    ddl = str(CreateTable(table).compile(dialect=pg_engine.dialect))
    ddl_ajustado = ajustar_ddl_postgres(ddl)
    print(f"\n➡️ Criando tabela: {table.name}")
    print(f"DDL ajustado:\n{ddl_ajustado}\n")
    try:
        pg_conn.execute(text(ddl_ajustado))
    except Exception as e:
        print(f"❌ ERRO ao criar tabela '{table.name}':\n{e}\n")
        erros_criacao.append(table.name)

# === EXECUÇÃO: MIGRAR DADOS ===
erros_insercao = []

for table in metadata.sorted_tables:
    print(f"\n⬇️ Migrando dados da tabela: {table.name}")
    try:
        rows = sqlite_conn.execute(table.select()).fetchall()
        if rows:
            columns = [col.name for col in table.columns]
            dict_rows = [dict(zip(columns, row)) for row in rows]
            pg_conn.execute(table.insert(), dict_rows)
            print(f"✅ Dados inseridos: {len(rows)} registros")
        else:
            print("⚠️ Nenhum dado para migrar.")
    except Exception as e:
        print(f"❌ ERRO ao inserir dados na tabela '{table.name}':\n{e}\n")
        erros_insercao.append(table.name)

# === RESUMO FINAL ===
print("\n📦 MIGRAÇÃO CONCLUÍDA")
if not erros_criacao and not erros_insercao:
    print("✅ Todas as tabelas criadas e dados migrados com sucesso!")
else:
    print("⚠️ Migração incompleta:")
    if erros_criacao:
        print(f"  ❌ Tabelas com erro de criação: {', '.join(erros_criacao)}")
    if erros_insercao:
        print(f"  ❌ Tabelas com erro na inserção de dados: {', '.join(erros_insercao)}")
