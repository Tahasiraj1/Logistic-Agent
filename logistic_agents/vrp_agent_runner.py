from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from tools.conversation import get_recent_conversations_tool
from tools.solve_vrp import solve_vrp_tool
from helper.set_user import set_current_user
from .instructions import VRP_INSTRUCTIONS

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

class VRPAssistant:
    def __init__(self, user_id=None):
        self.user_id = user_id
        set_current_user(user_id)  # Set the current user context
        self.assistant = self._create_assistant()

    def _create_assistant(self):
        return Agent(
            name="VRP Route Planner",
            instructions=VRP_INSTRUCTIONS,
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