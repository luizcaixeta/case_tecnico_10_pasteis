import pandas as pd

def transform_weather_data(input_csv, output_csv):
    #carrega os dados
    df = pd.read_csv(input_csv)

    #padroniza os nomes das colunas em snake_case
    df.columns = (
    df.columns
      .str.strip()
      .str.lower()
      .str.replace(r"[^\w\s]", "", regex=True)    #remove pontuação
      .str.replace(r"[\s\-]+", "_", regex=True)   #substitui espaços e hífens por "_"
    )

    #converte colunas para os tipos corretos
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    colunas_numericas = ['latitude', 'longitude', 'temperatura_max', 'temperatura_min', 
                         'prob_chuva_max', 'prob_chuva_min', 'quantidade_chuva',
                         'sensacao_termica_max', 'sensacao_termica_min', 'velocidade_vento_max',
                         'direcao_vento', 'duracao_sol', 'uv_max']
    df[colunas_numericas] = df[colunas_numericas].apply(pd.to_numeric, errors='coerce')

    #gera colunas extras (captra o dia da semana através do timestamp e se há chance alta de chuva por meio do prob_chuva_max)
    df['dia_semana'] = df['timestamp'].dt.day_name()
    df['chance_alta_de_chuva'] = (df['prob_chuva_max'] > 70).astype(int)

    #remove possíveis outliers
    condicoes_validas = (
        df['temperatura_max'].between(-20, 50) &
        df['temperatura_min'].between(-20, 50) &
        df['prob_chuva_max'].between(0, 100) &
        df['prob_chuva_media'].between(0, 100) &
        df['prob_chuva_min'].between(0, 100)
    )
    df = df[condicoes_validas]

    #salva o resultado
    df.to_csv(output_csv, index=False)

    return df

if __name__ == '__main__':
    caminho_entrada = 'clima/data/raw/weather_data_raw.csv'
    caminho_saida = 'clima/data/processed/weather_data_clean.csv'
    
    dados_limpos = transform_weather_data(caminho_entrada, caminho_saida)
    print(f"Transformação completa: {len(dados_limpos)} registros processados.")
