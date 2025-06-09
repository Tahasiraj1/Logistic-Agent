from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from address_to_coordinates import get_coordinates
from matrix import get_distance_duration_matrix
from inventory import retrieve_addresses_and_demands
from helper.optimize_by import get_optimize_by
import utils
import time


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

    distance_matrix, duration_matrix = get_distance_duration_matrix(coordinates)
    if distance_matrix is None:
        print("Exiting due to distance matrix failure.")
        return
    print('Distance Matrix: ', distance_matrix)
    print('Duration Matrix: ', duration_matrix)


    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, depot)

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[from_node][to_node])

    # Create and register duration callback
    def duration_callback(from_index, to_index):
        """Returns the duration between the two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(duration_matrix[from_node][to_node])


    distance_callback_index = routing.RegisterTransitCallback(distance_callback)
    duration_callback_index = routing.RegisterTransitCallback(duration_callback)

    # Define cost of each arc based on optimization preference
    if get_optimize_by() == 'Distance':
        routing.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)
    else:
        routing.SetArcCostEvaluatorOfAllVehicles(duration_callback_index)

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
    
    # Add Time Window constraint (using duration)
    routing.AddDimension(
        duration_callback_index,
        0,  # no slack
        86400,  # 24 hours max, adjust as needed
        False,  # don't force start to zero.
        "Time"
    )

    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 10

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)
    
    # Get routes
    routes = utils.get_routes(solution, routing, manager)

    return manager, routing, solution, routes, coordinates, addresses, demands

def solve_tsp():
    """Entry point of the program."""

    addresses_and_demands = retrieve_addresses_and_demands()
    addresses = [address for address, _ in addresses_and_demands]
    demands = [demand for _, demand in addresses_and_demands]

    # Convert addresses to coordinates
    coordinates = []
    for address in addresses:
        coord = get_coordinates(address)
        if coord:
            print(f"📍 {address} → {coord}")
            coordinates.append(coord)
        time.sleep(1)  # Respect rate limit

    print('Coordinates: ', coordinates)

    distance_matrix, duration_matrix = get_distance_duration_matrix(coordinates)
    if distance_matrix is None:
        print("Exiting due to distance matrix failure.")
        return
    print('Distance Matrix: ', distance_matrix)
    print('Duration Matrix: ', duration_matrix)

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, 0)
    
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        output = utils.print_solution(manager, routing, solution, addresses)

    # Get routes
    routes = utils.get_routes(solution, routing, manager)

    return output, routes, coordinates, addresses, demands

if __name__ == '__main__':
    output, routes, coordinates, addresses, demands = solve_tsp()
