import requests
import json
import logging

from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)

class WeatherXMAPI:
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.auth_token = None

    def authenticate(self) -> bool:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = {'username': self.username, 'password': self.password}
        try:
            r = requests.post(f'{self.host}/api/v1/auth/login', data=json.dumps(payload), headers=headers)
            if r.status_code == requests.codes.ok:
                self.auth_token = r.json()['token']
                return True
            else:
                _LOGGER.error("Authentication failed: %s", r.text)
                return False
        except requests.RequestException as e:
            _LOGGER.error("Error during authentication: %s", e)
            return False

    def get_devices(self):
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'accept': 'application/json'
        }
        try:
            r = requests.get(f'{self.host}/api/v1/me/devices', headers=headers)
            if r.status_code == requests.codes.ok:
                return r.json()
            else:
                _LOGGER.error("Failed to get devices: %s", r.text)
                return []
        except requests.RequestException as e:
            _LOGGER.error("Error fetching devices: %s", e)
            return []

    def get_forecast_data(self, device_id):
        today = datetime.now().strftime('%Y-%m-%d')
        future = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        url = f"{self.host}/api/v1/me/devices/{device_id}/forecast?fromDate={today}&toDate={future}"
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'accept': 'application/json'
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                _LOGGER.error("Failed to get forecast data: %s", response.text)
                return []
        except requests.RequestException as e:
            _LOGGER.error("Error fetching forecast data: %s", e)
            return []
