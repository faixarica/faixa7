from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql import func
import datetime

# === STRING DE CONEXÃO AO POSTGRES ===
POSTGRES_URL = 'postgresql://neondb_owner:npg_Lqjh6vGBVi5r@ep-black-hill-acpnaibc-pooler.sa-east-1.aws.neon.tech/Faixabs?sslmode=require&channel_binding=require'

engine = create_engine(POSTGRES_URL)
metadata = MetaData()

def criar_tabelas_postgres():
    try:
        print("🔧 Criando tabelas no PostgreSQL (Neon)...")

        Table('planos', metadata,
              Column('id', Integer, primary_key=True),
              Column('nome', Text, nullable=False),
              Column('palpites_dia', Integer, nullable=False),
              Column('valor', Float, nullable=False),
              Column('validade_dias', Integer, nullable=False),
              Column('bonus', Text),
              Column('status', Text, default='A')
        )

        Table('usuarios', metadata,
              Column('id', Integer, primary_key=True),
              Column('nome_completo', Text, nullable=False),
              Column('email', Text, nullable=False, unique=True),
              Column('usuario', Text, nullable=False, unique=True),
              Column('senha', Text, nullable=False),
              Column('tipo', Text, default='U'),
              Column('id_plano', Integer, ForeignKey('planos.id'), default=1),
              Column('ativo', Boolean, default=True),
              Column('telefone', Text),
              Column('data_nascimento', Text),
              Column('dt_cadastro', DateTime, default=func.now())
        )

        Table('client_plans', metadata,
              Column('id', Integer, primary_key=True),
              Column('id_client', Integer, ForeignKey('usuarios.id')),
              Column('id_plano', Integer, ForeignKey('planos.id')),
              Column('data_inclusao', DateTime, default=func.now()),
              Column('data_expira_plan', DateTime),
              Column('palpites_dia_usado', Integer, default=0),
              Column('ativo', Boolean)
        )

        Table('resultados_oficiais', metadata,
              Column('concurso', Integer, primary_key=True),
              Column('data', Text, nullable=False),
              *[Column(f'n{i}', Integer) for i in range(1, 16)],
              Column('ganhadores_15', Integer),
              Column('ganhadores_14', Integer),
              Column('ganhadores_13', Integer),
              Column('ganhadores_12', Integer),
              Column('ganhadores_11', Integer)
        )

        Table('palpites', metadata,
              Column('id', Integer, primary_key=True),
              Column('id_usuario', Integer, ForeignKey('usuarios.id')),
              Column('numeros', Text, nullable=False),
              Column('modelo', Text, nullable=False),
              Column('data', DateTime, default=func.now()),
              Column('status', Text),
              Column('premiado', Text, default='N'),
              Column('concurso_premio', Integer)
        )

        Table('financeiro', metadata,
              Column('id', Integer, primary_key=True),
              Column('id_cliente', Integer, ForeignKey('usuarios.id')),
              Column('id_plano', Integer, ForeignKey('planos.id')),
              Column('data_pagamento', Text),
              Column('forma_pagamento', Text),
              Column('valor', Float),
              Column('data_validade', Text),
              Column('estorno', Text, default='N'),
              Column('data_estorno', Text, default=datetime.datetime.now().isoformat())
        )

        Table('log_user', metadata,
              Column('id', Integer, primary_key=True),
              Column('id_cliente', Integer, ForeignKey('usuarios.id')),
              Column('data_hora', Text),
              Column('ip', Text),
              Column('hostname', Text),
              Column('city', Text),
              Column('region', Text),
              Column('country', Text),
              Column('loc', Text),
              Column('org', Text),
              Column('postal', Text),
              Column('timezone', Text)
        )

        Table('loterias', metadata,
              Column('id', Integer, primary_key=True),
              Column('nome_loteria', Text),
              Column('num_premio', Integer),
              Column('aposta', Integer)
        )

        metadata.create_all(engine)
        print("✅ Tabelas criadas com sucesso!")

    except ProgrammingError as e:
        print(f"❌ Erro ao criar tabelas: {str(e)}")

# Execução direta
if __name__ == "__main__":
    criar_tabelas_postgres()
