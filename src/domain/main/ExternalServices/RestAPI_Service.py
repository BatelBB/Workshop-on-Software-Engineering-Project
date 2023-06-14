import requests
from requests import Response
from requests.exceptions import RequestException


from src.domain.main.Utils.Logger import report_error


class RestAPI:
    def __init__(self, base_url):
        self.base_url = base_url

    def post(self, params, timeout=None):
        try:
            response: Response = requests.post(f'{self.base_url}', params, timeout=timeout)
            return response
        except RequestException as e:
            report_error(__name__, f"Request failed due to: {str(e)}")
            return None


