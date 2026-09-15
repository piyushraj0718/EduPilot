from rag.generator import generate_answer


def answer_question(vector_store, question):
    results = vector_store.similarity_search(question, k=4)
    
    context = "\n\n".join(doc.page_content for doc in results)
    answer = generate_answer(question, context)
    
    sources = sorted(set(doc.metadata.get("page", 0) + 1 for doc in results))
    
    return {
        "answer": answer,
        "sources": sources
    }