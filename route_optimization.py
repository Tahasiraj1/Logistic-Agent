from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from address_to_coordinates import get_coordinates
from distance_matrix import get_distance_matrix
import time


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
    print(plan_output)

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


def solve_vrp(addresses, demands, vehicle_capacities, num_vehicles, depot):
    """Solves the Vehicle Routing Problem (VRP) with capacity constraints."""

    # Convert addresses to coordinates
    coordinates = []
    for address in addresses:
        coord = get_coordinates(address)
        if coord:
            print(f"📍 {address} → {coord}")
            coordinates.append(coord)
        time.sleep(1)  # Respect rate limit

    print('Coordinates: ', coordinates)

    osrm_coords = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
    distance_matrix = get_distance_matrix(osrm_coords)
    if distance_matrix is None:
        print("Exiting due to distance matrix failure.")
        return

    # Convert distances from meters to integers (required by OR-Tools)
    distance_matrix = [[int(cell) for cell in row] for row in distance_matrix]
    print('Distance Matrix: ', distance_matrix)


    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot)

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[from_node][to_node])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Capacity constraint
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # no slack
        vehicle_capacities,  # vehicle maximum capacities
        True,  # start cumul to zero
        "Capacity")

    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 10

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console
    if solution:
        print_solution(manager, routing, solution, addresses)
    
    # Get and display routes
    routes = get_routes(solution, routing, manager)
    for i, route in enumerate(routes):
        print(f'Route {i}: {route}')

    return manager, solution, routes, coordinates, addresses, demands