from abc import ABC, abstractmethod
from typing import Optional


class GeolocationService(ABC):
    @abstractmethod
    def get_coordinates(self, location_name: str) -> Optional[tuple[float, float]]:
        pass
