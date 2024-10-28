import requests
import json
from config import TOGETHER_API_KEY, TOGETHER_API_URL

def get_llama_response(prompt):
    """
    Sends a prompt to the Together AI LLaMA model and retrieves the response.

    Parameters:
    - prompt (str): The user's prompt or question for the model.

    Returns:
    - str: The model's response or an error message if the request fails.
    """
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "max_tokens": 100,
        "temperature": 0.7
    }

    try:
        # Make the request to Together API
        response = requests.post(TOGETHER_API_URL, headers=headers, json=payload)
        print(f"Response Status Code: {response.status_code}")  # Debug: Print status code
        print(f"Response Text: {response.text}")  # Debug: Print raw response text
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        
        # Check for expected response format
        if "choices" in data and data["choices"]:
            return data["choices"][0].get("text", "No text in response").strip()
        else:
            return "Unexpected response format: " + json.dumps(data)
    
    except requests.RequestException as e:
        return f"Error retrieving response: {str(e)}"
