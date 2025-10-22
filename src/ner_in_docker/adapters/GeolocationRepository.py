import time
from typing import Optional
import requests

from ner_in_docker.ports.GeolocationService import GeolocationService


class GeolocationRepository(GeolocationService):

    def __init__(self, rate_limit_delay: float = 1.0):
        self.rate_limit_delay = rate_limit_delay
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.last_request_time = 0

    def get_coordinates(self, location_name: str) -> Optional[tuple[float, float]]:
        if not location_name or not location_name.strip():
            return None

        try:
            self._apply_rate_limit()

            params = {"q": location_name.strip(), "format": "json", "limit": 1}

            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return (lat, lon)
            else:
                return None

        except (KeyError, ValueError, IndexError, requests.exceptions.RequestException):
            return None

    def _apply_rate_limit(self):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()
