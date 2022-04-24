# -*- coding: utf-8 -*-
'''
This library provides several utility functions to deal with time and conversions.
'''

__author__     = "Olivier Nocent and Quentin Martinet"
__copyright__  = "Copyright 2021, Université de Reims Champagne Ardenne"
__license__    = "MIT"
__version__    = "0.0.1"
__maintainer__ = "Olivier Nocent"
__email__      = "olivier.nocent@univ-reims.fr"
__status__     = "Experimental"

from math import *
from datetime import *
import requests
from credentials import *



def compute_duration(start: str, end: str) -> int:
    '''
    Computes duration between two dates.

    Parameters:
        start (string): ISO 8601 start date.
        end (string): ISO 8601 end date.

    Returns:
        duration (int): expressed in seconds.
    '''

    duration = datetime.fromisoformat(end) - datetime.fromisoformat(start) 
    return duration.total_seconds()


def format_duration(total: int) -> str:
    '''
    Converts a duration in seconds into a human readable string.

    Parameters:
        total (int): total duration in seconds

    Returns:
        human readable text (str)
    '''
    if total >= 60 * 60 * 24:
        days  = total // (60 * 60 * 24)
        hours = (total % (60 * 60 * 24)) // (60 * 60)
        return f'{days} days and {hours} hours' 
    elif total >= 60 * 60:
        hours = total // (60 * 60)
        minutes = (total % (60 * 60)) // 60
        return f'{hours} hours and {minutes} minutes'
    elif total >= 60:
        minutes = total // 60
        seconds = total % 60
        return f'{minutes} minutes and {seconds} seconds'
    else:
        return f'{total} seconds' 



def get_solar_data(date: str, latitude: float, longitude: float) -> dict:
    '''
    Retrieves solar paremeters (sunrise, sunset, day length, ...).

    Parameters:
        date (string): ISO 8601 date.
        latitude (float): expressed in decimal degrees.
        longitude (float): expressed in decimal degrees.

    Returns:
        parameters (dict): dictionary with 'sunrise', 'sunset' and 'day_length' keys.
    '''
    
    parameters = {
        'lat' : latitude,
        'long': longitude,
        'date': date[0:10],
        'formatted': 0
    }

    response = requests.get('https://api.sunrise-sunset.org/json', params=parameters)

    if response.status_code == 200:
        data = response.json()

        return {
            'sunrise': time.fromisoformat(data['results']['sunrise'][11:19]),
            'sunset': time.fromisoformat(data['results']['sunset'][11:19]),
            'day_length': data['results']['day_length']
        }
    else:
        print('ERROR ' + response.status_code + ': ' + response.reason)



def get_time_offset(date: str, latitude: float, longitude: float) -> int:
    '''
    Retrieves the time offset of the corresponding time zone.

    Parameters:
        date (string): ISO 8601 date.
        latitude (float): expressed in decimal degrees.
        longitude (float): expressed in decimal degrees.

    Returns:
        offset (int): time offset expressed in seconds.
    '''
    
    parameters = {
        'key': TIMEZONEDB_API_KEY,
        'format': 'json',
        'by': 'position',
        'lat': latitude,
        'lng': longitude,
        'time': int(datetime.fromisoformat(date).timestamp())
    }

    response = requests.get('http://api.timezonedb.com/v2.1/get-time-zone', params=parameters)

    if response.status_code == 200:
        return response.json()['gmtOffset']
    else:
        print('ERROR ' + response.status_code + ': ' + response.reason)



def great_circle_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    '''
    Computes the great circle distance between two locations P1 and P2 on Earth
    using the Vincenty formula.
    https://en.wikipedia.org/wiki/Great-circle_distance#Formulas

    Parameters:
        lat1 (float): latitude of P1, expressed in decimal degrees.
        lon1 (float): longitude of P1, expressed in decimal degrees.
        lat2 (float): latitude of P2, expressed in decimal degrees.
        lon2 (float): longitude of P2, expressed in decimal degrees.

    Returns:
        distance (float), expressed in meters.
    '''
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    dLon = radians(fabs(lon2-lon1))

    cosLat1 = cos(lat1)
    sinLat1 = sin(lat1)
    cosLat2 = cos(lat2)
    sinLat2 = sin(lat2)
    cosDLon = cos(dLon)
    sinDLon = sin(dLon)

    A = cosLat2 * sinDLon
    B = cosLat1 * sinLat2 - sinLat1 * cosLat2 * cosDLon

    return 6371009 * atan2(sqrt(A * A + B * B),
                     sinLat1 * sinLat2 + cosLat1 * cosLat2 * cosDLon)
                     


def ppm_to_mass(ppm: float, temperature: float, pressure: float, molar_mass: float) -> float:
    '''
    Computes the mass concentration of a given gas based on
    https://www.lenntech.com/calculators/ppm/converter-parts-per-million.htm

    Parameters:
        ppm (float): parts per million.
        temperature (float): expressed in °C.
        pressure (float): expressed in hPa.
        molar_mass (float): molar mass of the gas expressed in g/mol.

    Returns:
        concentration (float): expressed in µg/m3.       
    '''

    return ppm * pressure * 0.1 * molar_mass / (8.31451 * (temperature + 273.15))



def map(x: float, x_min: float, x_max: float, y_min: float, y_max: float) -> float:
    '''
    Re-maps linearly a number from one range to another.
    
    Parameters:
        x (float): input value.
        x_min (float): min value of the input range.
        x_max (float): max value of the input range.
        y_min (float): min value of the output range.
        y_max (float): max value of the output range.

    Returns
        Re-mapped value (float)
    '''
    return y_min + (y_max - y_min) * ((x - x_min) / (x_max - x_min))
