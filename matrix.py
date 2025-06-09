import requests
import os
import json

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