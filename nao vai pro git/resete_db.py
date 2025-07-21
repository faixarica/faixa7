import sqlite3
import os
import time

def resetar_banco_dados():
    # Tentativa de remover o arquivo com tratamento de erro
    db_file = 'database.db'
    
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print("✅ Banco de dados antigo removido com sucesso")
        except PermissionError:
            print("⚠️  Não foi possível remover o arquivo. Tente:")
            print("1. Fechar todos os programas")
            print("2. Reiniciar o computador")
            print("3. Executar este script como Administrador")
            return False
    
    # Criar novo banco de dados
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE resultados_oficiais (
                concurso INTEGER PRIMARY KEY,
                data TEXT NOT NULL,
                n1 INTEGER NOT NULL, n2 INTEGER NOT NULL, n3 INTEGER NOT NULL,
                n4 INTEGER NOT NULL, n5 INTEGER NOT NULL, n6 INTEGER NOT NULL,
                n7 INTEGER NOT NULL, n8 INTEGER NOT NULL, n9 INTEGER NOT NULL,
                n10 INTEGER NOT NULL, n11 INTEGER NOT NULL, n12 INTEGER NOT NULL,
                n13 INTEGER NOT NULL, n14 INTEGER NOT NULL, n15 INTEGER NOT NULL,
                ganhadores_15 INTEGER NOT NULL DEFAULT 0,
                ganhadores_14 INTEGER NOT NULL DEFAULT 0,
                ganhadores_13 INTEGER NOT NULL DEFAULT 0,
                ganhadores_12 INTEGER NOT NULL DEFAULT 0,
                ganhadores_11 INTEGER NOT NULL DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Novo banco de dados criado com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar novo banco: {str(e)}")
        return False

if __name__ == "__main__":
    if resetar_banco_dados():
        print("Banco resetado com sucesso! Agora execute o importador.py")
    else:
        print("Falha ao resetar o banco. Veja as mensagens acima.")