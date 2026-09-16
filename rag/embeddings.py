from langchain_core.embeddings import Embeddings
import os

import requests
from dotenv import load_dotenv

load_dotenv()


class JinaEmbeddings(Embeddings):
    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "jina-embeddings-v5-text-small",
    ):
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        self.model_name = model_name

        if not self.api_key:
            raise ValueError("JINA_API_KEY is not configured.")

    def _embed(self, texts: list[str], task: str) -> list[list[float]]:
        response = requests.post(
            "https://api.jina.ai/v1/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model_name,
                "input": texts,
                "task": task,
            },
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()["data"]
        return [item["embedding"] for item in data]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts, "retrieval.passage")

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], "retrieval.query")[0]


def get_embeddings():
    return JinaEmbeddings()
