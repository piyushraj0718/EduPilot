from llm import get_llm


def analyze_performance(quiz, quiz_result):
    wrong_questions = []

    for result in quiz_result["results"]:
        if not result["is_correct"]:
            wrong_questions.append({
                "question": result["question"],
                "correct_answer": result["correct_answer"],
                "explanation": result["explanation"]
            })

    if not wrong_questions:
        return {
            "weak_topics": [],
            "recommendation": (
                "Excellent work! You answered every "
                "question correctly. Try a harder quiz "
                "to challenge yourself."
            )
        }

    questions_text = "\n\n".join(
        f"Question: {item['question']}\n"
        f"Explanation: {item['explanation']}"
        for item in wrong_questions
    )

    llm = get_llm(temperature=0.2)

    prompt = f"""
You are EduPilot, an AI learning assistant.

Analyze the student's incorrect quiz answers.

Incorrect questions:

{questions_text}

Identify the main academic topics or concepts
where the student needs more practice.

Return your response in exactly this format:

Weak topics:
- topic 1
- topic 2
- topic 3

Recommendation:
Give a concise and practical study recommendation
based on these weak topics.

Rules:
1. Identify actual academic concepts, not the question text.
2. Keep the weak topics short and specific.
3. Only include topics supported by the incorrect questions.
4. Do not invent topics.
"""

    response = llm.invoke(prompt)

    return {
        "weak_topics": response.content,
        "recommendation": (
            "Review the weak topics above and take "
            "a focused quiz to strengthen your understanding."
        )
    }