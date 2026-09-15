from llm import get_llm


def extract_topics(documents):
    # Use representative content from the document
    # instead of sending the entire PDF to the LLM.
    selected_documents = documents[:20]

    text = "\n\n".join(
        document.page_content
        for document in selected_documents
    )

    # Keep the request comfortably below the model limit.
    text = text[:18000]

    llm = get_llm(temperature=0)

    prompt = f"""
You are EduPilot, an AI study assistant.

Identify the main academic topics covered in this
educational document.

Document:
{text}

Return ONLY a numbered list.

Rules:
1. Identify 5 to 15 meaningful academic topics.
2. Prefer specific concepts such as:
   Linear Regression, Decision Trees, Gradient Descent.
3. Do not include generic topics like Introduction
   or Conclusion.
4. Do not include page numbers.
5. Do not explain the topics.
6. Avoid duplicate topics.

Example:

1. Linear Regression
2. Logistic Regression
3. Decision Trees
4. Random Forest
5. Support Vector Machines
"""

    response = llm.invoke(prompt)

    topics = []

    for line in response.content.splitlines():
        line = line.strip()

        if not line:
            continue

        if "." in line:
            line = line.split(".", 1)[1].strip()

        elif ")" in line:
            line = line.split(")", 1)[1].strip()

        if line:
            topics.append(line)

    return topics[:15]