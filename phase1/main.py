import logging
import os
import subprocess
import sys

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Set specific loggers to higher levels to reduce output
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Function to run the Streamlit app
def run_streamlit(title):
    try:
        filename = os.path.join(os.path.dirname(__file__), "streamlit_ui.py")
        command = ["streamlit", "run", filename, "--", "--title", title]
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../")
        )  # Set project root as PYTHONPATH

        subprocess.run(command, check=True, env=env)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error occurred while running command: {e}")


def run_app(title):
    # Start Streamlit app
    run_streamlit(title)


if __name__ == "__main__":
    app_title = "ביטוח לאומי Form Processor"
    run_app(app_title)
