import csv
from datetime import datetime
from database import get_db

def importar_resultados(caminho_csv):
    conn = get_db()
    cursor = conn.cursor()
    
    total_importados = 0
    erros = []
    concursos_importados = []

    try:
        with open(caminho_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=',')
            
            for linha in reader:
                try:
                    numeros = [int(linha[f'Bola{i}']) for i in range(1, 16)]
                    if len(numeros) != 15 or any(n < 1 or n > 25 for n in numeros):
                        raise ValueError("Números inválidos")
                    
                    data_obj = datetime.strptime(linha['Data Sorteio'], '%d/%m/%Y')
                    data_sql = data_obj.strftime('%Y-%m-%d')

                    concurso = int(linha['Concurso'])

                    cursor.execute("SELECT 1 FROM resultados_oficiais WHERE concurso = ?", (concurso,))
                    if cursor.fetchone():
                        continue  # Já existe, pula
                    
                    cursor.execute('''
                        INSERT INTO resultados_oficiais (
                            concurso, data, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10,
                            n11, n12, n13, n14, n15, ganhadores_15, ganhadores_14,
                            ganhadores_13, ganhadores_12, ganhadores_11
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        concurso,
                        data_sql,
                        *sorted(numeros),
                        int(linha['Ganhadores 15 acertos'] or 0),
                        int(linha['Ganhadores 14 acertos'] or 0),
                        int(linha['Ganhadores 13 acertos'] or 0),
                        int(linha['Ganhadores 12 acertos'] or 0),
                        int(linha['Ganhadores 11 acertos'] or 0)
                    ))
                    
                    total_importados += 1
                    concursos_importados.append(concurso)

                except Exception as e:
                    erros.append(f"Concurso {linha.get('Concurso', 'N/A')}: {str(e)}")
                    continue

        conn.commit()

        return {
            "total": total_importados,
            "importados": concursos_importados,
            "erros": erros
        }

    except Exception as e:
        conn.rollback()
        raise e
