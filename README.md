# Deye Cloud Python Plugin for Zabbix Agent Integration

This project provides a Python plugin to integrate Deye Cloud data with the Zabbix agent. It retrieves data from the Deye Cloud API and formats it for monitoring in Zabbix.

## Features

- Fetch access token from Deye API
- Retrieve list of Deye stations
- Get latest data for each station
- Format data for Zabbix monitoring

## Requirements

- Python 3.x
- Python `python-dotenv`, `requests`, `hashlib`, `json` libraries.
- Registered [Deye Cloud](https://developer.deyecloud.com/home) accont.
- Registered [application](https://developer.deyecloud.com/app) on Deye Cloud with `AppId` and `AppSecret`.
- Configured [Zabbix agent](https://www.zabbix.com/download_agents)

## Installation and usage

1. Clone the repository.
2. Install the required libraries:
    ```sh
    pip install requests python-dotenv
    ```
3. Create a `.env` file in the project directory with the following variables:
    ```env
    DEYE_API_URL=<your_deye_api_url>
    DEYE_APP_ID=<your_app_id>
    DEYE_APP_SECRET=<your_app_secret>
    DEYE_USER_EMAIL=<your_user_email>
    DEYE_USER_PASSWORD=<your_user_password>
    ```
4. Modify your Zabbix agent configuration file to include the path to the Python script:
    ```conf    
    UserParameter=deye.station.data,/usr/bin/python3 /path/to/deye.module.py
    ``` 
5. Restart the Zabbix agent:
    ```sh
    sudo systemctl restart zabbix-agent
    ```
## Zabbix configuration

1. Add new Item to the host in Zabbix:
    - Name: `Deye Station Data`
    - Type: `Zabbix agent`
    - Key: `deye.station.data`
    - Type of information: `Text`
    - Update interval: `1m`
    - Host interface: `your-zabbix-agent-ip:10050-or-your-custom-port`
2. Add new Dependent item to the host in Zabbix for Battery SOC:
    - Name: `Battery SOC`
    - Type: `Dependent item`
    - Key (unique key for each parameter): `battery.soc` 
    - Type of information: `Numeric (unsigned)`
    - Master item: `zabbix.agent.hostname:Deye Station Data`
    - Preprocessing steps (#61192223 is unique station id from Deye Cloud): `JSONPath:$.61192223.battery_soc` 
    - Preprocessing type of information: `Numeric (unsigned)`
3. Add new Dependent item to the host in Zabbix for Wired Power:
    - Name: `Battery Wired Power`
    - Type: `Dependent item`
    - Key (unique key for each parameter): `battery.wire_power`
    - Type of information: `Numeric (float)`
    - Master item: `zabbix.agent.hostname:Deye Station Data`
    - Units: `W`
    - Preprocessing steps (61192223 is unique station id from Deye Cloud): `JSONPath:$.61192223.wire_power` 
    - Preprocessing type of information: `Numeric (float)` 

Add other dependent items for other parameters like `battery.soc`, `battery.wired_power`

## Example of JSON output 
```json
{
   "61192223": {
      "battery_power": -11.0,
      "battery_soc": 100.0,
      "charge_power": 0.0,
      "consumption_power": 1762.0,
      "discharge_power": 0.0,
      "generation_power": 0.0,
      "grid_power": 0.0,
      "irradiate_intensity": 0.0,
      "last_update_time": 1732385970.0,
      "purchase_power": 0.0,
      "station_name": "Your Station Name",
      "wire_power": 1847.0
   }
}
```
       
## Additional information

- [DeyeCloud API documentation](https://developer.deyecloud.com/start)
