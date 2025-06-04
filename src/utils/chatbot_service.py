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
OPENAI_MODEL = "gpt-4"

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
        f"You can see the full conversation history in this chat and should use it to answer follow-up questions. "
        f"The user is currently speaking in {'Dutch' if user_lang == 'nl' else 'English'}, so respond in that language. "
        f"Use the provided knowledge graph context for factual information when relevant, and clearly mark such content as [Graph]. "
        f"Begin each response by briefly explaining any key concepts or entities from the user's question, especially if they relate to the Ion Beam Machine. "
        f"Then, provide a complete answer that incorporates relevant information from the knowledge graph (if any). "
        f"If the answer cannot be grounded in the graph, rely on your general knowledge and mark those parts as [LLM]. "
        f"If the question is unrelated to the Ion Beam Machine or the graph content, answer based on [LLM] knowledge only."
    )

    # Add the system message up top
    messages = [{"role": "system", "content": system_msg}]

    # Inject the graph context *just before the latest user message*, not at the end
    *prior_messages, last_user = messages_history
    messages.extend(prior_messages)
    messages.append({"role": "system", "content": f"Graph context:\n{graph_context}"})
    messages.append(last_user)

   # Send to OpenAI
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages
    )

    return response.choices[0].message.content

