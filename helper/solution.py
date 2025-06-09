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
