import os

from dotenv import load_dotenv

from agent.graph import create_graph
from rag.embeddings import get_embeddings
from rag.vector_store import load_vector_store


load_dotenv()


VECTORSTORE_PATH = (
    "vectorstore/"
    "fbf5ea8b57ef818f53186c87ac74d3ad108eb0bcae897e80e8e806f37887ec99"
)


embeddings = get_embeddings()

vector_store = load_vector_store(
    embeddings,
    VECTORSTORE_PATH
)

graph = create_graph(vector_store)


questions = [
    "What is linear regression?"
]


for question in questions:

    result = graph.invoke({
        "question": question,
        "tool": "",
        "result": "",
        "answer": ""
    })

    print("\nQuestion:", question)
    print("Selected tool:", result["tool"])
    print("Answer:", result["answer"])