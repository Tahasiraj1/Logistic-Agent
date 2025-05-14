import folium
import requests
import json
from utils import tile_providers, get_tile # Assuming these are correctly implemented
import click
import os

geoapify_api_key = os.getenv("GEOAPIFY_API_KEY")
if not geoapify_api_key:
    raise ValueError("GEOAPIFY_API_KEY not found in environment. Please check your .env file or hardcode temporarily.")

# --- New helper function to get detailed route geometry ---
def get_route_geometry(start_coords, end_coords):
    """
    Fetches detailed road geometry between two points using Geoapify Routing API.

    Args:
        start_coords (tuple): (latitude, longitude) of the start point.
        end_coords (tuple): (latitude, longitude) of the end point.
        geoapify_api_key (str): Your Geoapify API key.

    Returns:
        list: A list of (latitude, longitude) tuples representing the route path,
              or an empty list if the API call fails.
    """
    print(click.style(f"\nRequesting route from {start_coords} to {end_coords}", fg='green'))
    waypoints = f"{start_coords[0]},{start_coords[1]}|{end_coords[0]},{end_coords[1]}"
    api_url = f"https://api.geoapify.com/v1/routing?waypoints={waypoints}&mode=drive&apiKey={geoapify_api_key}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        route_geometry = []
        
        if 'features' in data and data['features']:
            for feature in data['features']:
                geometry = feature.get('geometry')
                if geometry and geometry.get('type') == 'MultiLineString':
                    coordinates_list = geometry.get('coordinates', [])
                    for line in coordinates_list:
                        for lon, lat in line:
                            route_geometry.append((lat, lon))  # Folium expects (lat, lon)
                    return route_geometry
                else:
                    print("Warning: Unsupported geometry type or missing geometry.")
        else:
            print(click.style("Warning: No route features found in response. Raw response:", fg='red'))
            print(json.dumps(data, indent=2)) # Print the JSON for inspection
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error fetching route geometry from Geoapify: {e}")
        if response is not None:
            print(f"Raw response content (RequestException): {response.text}")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON response from Geoapify.")
        if response is not None:
            print(f"Raw response content (JSONDecodeError): {response.text}")
        return []
    except Exception as e: # Catch any other potential errors
        print(f"An unexpected error occurred: {e}")
        if response is not None:
            print(f"Raw response content (Unexpected Error): {response.text}")
        return []

def create_map(coordinates, addresses, routes, demands):
    style = get_tile()
    tile_info = tile_providers.get(style, tile_providers["OpenStreetMap"])

    avg_lat = sum(lat for lat, _ in coordinates) / len(coordinates)
    avg_lon = sum(lon for _, lon in coordinates) / len(coordinates)
    m = folium.Map(location=[avg_lat, avg_lon], tiles=tile_info["tiles"], attr=tile_info["attr"], zoom_start=12)

    for i, (lat, lon) in enumerate(coordinates):
        popup_text = f"{addresses[i]}<br>Demand: {demands[i]}"
        folium.Marker(
            [lat, lon],
            popup=popup_text,
            icon=folium.Icon(color="green" if i == 0 else "blue")
        ).add_to(m)

    colors = ["red", "blue", "green", "purple", "orange", "yellow", "brown", "black", "gray", "pink", "cyan", "magenta"]
    for vehicle_id, route_indices in enumerate(routes): # routes now contain indices from OR-Tools
        # Skip empty routes or routes with only depot-depot
        if len(route_indices) <= 2 and route_indices[0] == route_indices[-1] == 0:
            continue

        full_route_path = []
        for i in range(len(route_indices) - 1):
            start_node_idx = route_indices[i]
            end_node_idx = route_indices[i+1]

            start_coords = coordinates[start_node_idx]
            end_coords = coordinates[end_node_idx]

            # Get detailed geometry for this segment
            segment_geometry = get_route_geometry(start_coords, end_coords)
            if segment_geometry:
                full_route_path.extend(segment_geometry)
            else:
                # Fallback: if API call fails, draw a straight line for this segment
                print(f"Warning: Failed to get road geometry for segment from {addresses[start_node_idx]} to {addresses[end_node_idx]}. Drawing straight line.\n")
                full_route_path.append(start_coords)
                if start_coords != end_coords: # Avoid adding duplicate points for same location
                    full_route_path.append(end_coords)

        # Add the polyline for the entire vehicle route
        if full_route_path:
            folium.PolyLine(
                full_route_path,
                color=colors[vehicle_id % len(colors)],
                weight=5,
                opacity=0.7,
                popup=f"Vehicle {vehicle_id}"
            ).add_to(m)
        else:
            print(f"No path drawn for vehicle {vehicle_id} due to missing geometry.")

    return m


if __name__ == "__main__":
    # Example usage
    m = create_map([(40.7484421, -73.9856589), (40.7540576, -73.9822573)], ["50 5th Ave, New York, NY 10118", "W 42nd St, New York, NY 10036"], [[0, 1, 0]], [0, 5], "fb3737b657e3472e8f7607a383def134")
    m.save("test_map.html")