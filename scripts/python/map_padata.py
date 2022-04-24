#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This script generates a map from a physical activity CSV file drawing a polyline of GPS trackpoints.
The line colour depends of the chosen column.

USAGE:

./map_padata.py [csv_file] [colum_name]

If no csv_file is provided, the script opens a file dialog box.
'''

__author__     = "Olivier Nocent and Quentin Martinet"
__copyright__  = "Copyright 2021, Université de Reims Champagne Ardenne"
__license__    = "MIT"
__version__    = "0.0.1"
__maintainer__ = "Olivier Nocent"
__email__      = "olivier.nocent@univ-reims.fr"
__status__     = "Experimental"

import sys
from os import path
import pandas as pd
import json
import folium
import easygui
from aerolab_utils import *

if len(sys.argv) == 1:
    csv_file = easygui.fileopenbox(title='Activity mapper', msg='Select a physical activity data file', filetypes=[
                                   ['*.csv', 'Hexoskin files']])
    column_name = 'Speed'
else:
    csv_file = sys.argv[1]
    if not path.exists(csv_file):
        print('\nERROR:', csv_file, 'does not exist!\n\n')
        exit(0)

    if len(sys.argv) == 3:
        column_name = sys.argv[2]
    else:
        column_name = 'Speed'


# Loads a color scale from JSON file
# https://cran.r-project.org/web/packages/viridis/vignettes/intro-to-viridis.html
with open('scripts/python/palette/magma.json', 'r') as f:
    palette = json.load(f)

df = pd.read_csv(csv_file)

latitude_center = df['Latitude'].mean()
longitude_center = df['Longitude'].mean()

min = df[column_name].min()
max = df[column_name].max()

# Création d'une carte
fmap = folium.Map(location=[latitude_center, longitude_center],
                  tiles='OpenStreetMap', zoom_start=10)

# Ajout d'un marqueur
folium.Marker([df['Latitude'][0], df['Longitude'][0]],
              popup='Départ',
              icon=folium.Icon(color='green')).add_to(fmap)

points = list(zip(df['Latitude'], df['Longitude']))
folium.PolyLine(points, lineCap='butt', color='black',
                weight=14, opacity=1).add_to(fmap)

for i in range(1, len(df.index)):
    weight = int(map(df[column_name][i], min, max, 0, len(palette)-1))

    points = [
        (df['Latitude'][i-1], df['Longitude'][i-1]),
        (df['Latitude'][i], df['Longitude'][i])
    ]
    folium.PolyLine(points, linecap='butt',
                    color=palette[weight], weight=8, opacity=1).add_to(fmap)

# Génération du fichier HTML contenant la carte
fmap.save(f'{csv_file[:-3]}html')
