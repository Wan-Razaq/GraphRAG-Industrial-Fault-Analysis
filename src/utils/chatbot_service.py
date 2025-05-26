from openai import OpenAI
from langdetect import detect
from dotenv import load_dotenv
import os
import openai

client = OpenAI()

# Load environment variables from .env file
load_dotenv()

# Read API key from environment
openai_api_key = os.getenv("OPENAI_API_KEY")

# Assign to OpenAI library
openai.api_key = openai_api_key

# Choose the model
OPENAI_MODEL = "gpt-3.5-turbo"

from langdetect import detect

def detect_language(text: str) -> str:
    try:
        lang_code = detect(text)
    except Exception:
        lang_code = "en"
    return "nl" if lang_code.startswith("nl") else "en"

def generate_answer(messages_history: str, graph_context: str, user_lang: str) -> str:

    #prompt for retriever behaviour and language (tuple)
    system_msg = (
        f"You are an industrial maintenance assistant chatbot. "
        f"The user is currently speaking in {'Dutch' if user_lang == 'nl' else 'English'}, so respond in that language. "
        f"Use the provided graph context for factual information when relevant and mark such content explicitly as [Graph]. "
        f"For answers not found in the graph, rely on your general knowledge and mark them as [LLM]. "
        f"If the user's question is unrelated to the graph context, respond only with [LLM] knowledge."
    )

    # Build up message history
    messages = [{"role": "system", "content": system_msg}]
    messages += messages_history

    # Add a combined message with both the current question and the graph context
    last_user_msg = messages_history[-1]["content"] if messages_history else ""
    messages.append({
        "role": "user",
        "content": (
            f"Here is the graph context:\n{graph_context}\n\n"
            f"And here is the user's current question:\n{last_user_msg}\n\n"
            "Please answer clearly, mark with [Graph] or [LLM], and follow the correct language."
        )
    })

   # Send to OpenAI
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages
    )

    return response.choices[0].message.content

