import logging
import requests

logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:5051"


def generate_response(chat_history):
    logger.info(f"Inside generate_response. chat_history: {chat_history}")
    try:
        # Sending the user input to FastAPI and receiving AI response
        response = requests.post(
            f"{API_BASE_URL}/generate_response", params={"chat_history": chat_history}
        )
        logger.info(f"Response: {response}")
        if response.status_code == 200:
            return response.json().get("response", "No AI response")
        else:
            return f"Error: Failed to get AI response. Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return {"response": f"Error communicating with the server: {str(e)}"}

