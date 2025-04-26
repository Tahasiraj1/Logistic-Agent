import requests

def get_coordinates(address):
    """Convert a textual address into GPS coordinates using OpenStreetMap Nominatim API."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
    }

    headers = {
        "User-Agent": "SupplyChainRouteAgent/1.0 (tahasiraj242@gmail.com)"
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    if data:
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon
    else:
        print(f"❌ No results found for: {address}")
        return None
