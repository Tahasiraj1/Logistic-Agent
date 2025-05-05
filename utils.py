import google.generativeai as genai
from typing import Dict
import json
import re
import streamlit as st

gemini_api_key = st.secrets["api_keys"]["GEMINI_API_KEY"]
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment. Please check your .env file or hardcode temporarily.")

# Function for printing the solution of the VRP
def print_solution(manager, routing, solution, addresses):
    """Prints the solution routes for all vehicles with addresses and distances."""
    total_distance = 0
    plan_output = "\n🚗 Optimized Routes:\n"
    
    for vehicle_id in range(routing.vehicles()):
        index = routing.Start(vehicle_id)
        route_distance = 0
        route_output = f"\nRoute for vehicle {vehicle_id}:\n"
        step = 1
        
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_output += f"{step}. {addresses[node_index]}\n"
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            step += 1
            
        node_index = manager.IndexToNode(index)
        route_output += f"{step}. {addresses[node_index]} (Return to Start)\n"
        route_distance_km = round(route_distance / 1000, 2)
        route_output += f"Distance of route: {route_distance_km} km\n"
        plan_output += route_output
        total_distance += route_distance
        
    plan_output += f"\n📏 Total Distance of all routes: {round(total_distance / 1000, 2)} km\n"
    return plan_output

# Function to get routes from the solution
def get_routes(solution, routing, manager):
    """Get vehicle routes from a solution and store them in an array."""
    routes = []
    for route_nbr in range(routing.vehicles()):
        index = routing.Start(route_nbr)
        route = [manager.IndexToNode(index)]
        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))
        routes.append(route)
    return routes

# Function to format the user query
def format_query(query: str) -> Dict:
    """
    Convert natural language query to structured format
    Returns a dictionary with VRP parameters
    """
    genai.configure(api_key=gemini_api_key)
    genai_model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
    Convert this delivery route optimization query to JSON format with these fields:
    - vehicle_capacity: integer representing max capacity per vehicle
    - num_vehicles: integer number of available vehicles
    - depot: integer index of depot location (usually 0)

    User Query: {query}

    Response format:
    {{
        "vehicle_capacity": 5,
        "num_vehicles": 3,
        "depot": 0
    }}
    """

    try:
        response = genai_model.generate_content(prompt)
        raw_response = response.text.strip()
        
        # Extract JSON using regex
        match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if not match:
            raise ValueError(f"Failed to extract JSON from response: {raw_response}")
            
        json_text = match.group(0)
        params = json.loads(json_text)
        
        # Validate required fields
        required_fields = ['vehicle_capacity', 'num_vehicles', 'depot']
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field}")

        vehicle_capacity = params.get('vehicle_capacity', 0)
        num_vehicles = params.get('num_vehicles', 0)
        depot = params.get('depot', 0)

        return vehicle_capacity, num_vehicles, depot
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return None
    
# Global configuration variables for the VRP
optimize_by = "Distance"  # Default value

# Functions to set and get the optimization preference for the VRP
def set_optimize_by(value: str):
    """Set the optimization preference"""
    global optimize_by
    optimize_by = value

# Function to get the optimization preference
def get_optimize_by() -> str:
    """Get the current optimization preference"""
    return optimize_by

# Function to clean and verify the output from the route optimizer Agent
def clean_output(output):
    """Clean and verify the output from the route optimizer."""
    output_clean = output.strip()
    output_json_match = re.search(r"\{.*\}", output_clean, re.DOTALL)
    
    if not output_json_match:
        raise ValueError("No valid JSON object found in the output")
    
    output_dict = json.loads(output_json_match.group())
    
    if not isinstance(output_dict, dict):
        raise ValueError("Unexpected response format from the route optimizer")
    
    return output_dict

tile = 'OpenStreetMap'

def set_tile(style: str):
    global tile
    tile = style

def get_tile():
    return tile

tile_providers = {
    "OpenStreetMap": {
        "tiles": "OpenStreetMap",
        "attr": None
    },
    "CartoDB Positron": {
        "tiles": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        "attr": "© OpenStreetMap contributors, © CartoDB"
    },
    "CartoDB Dark Matter": {
        "tiles": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        "attr": "© OpenStreetMap contributors, © CartoDB"
    },
    "Thunderforest SpinalMap": {
        "tiles": 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        "attr": 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    },
    'Esri.NatGeoWorldMap': {
        'tiles': 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}', 
	    'attr': 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC',
    },
    'MtbMap': {
        'tiles': 'http://tile.mtbmap.cz/mtbmap_tiles/{z}/{x}/{y}.png',
        'attr': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &amp; USGS'
    }
}
