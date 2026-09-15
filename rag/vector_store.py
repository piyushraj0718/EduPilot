import os
from langchain_community.vectorstores import FAISS


def create_vector_store(chunks, embeddings):
    return FAISS.from_documents(chunks, embeddings)


def save_vector_store(vector_store, path):
    os.makedirs(path, exist_ok=True)
    vector_store.save_local(path)


def load_vector_store(embeddings, path):
    return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)