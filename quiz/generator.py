from pydantic import BaseModel, Field

from llm import get_llm


class QuizQuestion(BaseModel):
    question: str

    options: list[str] = Field(
        min_length=4,
        max_length=4
    )

    correct_answer: int = Field(
        ge=0,
        le=3
    )

    explanation: str


class Quiz(BaseModel):
    questions: list[QuizQuestion]


def get_quiz_llm():
    return get_llm(
        temperature=0.3
    )


def generate_quiz(
    vector_store,
    number_of_questions=5,
    difficulty="Medium",
    topic="Entire Document"
):
    # Retrieve study material
    if topic == "Entire Document":

        search_query = (
            "important concepts, definitions, "
            "key ideas, principles and topics "
            "from this document"
        )

    else:

        search_query = (
            f"{topic}: important concepts, "
            f"definitions, key ideas, principles "
            f"and examples"
        )


    results = vector_store.similarity_search(
        search_query,
        k=12
    )


    context = "\n\n".join(
        doc.page_content
        for doc in results
    )


    llm = get_quiz_llm()


    prompt = f"""
You are EduPilot, an AI study assistant.

Create a multiple-choice quiz using ONLY
the provided study material.

Study material:

{context}

Quiz topic:
{topic}

Generate exactly {number_of_questions} questions.

Difficulty:
{difficulty}

Requirements:

- Every question must be related to the selected topic.
- If the selected topic is "Entire Document",
  questions may cover different topics from
  the provided study material.
- Each question must have exactly 4 options.
- Only one option must be correct.
- correct_answer must be the zero-based index
  of the correct option.
- Provide a short explanation for the correct answer.
- Questions should test understanding of the material.
- Avoid duplicate questions.
- Do not invent facts.
- Do not use information outside the study material.

Return ONLY valid JSON.

The JSON must follow this structure:

{{
  "questions": [
    {{
      "question": "string",
      "options": [
        "string",
        "string",
        "string",
        "string"
      ],
      "correct_answer": 0,
      "explanation": "string"
    }}
  ]
}}

Do not use markdown.
Do not use ```json.
Do not include any text outside the JSON.
"""


    response = llm.invoke(prompt)

    return Quiz.model_validate_json(
        response.content
    )