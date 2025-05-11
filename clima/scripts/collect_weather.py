import requests 
import pandas as pd
from tqdm import tqdm 
import time 
from datetime import datetime, timedelta

MAX_RETRIES = 3 #número máximo de tentativas por cidade
RETRY_DELAY = 5 #delay em segundos entre tentativas

#função responsável por buscar os dados climáticos de uma linha do df
def fetch_weather_data(row):
    #chave de requisição do open-meteo 
    base_url = "https://api.open-meteo.com/v1/forecast"

    """
    Parâmertos de entrada:
        - latitude
        - longitude

    Parãmetros de requisição:
        - temperatura (temperature_2m)
        - sensação térmica (apparent_temperature)
        - umidade relativa (relative_humidity_2m)
        - probabilidade de precipitação (precipitation_probability)
        - velocidade do vento (wind_speed_10m)
        - direção do vento (wind_direction_10m)
    """

    start_date = datetime.today().date()
    end_date = start_date + timedelta(days = 2)

    #configurando os parâmetros que serão extraídos
    params = {
        'latitude': row['latitude'],
        'longitude': row['longitude'],
        'daily': 'temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_probability_max,precipitation_probability_mean,precipitation_probability_min,precipitation_sum,wind_speed_10m_max,wind_direction_10m_dominant,sunshine_duration,uv_index_max',
        'timezone': 'auto',
        'temperature_unit': 'celsius',
        'wind_speed_unit': 'kmh',
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    }   

    for attempt in range(MAX_RETRIES):
        try:
            #envia a requisicação a API com timeout de 20 segundos
            response = requests.get(base_url, params=params, timeout=20)
            response.raise_for_status() #levanta o erro para status HTTP != 200
            data = response.json()
            
            #print para identificar qual cidade está sendo coletada
            print(f"Coletando: {row['cidade']}")

            open_meteo_data = []

            #retorna um dicionário com os dados extraídos para a cidade
            for i in range(len(data['daily']['time'])):

                open_meteo_data.append({
                    'cidade': row['cidade'],
                    'estado': row['estado'],
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                    'timestamp': pd.to_datetime(data['daily']['time'][i]),
                    'temperatura_max': data['daily']['temperature_2m_max'][i],
                    'temperatura_min': data['daily']['temperature_2m_min'][i],
                    'prob_chuva_max': data['daily']['precipitation_probability_max'][i],
                    'prob_chuva_media': data['daily']['precipitation_probability_mean'][i],
                    'prob_chuva_min': data['daily']['precipitation_probability_min'][i],
                    'quantidade_chuva': data['daily']['precipitation_sum'][i],
                    'sensacao_termica_max': data['daily']['apparent_temperature_max'][i],
                    'sensacao_termica_min': data['daily']['apparent_temperature_min'][i],
                    'velocidade_vento_max': data['daily']['wind_speed_10m_max'][i],
                    'direcao_vento': data['daily']['wind_direction_10m_dominant'][i],
                    'duracao_sol': data['daily']['sunshine_duration'][i],
                    'uv_max': data['daily']['uv_index_max'][i]
                })

            return open_meteo_data

        except requests.exceptions.Timeout:
            print(f"Timeout na tentativa {attempt + 1} para {row['cidade']}. Tentando novamente...")
            time.sleep(RETRY_DELAY) #delay para a próxima tentativa

        except requests.exceptions.RequestException as e:
            print(f"Erro na tentativa {attempt + 1} para {row['cidade']}: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                return None #retorna None após todas as tentativas falharem

    return None 

#função principal para coleta dos dados metereológicos de todas as cidades
def collect_weather_data():
    df_coords = pd.read_csv('cidades_sul/data/cidades_sul_brasil_coordinates_lat_lon.csv')

    weather_data = []

    #itera pelas linhas do df
    for _, row in tqdm(df_coords.iterrows(), total=len(df_coords), desc="Coletando dados climáticos"):
        result = fetch_weather_data(row)
        if result:
            weather_data.extend(result)

    #constrói e retorna um df com todos os dados coletados
    df_weather = pd.DataFrame(weather_data)
    return df_weather

if __name__ == '__main__':
    df = collect_weather_data()
    print(f"Coletados {len(df)} registros.")
    df.to_csv('clima/data/raw/weather_data_raw.csv', index=False)
