import requests
import json

from requests import Response


class RestAPI:
    def __init__(self, base_url):
        self.base_url = base_url

    def post(self, params):
        response: Response = requests.post(f'{self.base_url}', json=params)
        return response
