#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This script merges GPX et Hexoskin files related to the same physical activity.

USAGE:

./merge_gpx_hexoskin.py [gpx_file] [hexoskin_file]

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
    merge_file = easygui.fileopenbox(title='Activity files merger', msg='Select MERGE files (csv)', multiple=False, filetypes=[['*.csv', 'merge files']])
    AQT530_file = easygui.fileopenbox(title='Activity files merger', msg='Select AQT530 files (csv)', multiple=False, filetypes=[['*.csv', 'AQT530 files']])

else:    
    merge_file = sys.argv[1]
    if not path.exists(merge_file):
        print('\nERROR:', merge_file, 'does not exist!\n\n')
        exit(0)

    AQT530_file = sys.argv[2]
    if not path.exists(AQT530_file):
        print('\nERROR:', AQT530_file, 'does not exist!\n\n')
        exit(0)

# Loads GPX data
content = open(merge_file)
soup = BeautifulSoup(content, 'lxml')

# Retrieves time offset (seconds) according to time zone
date_string = soup.select_one('time').string[:19]
latitude = soup.select_one('trkpt')['lat']
longitude = soup.select_one('trkpt')['lon']

time_offset = get_time_offset(date_string, latitude, longitude)

# Parses geo data
data = []
for trackpoint in soup.select('trkpt'):
    # Applies time offset to each date
    date_string = trackpoint.select_one('time').string[:19]
    timestamp = datetime.fromisoformat(date_string).timestamp() + time_offset
    date_string = datetime.fromtimestamp(timestamp).isoformat()

    data.append({
        'Timestamp': int(timestamp),
        'DateTime':  date_string,
        'Latitude':  float(trackpoint['lat']),
        'Longitude': float(trackpoint['lon']),
        'Altitude':  trackpoint.select_one('ele').string,
        'Cadence':   trackpoint.select_one('ns3\:cad').string
    })

df_geo = pd.DataFrame(data)


# Parses air quality data
data = []
df = pd.read_csv(AQT530_file)

df_aqt = pd.DataFrame(data)

# Merges data (DateTime alignment)
df_geo = df_geo[df_geo['DateTime'] >= df_aqt['DateTime'][0]]
df_geo.reset_index(drop=True, inplace=True)

for i in df_geo.index:
    k = df_aqt[df_aqt['DateTime'] ==
                  df_geo['DateTime'][i]].index.values[0]
    df_geo.loc[i, 'Breathing rate (rpm)'] = df_aqt.loc[k, 'Breathing rate (rpm)'] 
    df_geo.loc[i, 'Minute ventilation (mL/min)'] = df_aqt.loc[k, 'Minute ventilation (mL/min)']
    df_geo.loc[i, 'Heart rate (bpm)'] = df_aqt.loc[k, 'Heart rate (bpm)']

# Saves merged data
dirname = path.dirname(merge_file)
df_geo.to_csv(f'{dirname}/merged_gpx_hexoskin_AQT530_data.csv', sep=',', index=False)
