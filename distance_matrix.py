import requests
import os
import json

# # Distance Matrix API call to OpenRouteService (OSRM)
# def get_distance_matrix(coordinates):
#     """Fetches distance matrix from OpenRouteService API."""
#     url = f"http://router.project-osrm.org/table/v1/driving/{coordinates}?annotations=duration,distance"
#     response = requests.get(url)
#     response.raise_for_status() # Raise an error for bad status codes
#     data = response.json()

#     if data.get("code") != "Ok":
#         print("Exiting due to OSRM error.")
#         exit()

#     durations = data.get("durations")
#     distances = data.get("distances")

#     print("\nDuration Matrix (in minutes):")
#     for row in durations:
#         print([round(x / 60, 1) if x is not None else None for x in row])

#     print("\nDistance Matrix (in km):")
#     for row in distances:
#         print([round(x / 1000, 2) if x is not None else None for x in row])
    
#     return distances

api_key = os.getenv("GEOAPIFY_API_KEY")

def get_distance_duration_matrix(coordinates):
    """Fetches distance matrix from Geoapify API."""
    url = f"https://api.geoapify.com/v1/routematrix?apiKey={api_key}"
    headers = {"Content-Type": "application/json"}

    # Construct the Geoapify payload
    sources = [{"location": [lon, lat]} for lat, lon in coordinates]  # Geoapify: [lon, lat]
    targets = [{"location": [lon, lat]} for lat, lon in coordinates]  # Geoapify: [lon, lat]
    payload = {
        "mode": "drive",
        "sources": sources,
        "targets": targets,
    }
    data = json.dumps(payload)

    try:
        resp = requests.post(url, headers=headers, data=data)
        resp.raise_for_status()
        matrix_data = resp.json()

        # Extract distance matrix.
        distances = []
        times = []
        if matrix_data and 'sources_to_targets' in matrix_data:
            #  Iterate through sources and targets to build the matrix
            for source_data in matrix_data['sources_to_targets']:
                row_distances = []
                row_times = []
                for target_data in source_data:
                    row_distances.append(target_data.get('distance', None))  # Get distance, None if missing
                    row_times.append(target_data.get('time', None))  # Get time, None if missing
                distances.append(row_distances)
                times.append(row_times)
        else:
            print("Error: 'sources_to_targets' key not found in Geoapify response.")
            return None

        return distances, times

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}, Response Text: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from Geoapify.")
        return None

# coordinates = [(40.7484421, -73.9856589), (40.7813974, -73.9733215), (40.7070653, -74.0111761), (40.7574044, -73.9902032)]
# distances, times = get_distance_matrix(coordinates)
# print(distances)
# print('---------')
# print(times)