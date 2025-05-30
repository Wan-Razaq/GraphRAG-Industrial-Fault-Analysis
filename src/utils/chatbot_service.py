import os
from pathlib import Path
from dotenv import load_dotenv
from langdetect import detect
from openai import OpenAI


# Load environment variables from .env file
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# Read API key from environment
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)


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
        f"You are an assistant specialized in industrial maintenance and troubleshooting. "
        f"Your role is to generate accurate, natural-language recommendations for technicians working with manufacturing equipment, particularly the Ion Beam Machine. "
        f"The user is currently speaking in {'Dutch' if user_lang == 'nl' else 'English'}, so respond in that language. "
        f"Use the provided knowledge graph context for factual information when relevant, and clearly mark such content as [Graph]. "
        f"Begin each response by briefly explaining any key concepts or entities from the user's question, especially if they relate to the Ion Beam Machine. "
        f"Then, provide a complete answer that incorporates relevant information from the knowledge graph (if any). "
        f"If the answer cannot be grounded in the graph, rely on your general knowledge and mark those parts as [LLM]. "
        f"If the question is unrelated to the Ion Beam Machine or the graph content, answer based on [LLM] knowledge only."
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

