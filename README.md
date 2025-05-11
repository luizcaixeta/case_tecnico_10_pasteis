# 🌤️ Case técnico: Extração de dados climáticos das cidades do Sul do Brasil

## Descrição do projeto

Este projeto tem como objetivo coletar, processar e carregar (para um banco de dados PostGres) dados climáticos das cidades da região Sul do Brasil, abrangendo os estados do Paraná, Santa Catarina e Rio Grande do Sul. O fluxo está dividido em três etapas principais:

### 1. Coleta de dados geográficos

Objetivo: Extrair a lista de municípios dos três estados da região Sul a partir da Wikipédia e obter suas respectivas coordenadas geográficas (latitude e longitude) via API Nominatim.

📁 cidades_sul/script:

- `get_cities.py`: Código responsável por realizar Web Scraping nas páginas da Wikipédia para extrair os nomes de todas as cidades do Paraná, Santa Catarina e Rio Grande do Sul, utilizando a biblioteca BeautifulSoup.

- `get_lat_lon.py`: Utiliza a API Nominatim para obter as coordenadas (latitude e longitude) das 1.192 cidades extraídas.

📁 cidades_sul/data

Nessa pasta, constam dois arquivos .csv: 

- `cidades_sul_brasil.csv`: Lista de cidades e o estado correspondente extraídas da Wikipédia.

- `cidades_sul_brasil_coordinates_lat_lon.csv`: Contém os mesmos dados do arquivo anterior, com a adição das coordenadas geográficas de cada cidade.

Esta etapa do projeto segue o fluxograma:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#ffffff', 'background': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#000000'}}}%%
flowchart LR
    subgraph "Fase 1: Extração"
        A[Wikipedia] -->|BeautifulSoup/Requests| B[("cidades_sul_brasil.csv"\nNomes das cidades)]
    end

    subgraph "Fase 2: Geocoding"
        B -->|Lê CSV| C{Nominatim API}
        C -->|Sucesso| D[("cidades_coordenadas.csv"\ncidade, estado, lat, long)]
        C -->|Falha| E[Fila de Retentativas]
        E -->|Repete| C
    end

    style A fill:#e6f3ff,stroke:#333
    style B fill:#e6ffe6,stroke:#333
    style C fill:#ffeb99,stroke:#333
    style D fill:#e6ffe6,stroke:#333
    style E fill:#ffcccc,stroke:#333
```


### 2. Coleta de dados climáticos: Consulta à API open-meteo para obter informações metereológicas com base nas coordenadas obtidas.

📁clima/scripts

Em `clima/scripts` está disponível o processo ETL utilizado para obter os dados climáticos de todas as cidades percentecentes a região Sul do país. 

`collect_weather.py` utiliza o arquivo `cidades_sul_brasil_coordinates_lat_lon.csv` para fazer a requisição na API open-meteo. O arquivo csv resultante (`weather_data_raw.csv`) é passado por `clean.py`, onde é realizada a limpeza e então o arquivo limpo é passado para `load.py`, onde é carregado para o banco de dados PostGres SupaBase.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#ffffff', 'background': '#ffffff', 'primaryBorderColor': '#000000', 'lineColor': '#000000'}}}%%
flowchart LR
    subgraph "Pipeline Climático"
        A[("cidades_sul_brasil_coordinates_lat_lon.csv")] --> B{collect_weather.py}
        B -->|API Open-Meteo| C[("weather_data_raw.csv")]
        C --> D{clean.py}
        D -->|Limpeza/Padronização| E[("weather_data_clean.csv")]
        E --> F{load.py}
        F -->|psycopg2| G[(SupaBase PostgreSQL)]
        C -.->|Erro na API\nRetry| B
    end

    subgraph "Detalhes do load.py"
        F --> H[Lê .env\nDB_HOST, DB_USER...]
        H --> I[Conecta via psycopg2]
        I --> J[INSERT linha-a-linha]
        J --> K[Commit transação]
    end

    style A fill:#e6ffe6,stroke:#333
    style B fill:#ffeb99,stroke:#333
    style C fill:#ffe6cc,stroke:#333
    style D fill:#ffeb99,stroke:#333
    style E fill:#e6f3ff,stroke:#333
    style F fill:#ffeb99,stroke:#333
    style G fill:#e6e6ff,stroke:#333
    style H fill:#f0f0f0,stroke:#333
    style I fill:#f0f0f0,stroke:#333
    style J fill:#f0f0f0,stroke:#333
    style K fill:#f0f0f0,stroke:#333

```

### 3. Consumindo o banco de dados 

📁 plot_clima_tempo/scripts

O banco de dados é consultado a partir do SUPABASE_URL e SUPABASE_KEY e, para testes, foram criados os códigos `prob_chuva.py`, `temperatura_maxima.py` e `temperatura_minima.py`. Esses gráficos utilizam um arquivo .shapefile da região sul, disponibilizado pelo IBGE, para delimitar o território e realizar uma interpolação, resultando em gráficos climáticos como:


<img src="https://github.com/user-attachments/assets/d5f644e7-7dae-4a44-8b64-a936b4dd14e9" width="500"/>

