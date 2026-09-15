import numexpr

from langchain_community.tools import DuckDuckGoSearchRun


def search_pdf(vector_store, query, k=4):
    """
    Search the uploaded PDF for information
    relevant to the user's query.
    """

    results = vector_store.similarity_search(
        query,
        k=k
    )

    sources = sorted(
        set(
            doc.metadata.get("page", 0) + 1
            for doc in results
        )
    )

    context = "\n\n".join(
        doc.page_content
        for doc in results
    )

    return {
        "context": context,
        "sources": sources
    }


def calculate(expression):
    """
    Safely evaluate a mathematical expression.
    """

    try:

        result = numexpr.evaluate(
            expression
        )

        return str(result)

    except Exception:

        return "Unable to calculate the expression."


def web_search(query):
    """
    Search the web for information that may not
    be available in the uploaded PDF.
    """

    search = DuckDuckGoSearchRun()

    try:

        return search.run(query)

    except Exception:

        return "Unable to perform web search."