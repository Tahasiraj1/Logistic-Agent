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


# Global configuration variables
optimize_by = "Distance"  # Default value

def set_optimize_by(value: str):
    """Set the optimization preference"""
    global optimize_by
    optimize_by = value

def get_optimize_by() -> str:
    """Get the current optimization preference"""
    return optimize_by