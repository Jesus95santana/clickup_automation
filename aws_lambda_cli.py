import json
import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Get environment variables from AWS Lambda Configuration
BASE_URL = os.getenv('BASE_URL', "https://api.clickup.com/api/v2")  # Default if not set
TOKEN = os.getenv('TOKEN')  # ClickUp API Token

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": TOKEN
}

def lambda_handler(event, context):
    """ AWS Lambda handler function for updating ClickUp task description based on JIRA label. """
    try:
        logger.info("Received JIRA event:")
        logger.info(json.dumps(event, indent=2))  # Log the entire JIRA webhook event

        # Hardcoded task ID for ClickUp
        task_id = '86dw30c2d'

        # Extract labels from JIRA webhook event
        labels = event.get("issue", {}).get("fields", {}).get("labels", [])

        logger.info(f"Extracted labels: {labels}")

        # Check if "Due" or "Ready" exists in the labels
        if "Due" in labels:
            new_description = "Due"
        elif "Ready" in labels:
            new_description = "Ready"
        else:
            logger.warning("No matching label found in JIRA issue. Skipping ClickUp update.")
            return {
                'statusCode': 200,
                'body': json.dumps({"message": "No relevant label found, no update made."})
            }

        logger.info(f"Updating ClickUp task {task_id} with description: {new_description}")

        # Call function to update description in ClickUp
        result = update_task_description(task_id, new_description)

        logger.info(f"ClickUp update result: {result}")

        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        logger.exception("An error occurred during lambda execution.")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }

def update_task_description(task_id, new_description):
    """ Updates the description of a ClickUp task. """
    url = f"{BASE_URL}/task/{task_id}"
    payload = {"description": new_description}

    try:
        response = requests.put(url, headers=HEADERS, json=payload)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)

        return {
            "status": "success",
            "message": "Task description updated successfully.",
            "data": response.json()
        }
    except requests.HTTPError as e:
        logger.error(f"HTTP error during task update: {e.response.status_code} {e.response.reason}")
        return {
            "status": "error",
            "message": f"HTTP error: {e.response.status_code} {e.response.reason}",
            "details": e.response.text
        }
    except requests.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}"
        }
