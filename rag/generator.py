from llm import get_llm


def generate_answer(question, context):
    llm = get_llm(temperature=0.2)
    
    prompt = f"""
You are EduPilot, an AI study assistant.

Answer the student's question using ONLY
the provided study material.

Study material:

{context}

Student question:

{question}

Instructions:

- Give a clear and student-friendly answer.
- Use simple Markdown.
- Do not use HTML tags.
- Do not use complex Markdown tables.
- Do not invent information.
- If the answer is not present in the material,
  say that the document does not provide enough
  information.

Return only the answer.
"""
    
    response = llm.invoke(prompt)
    return response.content