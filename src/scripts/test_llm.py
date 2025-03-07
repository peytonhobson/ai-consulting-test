import json
from datetime import datetime
import streamlit as st
from langchain.schema import HumanMessage, AIMessage

def main():
    st.title("Test Bot")
    if "messages" not in st.session_state:
        st.session_state.messages = [HumanMessage(content=(
            "You are an expert AI assistant designed to answer questions using the knowledge contained in the provided documents. "
            "Base your answers on the document context, and if needed, indicate when you draw on general knowledge. "
            f"The current date is: {datetime.now().date()}"
        ))]
    
    for message in st.session_state.messages:
        message_json = json.loads(message.json())
        if message_json["type"] in ["human", "ai"]:
            with st.chat_message(message_json["type"]):
                st.markdown(message_json["content"])
    
    if prompt := st.chat_input("What questions do you have?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("assistant"):
            ai_response = prompt_ai(st.session_state.messages)
            st.markdown(ai_response.content)
        st.session_state.messages.append(ai_response)

if __name__ == "__main__":
    main()