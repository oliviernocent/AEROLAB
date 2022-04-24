#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This script merges TCX et Hexoskin files related to the same physical activity.

USAGE:

./merge_tcx_hexoskin.py [tcx_file] [hexoskin_file]

If no file is provided, the script opens a file dialog box.
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
import easygui
from bs4 import BeautifulSoup
import pandas as pd
from aerolab_utils import *

if len(sys.argv) == 1:
    [tcx_file, hexoskin_file] = easygui.fileopenbox(title='Activity files merger', msg='Select 2 files (gpx, csv)', multiple=True, filetypes=[['*.csv', 'Hexoskin files'], ['*.gpx', 'GPX files']])
else:    
    tcx_file = sys.argv[1]
    if not path.exists(tcx_file):
        print('\nERROR:', tcx_file, 'does not exist!\n\n')
        exit(0)

    hexoskin_file = sys.argv[2]
    if not path.exists(hexoskin_file):
        print('\nERROR:', hexoskin_file, 'does not exist!\n\n')
        exit(0)

# Loads GPX data
content = open(tcx_file)
soup = BeautifulSoup(content, 'lxml')

# Retrieves time offset (seconds) according to time zone
date_string = soup.select_one('time').string[:19]
latitude = soup.select_one('latitudedegrees').string,
longitude = soup.select_one('longitudedegrees').string,

time_offset = get_time_offset(date_string, latitude, longitude)

# Parses geo data
data = []
for trackpoint in soup.select('trackpoint'):
    # Applies time offset to each date
    date_string = trackpoint.select_one('time').string[:19]
    timestamp = datetime.fromisoformat(date_string).timestamp() + time_offset
    date_string = datetime.fromtimestamp(timestamp).isoformat()

    data.append({
        'Timestamp': int(timestamp),
        'DateTime':  date_string,
        'Latitude':  trackpoint.select_one('latitudedegrees').string,
        'Longitude': trackpoint.select_one('longitudedegrees').string,
        'Altitude':  trackpoint.select_one('altitudemeters').string,
        'Cadence':   trackpoint.select_one('cadence').string,
        'Distance':  trackpoint.select_one('distancemeters').string,
        'Speed':     trackpoint.select_one('ns3\:speed').string
    })

df_geo = pd.DataFrame(data)

# Parses physiological data
data = []
df = pd.read_csv(hexoskin_file)
for i in df.index:
    timestamp = int(df.loc[i, 'time [s/256]']/256)
    date_string = datetime.fromtimestamp(timestamp).isoformat()

    if not pd.isna(df.loc[i, 'breathing_rate [rpm](/api/datatype/33/)']):
        breathing_rate = int(df.loc[i, 'breathing_rate [rpm](/api/datatype/33/)'])
    else:
        breathing_rate = None

    if not pd.isna(df.loc[i, 'minute_ventilation_adjusted [mL/min](/api/datatype/38/)']):
        ventilation = round(df.loc[i, 'minute_ventilation_adjusted [mL/min](/api/datatype/38/)'])
    else:
        ventilation = None

    if not pd.isna(df.loc[i, 'heart_rate [bpm](/api/datatype/19/)']):
        heart_rate = int(df.loc[i, 'heart_rate [bpm](/api/datatype/19/)'])
    else:
        heart_rate = None

    data.append({
        'Timestamp': int(timestamp),
        'DateTime': date_string,
        'Breathing rate (rpm)': breathing_rate,
        'Minute ventilation (mL/min)': ventilation,
        'Heart rate (bpm)': heart_rate,
    })

df_physio = pd.DataFrame(data)

# Merges data (DateTime alignment)
df_geo = df_geo[df_geo['DateTime'] >= df_physio['DateTime'][0]]
df_geo.reset_index(drop=True, inplace=True)

for i in df_geo.index:
    j = df_physio[ df_physio['DateTime'] == df_geo['DateTime'][i] ].index.values[0]

    df_geo.loc[i, 'Breathing rate (rpm)'] = df_physio.loc[j, 'Breathing rate (rpm)']
    df_geo.loc[i, 'Minute ventilation (mL/min)'] = df_physio.loc[j, 'Minute ventilation (mL/min)']
    df_geo.loc[i, 'Heart rate (bpm)'] = df_physio.loc[j, 'Heart rate (bpm)']

# Saves merged data
dirname = path.dirname(tcx_file)
df_geo.to_csv(f'{dirname}/merged_tcx_hexoskin_data.csv', sep=',', index=False)
