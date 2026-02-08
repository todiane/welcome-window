import requests
import html


def get_trivia_questions(amount=10, category=None, difficulty=None):
    """
    Fetch trivia questions from Open Trivia Database
    Categories: 9=General, 11=Film, 12=Music, 17=Science, 18=Computers,
                21=Sports, 22=Geography, 23=History
    Difficulty: easy, medium, hard
    """
    url = "https://opentdb.com/api.php"
    params = {"amount": amount}

    if category:
        params["category"] = category
    if difficulty:
        params["difficulty"] = difficulty

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data.get("response_code") == 0:
            # Decode HTML entities in questions and answers
            questions = []
            for q in data.get("results", []):
                questions.append(
                    {
                        "question": html.unescape(q["question"]),
                        "correct_answer": html.unescape(q["correct_answer"]),
                        "incorrect_answers": [
                            html.unescape(ans) for ans in q["incorrect_answers"]
                        ],
                        "category": html.unescape(q["category"]),
                        "difficulty": q["difficulty"],
                        "type": q["type"],
                    }
                )
            return questions
        return []
    except Exception as e:
        print(f"Error fetching trivia: {e}")
        return []
