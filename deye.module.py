import requests
import hashlib
import json

from dotenv import load_dotenv  # pip install python-dotenv
import os

load_dotenv()

TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'deye_access_token.txt')

api_url = os.getenv('DEYE_API_URL')
app_id = os.getenv('DEYE_APP_ID')
app_secret = os.getenv('DEYE_APP_SECRET')
user_email = os.getenv('DEYE_USER_EMAIL')
user_password = os.getenv('DEYE_USER_PASSWORD')

if not api_url or not app_id or not app_secret or not user_email or not user_password:
    raise ValueError('Please set your environment variables (.env file or system variables)')


class Station:
    """ Deye Station class """

    def __init__(self, id, name, locationLat, locationLng, locationAddress, regionNationId, regionTimezone,
                 gridInterconnectionType, installedCapacity, startOperatingTime, createdDate, batterySOC,
                 connectionStatus, generationPower, lastUpdateTime, contactPhone, ownerName):
        self.id = id
        self.name = name
        self.locationLat = locationLat
        self.locationLng = locationLng
        self.locationAddress = locationAddress
        self.regionNationId = regionNationId
        self.regionTimezone = regionTimezone
        self.gridInterconnectionType = gridInterconnectionType
        self.installedCapacity = installedCapacity
        self.startOperatingTime = startOperatingTime
        self.createdDate = createdDate
        self.batterySOC = batterySOC
        self.connectionStatus = connectionStatus
        self.generationPower = generationPower
        self.lastUpdateTime = lastUpdateTime
        self.contactPhone = contactPhone
        self.ownerName = ownerName


class StationData:
    """ Deye Station Data class """

    def __init__(self, code, msg, success, requestId, generationPower, consumptionPower, gridPower, purchasePower,
                 wirePower, chargePower, dischargePower, batteryPower, batterySOC, irradiateIntensity, lastUpdateTime):
        self.code = code
        self.msg = msg
        self.success = success
        self.requestId = requestId
        self.generationPower = generationPower
        self.consumptionPower = consumptionPower
        self.gridPower = gridPower
        self.purchasePower = purchasePower
        self.wirePower = wirePower
        self.chargePower = chargePower
        self.dischargePower = dischargePower
        self.batteryPower = batteryPower
        self.batterySOC = batterySOC
        self.irradiateIntensity = irradiateIntensity
        self.lastUpdateTime = lastUpdateTime


def get_access_token():
    """
    Get access token from Deye API
    :return: access token
    """
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "appSecret": app_secret,
        "email": user_email,
        "password": hashlib.sha256(user_password.encode()).hexdigest()
    }
    try:
        response = requests.post(f'{api_url}/v1.0/account/token?appId={app_id}', headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        if response_data.get('success'):
            return response_data.get('accessToken')
        else:
            raise ValueError('Failed to get access token')

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def refresh_access_token():
    global access_token
    access_token = get_access_token()
    if not access_token:
        raise ValueError('Failed to obtain access token')
    with open(TOKEN_PATH, 'w') as file:
        file.write(access_token)
    return access_token


def get_station_list(access_token):
    """
    Get stations
    :return: list of devices
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    data = {
        "page": 1,
        "size": 10
    }
    try:
        response = requests.post(f'{api_url}/v1.0/station/list', headers=headers, json=data)
        response_data = json.loads(response.text)
        if response_data.get('success'):
            station_list = response_data.get('stationList', [])
            stations = [Station(**station) for station in station_list]
            return stations
        elif response_data.get('success') == False and response_data.get('msg') == 'auth invalid token':
            access_token = refresh_access_token()
            return get_station_list(access_token)
        else:
            raise ValueError('Failed to get station devices')
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def get_station_latest(access_token, station_id):
    """
    Get latest data of a station
    :param station_id: station id
    :return: latest data
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    data = {
        "stationId": station_id
    }
    try:
        response = requests.post(f'{api_url}/v1.0/station/latest', headers=headers, json=data)
        response_data = json.loads(response.text)
        if response_data.get('success'):
            return StationData(**response_data)
        elif response_data.get('success') == False and response_data.get('msg') == 'auth invalid token':
            access_token = refresh_access_token()
            return get_station_latest(access_token, station_id)
        else:
            raise ValueError('Failed to get station latest data')
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def main():
    global access_token
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'r') as file:
            access_token = file.read()
    else:
        access_token = get_access_token()
        with open(TOKEN_PATH, 'w') as file:
            file.write(access_token)

    station_list = get_station_list(access_token)
    if len(station_list) == 0:
        raise ValueError('No DEYE station found')

    data = {}
    for station in station_list:
        station_data = get_station_latest(access_token, station.id)
        data[station.id] = {
            'battery_power': float(station_data.batteryPower or 0),
            'battery_soc': float(station_data.batterySOC or 0),
            'charge_power': float(station_data.chargePower or 0),
            'consumption_power': float(station_data.consumptionPower or 0),
            'discharge_power': float(station_data.dischargePower or 0),
            'generation_power': float(station_data.generationPower or 0),
            'grid_power': float(station_data.gridPower or 0),
            'irradiate_intensity': float(station_data.irradiateIntensity or 0),
            'last_update_time': float(station_data.lastUpdateTime or 0),
            'purchase_power': float(station_data.purchasePower or 0),
            'station_name': station.name or "",
            'wire_power': float(station_data.wirePower or 0)
        }

    json_data = json.dumps(data, indent=4)
    print(json_data)


if __name__ == "__main__":
    main()
