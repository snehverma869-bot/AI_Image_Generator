import ollama

def get_assistant_response(question: str) -> str:
    if not question.strip():
        return "Please ask a question."

    system_prompt = """
You are ChatGPT-like AI Assistant.

Rules:
- Always answer in detail.
- Never give one-line answers.
- Explain everything step by step.
- Use headings and bullet points whenever appropriate.
- If asked to write a story, write at least 700 words.
- If asked to explain a topic, explain with examples.
- Do not repeat the user's prompt.
"""

    try:
        response = ollama.chat(
            model="llama3",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            options={
                "temperature": 0.8,
                "num_predict": 1024,
                "top_p": 0.9
            }
        )

        return response["message"]["content"]

    except Exception as e:
        return str(e)