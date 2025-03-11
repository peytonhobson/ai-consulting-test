import json
import streamlit as st
import asyncio
from datetime import datetime
from langchain.schema import HumanMessage
from utils import prompt_ai

async def main():
    st.title("Test Bot")

    # Initialize session state for messages if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = [
            HumanMessage(
                content=(
                    "You are an expert AI assistant designed to answer questions using the knowledge contained in the provided documents. "
                    "Base your answers on the document context, and if needed, indicate when you draw on general knowledge. "
                    f"The current date is: {datetime.now().date()}"
                )
            )
        ]

    # Display existing messages
    for message in st.session_state.messages:
        message_json = json.loads(message.model_dump_json())
        if message_json["type"] in ["human", "ai"]:
            with st.chat_message(message_json["type"]):
                # Enable HTML rendering for messages
                st.markdown(message_json["content"], unsafe_allow_html=True)

    # Handle user input
    if prompt := st.chat_input("What questions do you have?"):
        # Display user message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append(HumanMessage(content=prompt))

        # Generate and display AI response
        with st.chat_message("assistant"):
            ai_response = await prompt_ai(st.session_state.messages)
            # Enable HTML rendering for AI response
            st.markdown(ai_response.content, unsafe_allow_html=True)

        # Append AI response to session state
        st.session_state.messages.append(ai_response)

if __name__ == "__main__":
    asyncio.run(main())