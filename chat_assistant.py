import streamlit as st
from google import genai

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def get_assistant_response(question: str, history=None, *args, **kwargs):
    if not question.strip():
        return "Please ask a question."

    conversation = ""

    if history:
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            conversation += f"{role}: {msg['content']}\n"

    conversation += f"User: {question}"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=conversation
        )

        return response.text

    except Exception as e:
        return f"Error: {e}"
