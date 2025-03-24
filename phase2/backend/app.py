from fastapi import FastAPI
import uvicorn
import logging
from .ai_processor import OpenAIProcessor
from dotenv import load_dotenv, find_dotenv
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

load_dotenv(find_dotenv())

class ChatbotApp:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.app = FastAPI()

        self.register_endpoints()

        self.processor = OpenAIProcessor()
        self.logger.info("ChatbotApp initialized")


    def register_endpoints(self):
        @self.app.get("/ping")
        async def ping():
            return {"message": "pong"}
        
        @self.app.post("/generate_response")
        async def generate_response(chat_history: str):
            self.logger.info(f"Received chat history: {chat_history}")
            extracted_fields = self.processor.extract_fields(chat_history)
            validation_fields = self.processor.validate_fields(extracted_fields)
            response = self.processor.generate_response(
                validation_fields, chat_history
            )
            return {"response": response}

    def run(self, **kwargs):
        uvicorn.run(self.app, **kwargs)