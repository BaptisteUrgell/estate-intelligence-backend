class MarketDataDomainError(Exception):
    """Base exception for the Market Data domain."""

    pass


class GridCellNotFoundError(MarketDataDomainError):
    def __init__(self, lat: float, lon: float, resolution: int):
        self.lat = lat
        self.lon = lon
        self.resolution = resolution
        super().__init__(
            f"Grid cell not found for coordinates ({lat}, {lon}) at resolution {resolution}"
        )
