"""
Validation utilities
"""

def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate latitude and longitude"""
    if lat is None or lon is None:
        return False
    
    try:
        lat = float(lat)
        lon = float(lon)
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except (TypeError, ValueError):
        return False


def validate_units(units: str) -> bool:
    """Validate temperature units"""
    return units in ['metric', 'imperial']


def validate_location_name(name: str) -> bool:
    """Validate location name"""
    return isinstance(name, str) and 2 <= len(name) <= 100
