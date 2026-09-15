import numexpr
from langchain_community.tools import DuckDuckGoSearchRun


def search_pdf(vector_store, query, k=4):
    results = vector_store.similarity_search(query, k=k)
    
    sources = sorted(set(doc.metadata.get("page", 0) + 1 for doc in results))
    context = "\n\n".join(doc.page_content for doc in results)
    
    return {"context": context, "sources": sources}


def calculate(expression):
    try:
        result = numexpr.evaluate(expression)
        return str(result)
    except Exception:
        return "Unable to calculate the expression."


def web_search(query):
    search = DuckDuckGoSearchRun()
    try:
        return search.run(query)
    except Exception:
        return "Unable to perform web search."