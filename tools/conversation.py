from agents import function_tool
from db_config import get_user_conversations
from helper.set_user import current_user_id

@function_tool
def get_recent_conversations_tool():
    """Retrieve recent conversations from the database."""
    global current_user_id
    if not current_user_id:
        return "No conversation history available - user not logged in"
    history_context = get_user_conversations(user_id=current_user_id)
    print("Retrieved conversation history:", history_context)
    return history_context