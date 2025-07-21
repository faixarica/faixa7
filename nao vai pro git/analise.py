import csv

def analisar_csv(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            # Detecta formato automaticamente
            try:
                dialect = csv.Sniffer().sniff(f.read(5000))
                f.seek(0)
                tem_cabecalho = csv.Sniffer().has_header(f.read(5000))
                f.seek(0)
            except:
                dialect = None
                tem_cabecalho = False
                f.seek(0)
            
            print("="*50)
            print("ANÁLISE DO ARQUIVO CSV".center(50))
            print("="*50)
            
            # Mostra primeiras linhas
            linhas = [next(f) for _ in range(5)]
            print("\nPRIMEIRAS LINHAS:")
            for i, linha in enumerate(linhas, 1):
                print(f"{i}: {linha.strip()}")
            
            if dialect:
                print("\nINFORMAÇÕES DETECTADAS:")
                print(f"- Delimitador: '{dialect.delimiter}'")
                print(f"- Tem cabeçalho: {'Sim' if tem_cabecalho else 'Não'}")
            else:
                print("\n⚠️ Não foi possível detectar o formato automaticamente")
            
            return True
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        return False

# Uso:
analisar_csv(r'C:\Users\Daniela Franco\Documents\Projeto_lotofacil\v6\Frontend\loteria.csv')