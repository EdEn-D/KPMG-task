import streamlit as st
from dotenv import load_dotenv
import os
import shelve
import argparse
import sys
import os
from pathlib import Path
import logging
from client import generate_response


load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Argument parser to handle command-line arguments
parser = argparse.ArgumentParser(description="Streamlit Chatbot Interface")
# parser.add_argument('--clean', action='store_true', help="Delete chat history before startup")
parser.add_argument(
    "--title",
    type=str,
    default="Streamlit Chatbot Interface",
    help="Set the title of the app",
)
args = parser.parse_args()


# Use the title argument to set the title of the Streamlit app
st.title(args.title)

logger.info("Streamlit app has started")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# Initialize messages in session state if not present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Main chat interface
if prompt := st.chat_input("How can I help?"):
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()

        # Convert message history to formatted string
        message_string = ""
        for msg in st.session_state.messages:
            prefix = "User: " if msg["role"] == "user" else "Assistant: "
            message_string += f"{prefix}{msg['content']}\n"

        # Pass the formatted message string to generate_response
        full_response = generate_response(message_string)

        message_placeholder.markdown(full_response)

    # Add assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# streamlit run streamlit_chat_ui.py -- --clean
