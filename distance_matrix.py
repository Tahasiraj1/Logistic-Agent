import requests

# Distance Matrix API call to OpenRouteService (OSRM)
def get_distance_matrix(coordinates):
    """Fetches distance matrix from OpenRouteService API."""
    url = f"http://router.project-osrm.org/table/v1/driving/{coordinates}?annotations=duration,distance"
    response = requests.get(url)
    response.raise_for_status() # Raise an error for bad status codes
    data = response.json()

    if data.get("code") != "Ok":
        print("Exiting due to OSRM error.")
        exit()

    durations = data.get("durations")
    distances = data.get("distances")

    print("\nDuration Matrix (in minutes):")
    for row in durations:
        print([round(x / 60, 1) if x is not None else None for x in row])

    print("\nDistance Matrix (in km):")
    for row in distances:
        print([round(x / 1000, 2) if x is not None else None for x in row])
    
    return distances