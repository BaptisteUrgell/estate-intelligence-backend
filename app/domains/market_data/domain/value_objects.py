from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinates:
    lat: float
    lon: float

    def __post_init__(self):
        if not (-90 <= self.lat <= 90):
            raise ValueError(f"Latitude must be between -90 and 90. Got {self.lat}")
        if not (-180 <= self.lon <= 180):
            raise ValueError(f"Longitude must be between -180 and 180. Got {self.lon}")


@dataclass(frozen=True)
class Resolution:
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError(f"Resolution must be strictly positive. Got {self.value}")
