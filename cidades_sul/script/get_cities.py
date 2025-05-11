import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import pandas as pd 

#dicionário com nome dos estados da região sul do Brasil
ESTADOS = {
    "Paraná": "do_Paran%C3%A1",
    "Santa Catarina": "de_Santa_Catarina",
    "Rio Grande do Sul": "do_Rio_Grande_do_Sul"
}

#função para capturar a lista de cidades da região Sul do Brasil 
def get_cities_from_state(estado, complemento_url):
    #url da página da Wikipédia contendo uma tabela com o nome de todas as cidades de cada um dos estados
    url = f"https://pt.wikipedia.org/wiki/Lista_de_munic%C3%ADpios_{complemento_url}"

    try:
        #requisição com headers para simular navegador 
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        #encontra a tabela correta - primeira tabela da página 
        tables = soup.find_all('table', {'class': 'wikitable'})
        table = tables[0] 

        #para salvar as cidades 
        cities = []
        for row in table.find_all('tr')[1:]: #pula o cabeçalho
            cells = row.find_all('td')
            if len(cells) >= 2:
                link = cells[1].find('a')
                if link: 
                    city_name = link.get_text(strip=True)
                else:
                    city_name = cells[1].get_text(strip=True)
                #remove notas de rodapé
                city_name = city_name.split('[')[0].strip()
                cities.append({'estado': estado, 'cidade': city_name})

        return cities

    except Exception as e:
        print(f"Erro ao fazer scraping: {str(e)}")
        return []

#salva os resultados 
def save_cities_to_csv():
    cidades_do_sul = []

    for estado, url_suffix in ESTADOS.items():
        print(f"Extraindo cidades de {estado}...")
        cidades = get_cities_from_state(estado, url_suffix)
        cidades_do_sul.extend(cidades)

    df_result = pd.DataFrame(cidades_do_sul)
    df_result.to_csv('cidades_sul/data/cidades_sul_brasil.csv')

    print(f"\nProcesso concluído.")
    print(f"Extraídas {len(df_result)} cidades do sul do Brasil.")

if __name__ == '__main__':
    save_cities_to_csv()

