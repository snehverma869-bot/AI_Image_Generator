import streamlit as st
import google.generativeai as genai


# Configure Gemini using Streamlit Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Load Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")


def get_assistant_response(question: str, history=None, *args, **kwargs) -> str:
    if not question.strip():
        return "Please ask a question so I can help."

    # Convert history to Gemini-friendly format
    chat_history = []

    if history: 
        for msg in history:       
            role = "model" if msg["role"] == "assistant" else "user"
            chat_history.append({
                "role": role,
                "parts": [msg["content"]]
            })

    try:
        chat = model.start_chat(history=chat_history)
        response = chat.send_message(question)
        return response.text

    except Exception as e:
        return f"Error: {str(e)}"
