import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


def get_llm(temperature=0):

    model_name = os.getenv(
        "GROQ_MODEL_NAME"
    )

    api_key = os.getenv(
        "GROQ_API_KEY"
    )

    if not model_name:
        raise ValueError(
            "GROQ_MODEL_NAME is missing from .env"
        )

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing from .env"
        )

    return ChatGroq(
        model=model_name,
        groq_api_key=api_key,
        temperature=temperature
    )