from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd 
from tqdm import tqdm 
import time 

#configurando tentativas extras para quando a requisição falhar 
MAX_RETRIES = 3
RETRY_DELAY = 5

#configuração do geocoder
geolocator = Nominatim(
    user_agent = "cidades_sul_brasil",
    timeout = 10
)

#adiciona rate limiting (1 requisição por segundo)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def get_coordinates(city_name, estado):
    tentativa = 0
    while tentativa < MAX_RETRIES:
        try: 
            print(f"Obtendo dados de: {city_name}, {estado}")
            #padroniza a busca para o estado do Paraná
            location = geocode(f"{city_name}, {estado}, Brazil")

            if location:
                return {
                    'estado': estado,
                    'cidade': city_name,
                    'latitude': location.latitude,
                    'longitude': location.longitude
                }

            else:
                return None
        
        except Exception as e:
            print(f"Tentativa {tentativa+1}/{MAX_RETRIES} falhou para {city_name} ({estado}): {str(e)}")
            tentativa += 1
            time.sleep(RETRY_DELAY)
        return None 
        
def main():
    #carrega a lista de cidades do sul que foi extraída do Wikipedia 
    df_cities = pd.read_csv('cidades_sul/data/cidades_sul_brasil.csv')
    cidades = df_cities.to_dict(orient='records')

    #obtém as coordenadas com barra de progresso
    resultados = []
    for entrada in tqdm(cidades, desc="Obtendo coordenadas"):
        coords = get_coordinates(entrada['cidade'], entrada['estado'])
        if coords:
            resultados.append(coords)
        time.sleep(1) 
    
    #salva os resultados
    df_result = pd.DataFrame(resultados)
    df_result.to_csv('cidades_sul/data/cidades_sul_brasil_coordinates_lat_lon.csv', index=False)

    print(f"\nProcesso concluído. {len(resultados)} cidades processadas com sucesso.")
    print(f"{len(cidades) - len(resultados)} cidades não foram encontradas.")

if __name__ == "__main__":
    main()