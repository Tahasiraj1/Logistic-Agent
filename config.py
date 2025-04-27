# Global configuration variables
optimize_by = "Distance"  # Default value

def set_optimize_by(value: str):
    """Set the optimization preference"""
    global optimize_by
    optimize_by = value

def get_optimize_by() -> str:
    """Get the current optimization preference"""
    return optimize_by