import folium
import utils

def create_map(coordinates, addresses, routes, demands):
    style = utils.get_tile()
    tile_info = utils.tile_providers.get(style, utils.tile_providers["OpenStreetMap"])

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

    colors = ["red", "blue", "green", "purple", "orange"]
    for vehicle_id, route in enumerate(routes):
        if len(route) <= 2 and route[0] == route[-1] == 0:
            continue
        route_coords = [coordinates[node] for node in route]
        folium.PolyLine(
            route_coords,
            color=colors[vehicle_id % len(colors)],
            weight=5,
            opacity=0.7,
            popup=f"Vehicle {vehicle_id}"
        ).add_to(m)

    return m