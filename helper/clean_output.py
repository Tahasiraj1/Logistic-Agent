import json
import re

# Function to clean and verify the output from the route optimizer Agent
def clean_output(output):
    """Clean and verify the output from the route optimizer."""
    output_clean = output.strip()
    output_json_match = re.search(r"\{.*\}", output_clean, re.DOTALL)
    
    if not output_json_match:
        raise ValueError("No valid JSON object found in the output")
    
    output_dict = json.loads(output_json_match.group())
    
    if not isinstance(output_dict, dict):
        raise ValueError("Unexpected response format from the route optimizer")
    
    return output_dict