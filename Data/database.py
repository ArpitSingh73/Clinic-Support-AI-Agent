import json
from typing import Union

def get_patient_by_name(patient_name: str) -> Union[str, None]:
    """Fetch patient data by name from a JSON file."""
    try:
        file_path = "Data/data.json"
        with open(file_path, "r") as file:
            data = json.load(file)
    
        for item in data:
            if item["name"].lower() == patient_name.lower():
                return item
        return None
    except Exception as e:
        print("Error reading patient data:", e)
        return None