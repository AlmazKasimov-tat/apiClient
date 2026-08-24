import requests
import os
from dotenv import load_dotenv
from core.settings.enviroments import Enviroments

load_dotenv()

class APUClient:
    def __init__(self):
        environment_str = os.getenv('ENVIRONMENT')
        try:
            environment = Enviroments[environment_str]
        except KeyError:
            raise ValueError(f"Unsupported environment value: {environment_str}")

        self.base_url = self.get_base_url(environment)
        self.headers = {
            'Content-Type': 'application/json',
        }

    def get_base_url(self, environment: Enviroments) -> str:
        if environment == Enviroments.TEST:
            return os.getenv('TEST_BASE_URL')
        elif environment == Enviroments.PROD:
            return os.getenv('PROD_BASE_URL')
        else:
            raise ValueError(f"Unsupported environment value: {environment}")

    def get(self, endpoint, params=None, status_code=200):
        url = self.base_url + endpoint
        response = requests.get(url, headers=self.headers, params=params)
        if status_code:
            assert response.status_code == status_code
        return response.json()

    def post(self, endpoint, data=None, status_code=200):
        url = self.base_url + endpoint
        response = requests.post(url, headers=self.headers, json=data)
        if status_code:
            assert response.status_code == status_code
        return response.json()