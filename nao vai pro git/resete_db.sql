import sqlite3
import os

def resetar_banco_dados():
    # Remove o arquivo do banco de dados se existir
    if os.path.exists('database.db'):
        os.remove('database.db')
        print("✅ Banco de dados antigo removido")
    
    # Cria um novo banco de dados
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Cria a tabela com a estrutura correta
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
    print("✅ Novo banco de dados criado com estrutura correta")

if __name__ == "__main__":
    resetar_banco_dados()