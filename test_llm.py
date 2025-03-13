import streamlit as st
import asyncio
from src.llm import process_query


async def main():
    st.title("Test Bot")

    # Initialize session state for messages and response_id if they don't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "last_response_id" not in st.session_state:
        st.session_state.last_response_id = None

    # Display existing messages
    for message in st.session_state.messages:
        message_type = "user" if message["type"] == "human" else "assistant"
        with st.chat_message(message_type):
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
                # Process the query with the new API
                ai_response, new_response_id = await process_query(
                    st.session_state.last_response_id, prompt
                )

                # Update the last response ID for the next conversation turn
                if new_response_id:
                    st.session_state.last_response_id = new_response_id

                # Enable HTML rendering for AI response
                st.markdown(ai_response, unsafe_allow_html=True)

        # Append AI response to session state
        st.session_state.messages.append({"type": "ai", "content": ai_response})


if __name__ == "__main__":
    asyncio.run(main())
