import json
import re
import os

gemini_api_key = os.getenv("GEMINI_API_KEY")
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