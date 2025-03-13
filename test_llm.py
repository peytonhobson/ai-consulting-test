import streamlit as st
import asyncio
from openai import OpenAI
from src.utils.config import openai_client
from llm import handle_prompt
from llm.process_queries import get_thread_messages
from dotenv import load_dotenv
import os

load_dotenv()
assistant_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def main():
    st.title("Test Bot")

    # Initialize session state for thread_id if it doesn't exist
    if "thread_id" not in st.session_state:
        # Create a new thread when the app starts
        thread = assistant_client.beta.threads.create()
        st.session_state.thread_id = thread.id
        st.session_state.messages = []

    # Display existing messages from the thread
    if not st.session_state.messages:
        # If local state is empty, fetch messages from the thread
        thread_messages = get_thread_messages(st.session_state.thread_id)
        st.session_state.messages = thread_messages

    # Display all messages
    for message in st.session_state.messages:
        with st.chat_message(message["type"]):
            # Enable HTML rendering for messages
            st.markdown(message["content"], unsafe_allow_html=True)

    # Handle user input
    if prompt := st.chat_input("What questions do you have?"):
        # Display user message
        st.chat_message("user").markdown(prompt)

        # Add to session state
        st.session_state.messages.append({"type": "human", "content": prompt})

        # Generate and display AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                ai_response = await handle_prompt(st.session_state.thread_id, prompt)
                # Enable HTML rendering for AI response
                st.markdown(ai_response, unsafe_allow_html=True)

        # Append AI response to session state
        st.session_state.messages.append({"type": "ai", "content": ai_response})


if __name__ == "__main__":
    asyncio.run(main())
