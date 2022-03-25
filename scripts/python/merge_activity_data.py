from sqlite3 import Timestamp
from bs4 import BeautifulSoup
import datetime
import pandas as pd

# Chargement du fichier XML
content = open('AEROLAB/data/manip_x5_climb/activity_8505136019.tcx')

# Construction de l'arborescence
soup = BeautifulSoup(content, 'lxml')

data = []

for trackpoint in soup.select('trackpoint'):
    date_string = trackpoint.select_one('time').string[:19]
    timestamp = datetime.datetime.fromisoformat(date_string).timestamp()

    data.append({
        'Timestamp': int(timestamp),
        'DateTime':  date_string,
        'Latitude':  trackpoint.select_one('latitudedegrees').string,
        'Longitude': trackpoint.select_one('longitudedegrees').string,
        'Altitude':  trackpoint.select_one('altitudemeters').string,
        'Distance':  trackpoint.select_one('distancemeters').string,
        'Speed':     trackpoint.select_one('ns3\:speed').string,
        'Cadence':   trackpoint.select_one('cadence').string
    })

df = pd.DataFrame(data)
df.to_csv('AEROLAB/data/manip_x5_climb/activity.csv', index=False)

data = []
df = pd.read_csv('AEROLAB/data/manip_x5_climb/range-2453736-G01-45359.csv')
for i in df.index:
    timestamp = int(df.loc[i, 'time [s/256]']/256)
    date_string = datetime.datetime.fromtimestamp(timestamp).isoformat()

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

df = pd.DataFrame(data)
df.to_csv('AEROLAB/data/manip_x5_climb/record.csv', index=False)
