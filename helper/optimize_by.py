# Global configuration variables for the VRP
optimize_by = "Distance"  # Default value

# Functions to set and get the optimization preference for the VRP
def set_optimize_by(value: str):
    """Set the optimization preference"""
    global optimize_by
    optimize_by = value

# Function to get the optimization preference
def get_optimize_by() -> str:
    """Get the current optimization preference"""
    return optimize_by
