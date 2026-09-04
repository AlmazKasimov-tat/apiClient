import requests
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from core.settings.environments import Environments
from core.clients.endpoints import Endpoints
from core.settings.config import Users, Timeouts
from requests.auth import HTTPBasicAuth

import allure

# Находим .env файл автоматически (ищет вверх по дереву папок)
env_file = find_dotenv()
if env_file:
    load_dotenv(env_file)
else:
    # Если не нашли, пытаемся загрузить из текущей директории
    load_dotenv()
# Временная проверка
print("=" * 50)
print(f"ENVIRONMENT = {os.getenv('ENVIRONMENT')}")
print(f"TEST_BASE_URL = {os.getenv('TEST_BASE_URL')}")
print("=" * 50)

class APIClient:
    def __init__(self):
        environment_str = os.getenv('ENVIRONMENT')

        if environment_str is None:
            raise ValueError(
                "ENVIRONMENT variable not set! "
                "Check your .env file or environment variables."
            )

        try:
            environment = Environments[environment_str.upper()]
        except KeyError:
            raise ValueError(
                f"Unsupported environment value: {environment_str}. "
                f"Use TEST or PROD"
            )

        self.base_url = self.get_base_url(environment)
        self.session = requests.Session()
        self.session.headers = {
            'Content-Type': 'application/json',
        }

    def get_base_url(self, environment: Environments) -> str:
        if environment == Environments.TEST:
            return os.getenv('TEST_BASE_URL')
        elif environment == Environments.PROD:
            return os.getenv('PROD_BASE_URL')
        else:
            raise ValueError(f"Unsupported environment value: {environment}")

    def get(self, endpoint, params=None, status_code=200):
        url = self.base_url + endpoint
        response = self.session.get(url, params=params)  # Исправлено: self.session.get
        if status_code:
            assert response.status_code == status_code
        return response.json()

    def post(self, endpoint, data=None, status_code=200):
        url = self.base_url + endpoint
        response = self.session.post(url, json=data)  # Исправлено: self.session.post
        if status_code:
            assert response.status_code == status_code
        return response.json()

    def ping(self):
        with allure.step('Ping api client'):
            url = f"{self.base_url}{Endpoints.PING_ENDPOINT.value}"
            response = self.session.get(url)
            response.raise_for_status()
        with allure.step('Assert status code'):
            assert response.status_code == 201, f"Expected status 201 but got {response.status_code}"
            return response.status_code

    def auth(self):
        with allure.step('Getting authenticate'):
            url = f"{self.base_url}{Endpoints.AUTH_ENDPOINT.value}"
            payload = {
                "username": Users.USERNAME,
                "password": Users.PASSWORD
            }
            response = self.session.post(url, json=payload)
            response.raise_for_status()
        with allure.step('Checking status code'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        token = response.json().get('token')
        with allure.step('Updating header with authorization'):
            self.session.headers.update({'Authorization': f"Bearer {token}"})

    def get_booking_by_id(self, booking_id):
        with allure.step('Getting booking by id'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"
            response = self.session.get(url)
            response.raise_for_status()
        with allure.step('Assert status code'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        return response.json()

    def delete_booking_by_id(self, booking_id):
        with allure.step('Deleting booking by id'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"
            response = self.session.delete(url, auth=HTTPBasicAuth(Users.USERNAME, Users.PASSWORD))
            response.raise_for_status()
        with allure.step('Assert status code'):
            assert response.status_code == 201, f"Expected status 201 but got {response.status_code}"
        return response.status_code == 201

    def create_booking(self, booking_data):
        with allure.step('Creating booking'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}"
            response = self.session.post(url, json=booking_data)
            response.raise_for_status()
        with allure.step('Assert status code'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        return response.json()

    def get_bookings(self, params=None):
        with allure.step('Getting bookings'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}"
            response = self.session.get(url, params=params)
            response.raise_for_status()
        with allure.step('Assert status code'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        return response.json()

    def full_update_booking(self, booking_id, booking_data):
        with allure.step('Updating booking'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"
            response = self.session.put(url, json=booking_data, auth=HTTPBasicAuth(Users.USERNAME, Users.PASSWORD))
            response.raise_for_status()
        with allure.step('Assert status code'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        return response.json()

    def partial_update_booking_by_id(self, booking_id, booking_data):
        with allure.step(f'Patching booking by id: {booking_id}'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"
            response = self.session.patch(url, json=booking_data, auth=HTTPBasicAuth(Users.USERNAME, Users.PASSWORD))
            response.raise_for_status()
        with allure.step('Assert status code'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        return response.json()