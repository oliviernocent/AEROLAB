#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This script computes the max mean mass concentration of several pollutants
from CSV a file containing the following columns :
    - 'DateTime' : ISO 8601 date and time 
    - 'Timestamp': seconds elapsed since 01/01/1970
    - 'P10 (µg/m3)' (optional)
    - 'P25 (µg/m3)' (optional)
    - 'NO2 (µg/m3)' (optional)
    - 'CO (mg/m3)'  (optional)
    - 'O3 (µg/m3)'  (optional)
'''

__author__ = "Olivier Nocent and Quentin Martinet"
__copyright__ = "Copyright 2021, Université de Reims Champagne Ardenne"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Olivier Nocent"
__email__ = "olivier.nocent@univ-reims.fr"
__status__ = "Experimental"

from os import path
import sys
import easygui
import glob
import pandas as pd
from aerolab_utils import *

if len(sys.argv) == 1:
    filename = easygui.fileopenbox(
        title='Exposure estimation', msg='Choose a CSV file', filetypes=[['*.csv', 'CSV files']])
else:
    filename = sys.argv[1]
    if not path.exists(filename):
        print('\nERROR:', filename, 'does not exist!\n\n')
        exit(0)

df = pd.read_csv(filename)

pollutants = ['PM10 (µg/m3)', 'PM2.5 (µg/m3)', 'NO2 (µg/m3)',
              'CO (mg/m3)', 'O3 (µg/m3)']
max_value = {}
max_index = {}
for pollutant in pollutants:
    max_value[pollutant] = 0
    max_index[pollutant] = 0

i, end = 0, df['Timestamp'].iloc[-1] - 24 * 3600
while df.loc[i, 'Timestamp'] < end:
    start = df.loc[i, 'Timestamp']
    df_24h = df[(df['Timestamp'] >= start) & (
        df['Timestamp'] < start + 24 * 3600)]

    for pollutant in pollutants:
        if pollutant in df.columns:
            mean_value = df_24h[pollutant].mean()
            if mean_value > max_value[pollutant]:
                max_value[pollutant] = mean_value
                max_index[pollutant] = i

    i += 1

if 'O3 (µg/m3)' in df.columns:
    i, end = 0, df['Timestamp'].iloc[-1] - 8 * 3600
    while df.loc[i, 'Timestamp'] < end:
        start = df.loc[i, 'Timestamp']
        df_8h = df[(df['Timestamp'] >= start) & (
            df['Timestamp'] < start + 8 * 3600)]

        mean_value = df_24h['O3 (µg/m3)'].median()
        if mean_value > max_value['O3 (µg/m3)']:
            max_value['O3 (µg/m3)'] = mean_value
            max_index['O3 (µg/m3)'] = i

        i += 1

print('\nMaximum mean mass concentration during 24h:\n')
if 'PM10 (µg/m3)' in df.columns:
    print('PM10  :', round(max_value['PM10 (µg/m3)'], 3),
          'µg/m3\t\t(45 µg/m3) at', df['DateTime'][max_index['PM10 (µg/m3)']])
if 'PM2.5 (µg/m3)' in df.columns:
    print('PM2.5 :', round(max_value['PM2.5 (µg/m3)'], 3),
          'µg/m3\t\t(15 µg/m3) at', df['DateTime'][max_index['PM2.5 (µg/m3)']])
if 'NO2 (µg/m3)' in df.columns:
    print('NO2   :', round(max_value['NO2 (µg/m3)'], 3),
          'µg/m3\t\t(25 µg/m3) at', df['DateTime'][max_index['NO2 (µg/m3)']])
if 'CO (mg/m3)' in df.columns:
    print('CO    :', round(max_value['CO (mg/m3)'], 3),
          'mg/m3\t\t( 4 mg/m3) at', df['DateTime'][max_index['CO (mg/m3)']])
if 'O3 (µg/m3)' in df.columns:
    print('\nMaximum mean mass concentration during 8h:\n')
    print('O3    :', round(max_value['O3 (µg/m3)'], 3),
          'µg/m3\t\t(100 µg/m3) at', df['DateTime'][max_index['O3 (µg/m3)']])
