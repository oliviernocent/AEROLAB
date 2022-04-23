import pandas as pd
import json
import folium

def map(x: float, x_min: float, x_max: float, y_min: float, y_max: float) -> float:
    return y_min + (y_max - y_min) * ((x - x_min) / (x_max - x_min))

# Loads a color scale from JSON file
# https://cran.r-project.org/web/packages/viridis/vignettes/intro-to-viridis.html
with open('AEROLAB/scripts/python/palette/magma.json', 'r') as f:
  palette = json.load(f)

df = pd.read_csv('AEROLAB/reports/2022-03-21/merge_gpx_hexoskin.csv')

latitude_center = df['Latitude'].mean()
longitude_center = df['Longitude'].mean()

heartrate_min = df['Heart rate (bpm)'].min()
heartrate_max = df['Heart rate (bpm)'].max()

# Création d'une carte
fmap = folium.Map(location=[latitude_center, longitude_center], tiles='OpenStreetMap', zoom_start=10)

# Ajout d'un marqueur
folium.Marker([df['Latitude'][0], df['Longitude'][0]],
              popup='Départ',
              icon=folium.Icon(color='green')).add_to(fmap)

points = list(zip(df['Latitude'], df['Longitude']))
folium.PolyLine(points, lineCap='butt', color='black', weight=14, opacity=1).add_to(fmap)

for i in range(1, len(df.index)):
    #weight = int(map(df['Heart rate (bpm)'][i], 50, 200, 0, len(palette)-1))
    weight = int(map(df['Altitude'][i], 50, 300, 0, len(palette)-1))
    
    points = [
        (df['Latitude'][i-1], df['Longitude'][i-1]),
        (df['Latitude'][i], df['Longitude'][i])
    ]
    folium.PolyLine(points, linecap='butt', color=palette[weight], weight=8, opacity=1).add_to(fmap)

# Génération du fichier HTML contenant la carte
fmap.save('AEROLAB/reports/2022-03-21/map_gpx_hexoskin_data.html')




