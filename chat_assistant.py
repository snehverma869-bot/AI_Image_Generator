import ollama

def get_assistant_response(question: str, history=None, *args, **kwargs) -> str:
    if not question.strip():
        return "Please ask a question so I can help."

    if history is None and args:
        history = args[0]
    if history is None and "history" in kwargs:
        history = kwargs["history"]

    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant. Give detailed, accurate and useful answers."
        }
    ]

    if history:
        messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    try:
        response = ollama.chat(
            model="llama3",
            messages=messages
        )

        return response["message"]["content"]

    except Exception as e:
        error_text = str(e)
        if "llama-server" in error_text.lower() or "server process" in error_text.lower():
            return (
                "Error: The Ollama/llama-server backend is not available. "
                "Please make sure llama-server is running and accessible, then try again."
            )
        return f"Error: {error_text}"