import os 
import psycopg2
import pandas as pd 
from dotenv import load_dotenv 

#utiliza o arquivo .env para acessar o banco de dados
load_dotenv(dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env'))

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

#função para salvar os dados extraídos no banco de dados
def salvar_no_db(input_csv: str):
    df = pd.read_csv(input_csv)
    conn = psycopg2.connect(
        host = DB_HOST,
        port = DB_PORT,
        database = DB_NAME,
        user = DB_USER,
        password = DB_PASS
    )
    cursor = conn.cursor()

    try:
        for _, row in df.iterrows():
            #adiciona nas colunas de mesmo nome das que foram extraídas pelo open-meteo
            #transforma a coluna chance_alta_de_chuva em booleano
            cursor.execute(
                """
                INSERT INTO clima_cidades_sul (
                    cidade, estado, latitude, longitude, timestamp,
                    temperatura_max, temperatura_min, prob_chuva_max, prob_chuva_media,
                    prob_chuva_min, quantidade_chuva, sensacao_termica_max,
                    sensacao_termica_min, velocidade_vento_max, direcao_vento,
                    duracao_sol, uv_max, dia_semana, chance_alta_de_chuva
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    row['cidade'], row['estado'], row['latitude'], row['longitude'], row['timestamp'],
                    row['temperatura_max'], row['temperatura_min'], row['prob_chuva_max'], row['prob_chuva_media'],
                    row['prob_chuva_min'], row['quantidade_chuva'], row['sensacao_termica_max'],
                    row['sensacao_termica_min'], row['velocidade_vento_max'], row['direcao_vento'],
                    row['duracao_sol'], row['uv_max'], row['dia_semana'], bool(row['chance_alta_de_chuva'])  
                )
            )
    except Exception as e:
        print(f"Erro ao inserir linha: {e}")
    else:
        conn.commit()

    cursor.close()
    conn.close()

if __name__ == "__main__":
    salvar_no_db('clima/data/processed/weather_data_clean.csv')
    print("Dados carregados no banco com sucesso!")