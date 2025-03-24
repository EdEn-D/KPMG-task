from backend.app import ChatbotApp
import logging
import threading
import os
import subprocess
import sys

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Set specific loggers to higher levels to reduce output
logging.getLogger('httpx').setLevel(logging.WARNING)  # Only show WARNING or higher for httpx
logging.getLogger('httpcore').setLevel(logging.WARNING)  # In case httpcore is also logging
logging.getLogger('urllib3').setLevel(logging.WARNING)  # In case urllib3 is also logging

logger = logging.getLogger(__name__)

# Function to run the FastAPI app
def run_server(app):
    logger.info("FastAPI app started")
    app.run(port=5051, host="0.0.0.0")

# Function to run the Streamlit app to avoid running from the command line
def run_streamlit(title):
    try:
        filename = os.path.join(os.path.dirname(__file__), "frontend", "chat_ui.py")
        # filename = os.path.join(os.path.dirname(__file__), "chat_ui.py")
        command = ["streamlit", "run", filename, "--", "--title", title]
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../")
        )  # Set project root as PYTHONPATH

        subprocess.run(command, check=True, env=env)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error occurred while running command: {e}")


def run_app(app, title="Bot name"):
    # Start FastAPI app in a separate thread
    fastapi_thread = threading.Thread(target=run_server, args=(app,))
    fastapi_thread.daemon = True  # This makes the FastAPI thread exit when the main program exits
    fastapi_thread.start()

    # Start Streamlit app
    run_streamlit(title)

if __name__ == "__main__":
    app = ChatbotApp()
    chat_title = "HMO Chatbot"
    run_app(app, chat_title)