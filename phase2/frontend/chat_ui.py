import streamlit as st
from dotenv import load_dotenv
import os
import shelve
import argparse
import sys
import os
from pathlib import Path
import logging
from client import generate_response #, delete_history

def send_input(prompt):
    # Placeholder for the function that sends input to the chatbot and gets a response
    # This should be replaced with the actual implementation
    return "This is a placeholder response."

def delete_history():
    # Placeholder for the function that deletes chat history from the server
    # This should be replaced with the actual implementation
    pass

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Argument parser to handle command-line arguments
parser = argparse.ArgumentParser(description="Streamlit Chatbot Interface")
# parser.add_argument('--clean', action='store_true', help="Delete chat history before startup")
parser.add_argument('--title', type=str, default="Streamlit Chatbot Interface", help="Set the title of the app")
args = parser.parse_args()


# Use the title argument to set the title of the Streamlit app
st.title(args.title)

logger.info("Streamlit app has started")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# # TODO: ###########################################
# # TODO: Remove load and save chat history functions
# # Load chat history from shelve file
# def load_chat_history():
#     dir_path = "view/.streamlit"
    
#     # Create the directory if it doesn't exist
#     if not os.path.exists(dir_path):
#         os.makedirs(dir_path)
    
#     with shelve.open(f"{dir_path}/chat_history") as db:
#         return db.get("messages", [])


# # Save chat history to shelve file
# def save_chat_history(messages):
#     with shelve.open("view/.streamlit/chat_history") as db:
#         db["messages"] = messages


# # Initialize or load chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = load_chat_history()

# def delete_chat_history():
#     # delete history locally (streamlit)
#     st.session_state.messages = []
#     save_chat_history([])
#     # delete history from the server (agent)
#     delete_history() 

# # # Clean history before loading if --clean argument is passed
# # if args.clean and "clean" not in st.session_state:
# #     st.session_state.clean = True 
# #     delete_chat_history()

# # Sidebar with a button to delete chat history
# with st.sidebar:
#     if st.button("Delete Chat History"):
#         delete_chat_history()
# # TODO: Remove load and save chat history functions
# # TODO: ###########################################

# Display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])



# Main chat interface
if prompt := st.chat_input("How can I help?"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        full_response = generate_response(prompt)


        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Save chat history after each interaction
save_chat_history(st.session_state.messages)

# streamlit run streamlit_chat_ui.py -- --clean