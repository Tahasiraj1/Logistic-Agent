from agents import function_tool
from utils import print_solution
from inventory import retrieve_addresses_and_demands
from route_optimization import solve_vrp

@function_tool
def solve_vrp_tool(query: str, vehicle_capacity: int, num_vehicles: int, depot: int = 0):
    """Fetch the weather for a given location.

    Args:
        vehicle_capacity: integer representing max capacity per vehicle. (e.g. [0, 5, 5, 5])
        num_vehicles: integer number of available vehicles. (e.g. 3)
        depot: integer index of depot location (usually 0)
        query: natural language query from which vehicle capacity, num_vehicles, and depot are extracted.

    Returns:
        An object containing the solution routes, coordinates, addresses, and demands.
    """

    addresses_and_demands = retrieve_addresses_and_demands() 
        
    # Solve VRP with parsed parameters
    try:
        manager, routing, solution, routes, coordinates, addresses, demands = solve_vrp(
            addresses=[address for address, _ in addresses_and_demands],
            demands=[demand for _, demand in addresses_and_demands],
            vehicle_capacities=[vehicle_capacity] * num_vehicles,
            num_vehicles=num_vehicles,
            depot=depot
        )
        
        if not solution:
            return "No valid solution found. Please check your constraints."

        # Get nicely formatted plan_output
        plan_output = print_solution(manager, routing, solution, addresses)
    
        result = {
            "routes": routes,  # List of routes
            "coordinates": coordinates,  # List of (lat, lon) tuples
            "addresses": addresses,  # List of address strings
            "demands": demands,  # List of demands
            "plan_output": plan_output,  # 👈 nicely formatted VRP solution as a string
            "user_query": query,
        }
        
        return result
        
    except Exception as e:
        return f"Error solving VRP: {str(e)}"
