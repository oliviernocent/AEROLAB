from bs4 import BeautifulSoup
import pandas as pd
from aerolab_utils import *

# Loads XML data
content = open('data/2022-03-21/activity_8498669195.gpx')
soup = BeautifulSoup(content, 'lxml')

# Retrieves time offset (seconds) according to time zone
date_string = soup.select_one('time').string[:19]
latitude = soup.select_one('trkpt')['lat']
longitude = soup.select_one('trkpt')['lon']

time_offset = get_time_offset(date_string, latitude, longitude)

# Parses geo data
data = []
for trackpoint in soup.select('trkpt'):
    date_string = trackpoint.select_one('time').string[:19]
    timestamp = datetime.fromisoformat(date_string).timestamp() + time_offset
    date_string = datetime.fromtimestamp(timestamp).isoformat()

    data.append({
        'Timestamp': int(timestamp),
        'DateTime':  date_string,
        'Latitude':  float(trackpoint['lat']),
        'Longitude': float(trackpoint['lon']),
        'Altitude':  trackpoint.select_one('ele').string,
        # 'Distance':  trackpoint.select_one('distancemeters').string,
        # 'Speed':     trackpoint.select_one('ns3\:speed').string,
        'Cadence':   trackpoint.select_one('ns3\:cad').string
    })

df_geo = pd.DataFrame(data)

df_geo.loc[0, 'Distance'] = 0
df_geo.loc[0, 'Speed'] = 0

for i in range(1, len(df_geo.index)):
    distance = great_circle_distance(df_geo.loc[i-1, 'Latitude'], df_geo.loc[i-1, 'Longitude'], df_geo.loc[i, 'Latitude'],   df_geo.loc[i, 'Longitude'])
    df_geo.loc[i, 'Distance'] = df_geo.loc[i-1, 'Distance'] + distance

for i in range(1, len(df_geo.index)-1):
    df_geo.loc[i, 'Speed'] = ( df_geo.loc[i+1, 'Distance'] - df_geo.loc[i-1, 'Distance'] ) / ( df_geo.loc[i+1, 'Timestamp'] - df_geo.loc[i-1, 'Timestamp'] )
df_geo.loc[i+1, 'Speed'] = ( df_geo.loc[i+1, 'Distance'] - df_geo.loc[i, 'Distance'] ) / ( df_geo.loc[i+1, 'Timestamp'] - df_geo.loc[i, 'Timestamp'] )

# Parses physiological data
data = []
df = pd.read_csv('data/2022-03-21/record-241758.csv')
for i in df.index:
    timestamp = int(df.loc[i, 'time [s/256]']/256)
    date_string = datetime.fromtimestamp(timestamp).isoformat()

    if not pd.isna(df.loc[i, 'breathing_rate [rpm](/api/datatype/33/)']):
        breathing_rate = int(
            df.loc[i, 'breathing_rate [rpm](/api/datatype/33/)'])
    else:
        breathing_rate = None

    if not pd.isna(df.loc[i, 'minute_ventilation_adjusted [mL/min](/api/datatype/38/)']):
        ventilation = round(
            df.loc[i, 'minute_ventilation_adjusted [mL/min](/api/datatype/38/)'])
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

df_geo = df_geo[df_geo['DateTime'] >= df_physio['DateTime'][0]]
df_geo.reset_index(drop=True, inplace=True)

# Merges data (DateTime alignment)
for i in df_geo.index:
    j = df_physio[df_physio['DateTime'] ==
                  df_geo['DateTime'][i]].index.values[0]

    df_geo.loc[i, 'Breathing rate (rpm)'] = df_physio.loc[j, 'Breathing rate (rpm)']
    df_geo.loc[i, 'Minute ventilation (mL/min)'] = df_physio.loc[j, 'Minute ventilation (mL/min)']
    df_geo.loc[i, 'Heart rate (bpm)'] = df_physio.loc[j, 'Heart rate (bpm)']

df_geo.to_csv('reports/2022-03-21/merge_gpx_hexoskin.csv', index=False)
