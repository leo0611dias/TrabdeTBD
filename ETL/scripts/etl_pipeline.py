import pandas as pd
from sqlalchemy import create_engine
import os

def run_etl(csv_path, db_url):
    try:
        print("Lendo CSV...")
        df = pd.read_csv(csv_path, sep=';')

        df = df.dropna(axis=1, how='all')

        parquet_file = 'docentes_processados.parquet'
        df.to_parquet(parquet_file, index=False)
        print(f"Arquivo Parquet gerado: {parquet_file}")

        engine = create_engine(db_url)
        df_ready = pd.read_parquet(parquet_file)
        
        print("Enviando para o PostgreSQL...")
        df_ready.to_sql('tb_docentes', engine, if_exists='replace', index=False)
        print("Carga finalizada com sucesso!")

    except Exception as e:
        print(f"Erro no pipeline: {e}")

if __name__ == "__main__":
    CSV_FILE = 'Tabela_Docente_2025.csv'
    DATABASE_URL = "postgresql+psycopg2://admin:senha123@localhost:5432/inep"
    
    run_etl(CSV_FILE, DATABASE_URL)