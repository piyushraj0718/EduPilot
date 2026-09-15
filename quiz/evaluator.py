def evaluate_quiz(quiz, user_answers):

    score = 0
    results = []

    for index, question in enumerate(quiz.questions):

        user_answer = user_answers[index]

        is_correct = (
            user_answer == question.correct_answer
        )

        if is_correct:
            score += 1

        results.append({
            "question": question.question,
            "user_answer": user_answer,
            "correct_answer": question.correct_answer,
            "is_correct": is_correct,
            "explanation": question.explanation
        })

    return {
        "score": score,
        "total": len(quiz.questions),
        "results": results
    }