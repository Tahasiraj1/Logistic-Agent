# Global variable to store current user context
current_user_id = None

def set_current_user(user_id):
    """Set the current user context"""
    global current_user_id
    current_user_id = user_id