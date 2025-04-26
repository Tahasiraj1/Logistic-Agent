from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, Runner
from route_optimization import solve_vrp
from inventory import retrieve_addresses
import google.generativeai as genai
from typing import Dict
import json
import os
import re

gemini_api_key = os.getenv("GEMINI_API_KEY")

provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
)

model = OpenAIChatCompletionsModel(
    model='gemini-2.0-flash',
    openai_client=provider,
)

def format_query(query: str) -> Dict:
    """
    Convert natural language query to structured format
    Returns a dictionary with VRP parameters
    """
    genai.configure(api_key=gemini_api_key)
    genai_model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
    Convert this delivery route optimization query to JSON format with these fields:
    - delivery_demands: list of integers representing demands at each location (first number should be 0 for depot)
    - vehicle_capacity: integer representing max capacity per vehicle
    - num_vehicles: integer number of available vehicles
    - depot: integer index of depot location (usually 0)

    User Query: {query}

    Response format:
    {{
        "delivery_demands": [0, 5, 5, 5],
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
        required_fields = ['delivery_demands', 'vehicle_capacity', 'num_vehicles', 'depot']
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Missing required field: {field}")
                
        return params
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return None

@function_tool
def solve_vrp_tool(query: str):
    """Process natural language query and solve the VRP."""
    # Parse the query
    params = format_query(query)
    if not params:
        return "Failed to parse query. Please try rephrasing."
    
    delivery_demands = params.get('delivery_demands', [])
    vehicle_capacity = params.get('vehicle_capacity', 0)
    num_vehicles = params.get('num_vehicles', 0)
    depot = params.get('depot', 0)

    required_fields = ['delivery_demands', 'vehicle_capacity', 'num_vehicles', 'depot']
    for field in required_fields:
        if field not in params:
            return f"Missing required field: {field}"
    
    print(delivery_demands, vehicle_capacity, num_vehicles, depot)
        
    # Get delivery addresses
    addresses = retrieve_addresses()
    if not addresses:
        return "No delivery addresses found in orders."
        
    # Solve VRP with parsed parameters
    try:
        manager, solution, routes, coordinates, addresses, demands = solve_vrp(
            addresses=addresses,
            demands=delivery_demands,
            vehicle_capacities=[vehicle_capacity] * num_vehicles,
            num_vehicles=num_vehicles,
            depot=depot
        )
        
        if not solution:
            return "No valid solution found. Please check your constraints."
            
        result = {
            "routes": routes,  # List of routes, each route is a list of node indices
            "coordinates": coordinates,  # List of (lat, lon) tuples
            "addresses": addresses,  # List of address strings
            "demands": demands,  # List of demand values
        }
        
        return result
        
    except Exception as e:
        return f"Error solving VRP: {str(e)}"

assistant = Agent(
    name="VRP Route Planner",
    instructions="""
    You are a supply chain expert. Given the user query, extract:
    - Number of vehicles
    - Vehicle capacity
    - Delivery demands
    - Depot (optional, default: 0)
    Do NOT ask for delivery addresses — they are retrieved automatically.
    Call solve_vrp_tool with these parameters and return the result as a JSON object containing routes, addresses, demands, and coordinates, with an explanation field.
    Example:
    {
      "routes": [[0, 1, 0], [0, 2, 0], [0, 3, 0]],
      "addresses": ["350 5th Ave, New York, NY 10118", ...],
      "demands": [0, 5, 5, 5],
      "coordinates": [[40.7484421, -73.9856589], ...],
      "explanation": "..."
    }
    """,
    model=model,
    tools=[solve_vrp_tool],
)

# # Example usage
if __name__ == "__main__":
    user_query = """
    Please optimize delivery routes with:
    - 3 vehicles available
    - Each vehicle can carry 5 items
    - Delivery demands are 5 each at 3 delivery address
    """
    
    result = Runner.run_sync(assistant, user_query)
    print(result.final_output)