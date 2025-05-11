import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import geopandas as gpd
from shapely.geometry import Point
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from supabase import create_client, Client
from dotenv import load_dotenv 
import os

#importa as variáveis e ambiente SUPABASE_URL e SUPABASE_KEY
load_dotenv(dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env'))

#recupera a URL e a chave de acesso da API 
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

#cria o cliente Supabase para se conectar ao banco de dados
supabase: Client = create_client(url, key)

dia_semana = "Monday" #define para qual dia da semana será plotado

#consulta a tabela 'clima_cidades_sul' filtrando pela coluna 'dia_semana'
#retorna as colunas cidade, latitude, longitudee temperatura mínima
response = supabase.table('clima_cidades_sul').select(
    "cidade, latitude, longitude, temperatura_min"
).eq("dia_semana", dia_semana).execute() 

data = response.data

lats = np.array([item['latitude'] for item in data])
lons = np.array([item['longitude'] for item in data])
temps = np.array([item['temperatura_min'] for item in data])

#interpola os dados de latitude e longitude para evitar longos espaços em branco pelo mapa
margin = 1.0
min_lon, max_lon = lons.min() - margin, lons.max() + margin
min_lat, max_lat = lats.min() - margin, lats.max() + margin

#cria uma grade de pontos com a latitude e longitude interpoladas
grid_lon, grid_lat = np.meshgrid(
    np.linspace(min_lon, max_lon, 300),
    np.linspace(min_lat, max_lat, 300)
)

#interpola os dados de temperatura sobre a grade criada
grid_temp = griddata(
    (lons, lats), temps,
    (grid_lon, grid_lat),
    method='cubic'
)

#lê o shapefile da região sul (obtido no site do IBGE)
shapefile_path = "plot_clima_tempo/4mu1000gc/4mu1000gc.shp" 
regiao_sul = gpd.read_file(shapefile_path)

#cria GeoSeries de pontos da grade
pontos = [Point(x, y) for x, y in zip(grid_lon.flatten(), grid_lat.flatten())]
pontos_gdf = gpd.GeoSeries(pontos, crs="EPSG:4326")

#cria uma máscara para pontos dentro da região
mask = pontos_gdf.within(regiao_sul.unary_union)

#aplica a máscara 
masked_temp = np.full(grid_temp.shape, np.nan)
masked_temp_flat = masked_temp.flatten()
grid_temp_flat = grid_temp.flatten()
masked_temp_flat[mask.values] = grid_temp_flat[mask.values]
masked_temp = masked_temp_flat.reshape(grid_temp.shape)

#plotagem
plt.figure(figsize=(12, 10))
ax = plt.axes(projection=ccrs.PlateCarree())

#define a área de foco com base na latitude e longitude mínima e máxima
ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

#adiciona as fronteiras, costa e estados
ax.add_feature(cfeature.BORDERS)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.STATES, edgecolor='gray')

#plota a interpolação das temperaturas mínimas
contour = ax.contourf(
    grid_lon, grid_lat, masked_temp,
    levels=20, cmap='coolwarm', transform=ccrs.PlateCarree()
)

#define o título do gráfico
plt.colorbar(contour, ax=ax, label='Temperatura (°C)')
plt.title(f"Temperatura Mínima - Sul do Brasil ({dia_semana})")
plt.show()