#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import requests
import json
import base64
from urllib.parse import urlparse
from datetime import datetime

# Get the environment type from an environment variable
env_type = os.getenv('ENV', 'development')  # Default to 'development' if not set

# Assume the custom-named .env file is in the same directory as the script
base_dir = os.path.dirname(os.path.realpath(__file__))
dotenv_path = os.path.join(base_dir, f'.env.{env_type}')

# Load the environment variables from the specified .env file
load_dotenv(dotenv_path)

# Constants
EMAIL = os.getenv('JIRA_EMAIL')  # Your Jira account email
TOKEN = os.getenv('JIRA_TOKEN')  # Your Jira PAT
BASE_URL = os.getenv('JIRA_BASE_URL')  # Jira base URL, e.g., 'https://yourdomain.atlassian.net'

# Encode EMAIL and TOKEN for Basic Authentication
auth_string = f'{EMAIL}:{TOKEN}'
encoded_auth = base64.b64encode(auth_string.encode()).decode()  # Encode and convert bytes back to string


HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Basic {encoded_auth}"  # Use encoded auth string here
}


def make_request(url, method='get', data=None):
    """Handles making HTTP requests and error management."""
    try:
        if method == 'get':
            response = requests.get(url, headers=HEADERS)
        elif method == 'post':
            response = requests.post(url, headers=HEADERS, json=data)
        elif method == 'put':
            response = requests.put(url, headers=HEADERS, json=data)
        response.raise_for_status()  # This will raise an error for non-200 status codes
        return response.json() if response.content else None  # Extract JSON safely
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e.response.status_code} {e.response.reason}")
        if e.response.content:
            print("Error details:", e.response.json())
        return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def confirm_connection():
    url = f"{BASE_URL}/rest/agile/1.0/board"
    response = make_request(url)
    if response:
        print("Connection confirmed. User data received successfully.")
        print(response)

def get_issue(issue_id_or_key):
    """
    Retrieves a Jira issue by its ID or key.
    Args:
    issue_id_or_key (str): The ID or key of the issue (e.g., 'WM-48').
    Returns:
    dict or None: The issue data as a dictionary if successful, None otherwise.
    """
    url = f"{BASE_URL}/rest/agile/1.0/issue/{issue_id_or_key}"
    return make_request(url)

def update_issue(issue_id_or_key, update_data):
    """
    Updates a Jira issue by its ID or key with the provided update data.
    Args:
    issue_id_or_key (str): The ID or key of the issue (e.g., 'WM-48').
    update_data (dict): A dictionary containing the issue fields to be updated.
    Returns:
    dict or None: The updated issue data as a dictionary if successful, None otherwise.
    """
    url = f"{BASE_URL}/rest/api/2/issue/{issue_id_or_key}"
    return make_request(url, method='put', data=update_data)


# Main function and navigation omitted for brevity - can be adapted from your original script
def main():
    issue_id_or_key = 'WM-48'  # Replace 'WM-48' with the actual issue ID or key you want to update
    update_data = {
        "fields": {
            "description": "New description here",
            "labels": [
                "Ready"
            ]
        }
    }
    updated_issue = update_issue(issue_id_or_key, update_data)


if __name__ == "__main__":
    main()

