from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, Runner, set_tracing_disabled
from route_optimization import solve_vrp
from utils import print_solution
from db_config import get_user_conversations
from inventory import retrieve_addresses_and_demands
import os

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment. Please check your .env file or hardcode temporarily.")

set_tracing_disabled(disabled=True)

provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
)

model = OpenAIChatCompletionsModel(
    model='gemini-2.0-flash',
    openai_client=provider,
)

# Global variable to store current user context
current_user_id = None

def set_current_user(user_id):
    """Set the current user context"""
    global current_user_id
    current_user_id = user_id

@function_tool
def get_recent_conversations_tool():
    """Retrieve recent conversations from the database."""
    global current_user_id
    if not current_user_id:
        return "No conversation history available - user not logged in"
    history_context = get_user_conversations(user_id=current_user_id)
    print("Retrieved conversation history:", history_context)
    return history_context

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

class VRPAssistant:
    def __init__(self, user_id=None):
        self.user_id = user_id
        set_current_user(user_id)  # Set the current user context
        self.assistant = self._create_assistant()

    def _create_assistant(self):
        return Agent(
            name="VRP Route Planner",
            instructions="""
            You are a supply chain expert. Given the user query, extract:
            - Number of vehicles
            - Vehicle capacity
            - Depot (optional, default: 0)
            Do NOT ask for delivery addresses or demands — they are retrieved automatically.
            Do NOT generate addresses on your own — they are retrieved automatically.
            You MUST check the past conversation context by calling get_recent_conversations_tool(), if your response is based on past conversations, mention it appropriately.
            Call solve_vrp_tool with these parameters and return the result as a JSON object containing routes, addresses, demands, and coordinates, with a plan_output and an explanation field.
            Example:
            {
              "routes": [[0, 1, 0], [0, 2, 0], [0, 3, 0]],
              "addresses": ["350 5th Ave, New York, NY 10118", ...],
              "demands": [0, 5, 5, 5],
              "coordinates": [[40.7484421, -73.9856589], ...],
              "plan_output": "...",
              "explanation": "...",
              "user_query": "...",
            }
            """,
            model=model,
            tools=[solve_vrp_tool, get_recent_conversations_tool],
        )

    def run(self, query):
        return Runner.run_sync(self.assistant, query)

# Example usage
if __name__ == "__main__":
    user_query = """
    Please optimize delivery routes with:
    - 3 vehicles available
    - Each vehicle can carry 5 items
    """
    
    assistant = VRPAssistant(user_id="test_user")
    result = assistant.run(user_query)
    print(result.final_output)